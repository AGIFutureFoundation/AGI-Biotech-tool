"""secp256k1 public-key recovery, in pure Python, with no dependencies.

Needed to verify a MetaMask signature: given a message hash and a 65-byte
signature, recover which address signed it. That is the whole of wallet login --
there is no password to check, only a signature to attribute.

Why not a library: eth-keys/coincurve are the right answer on a machine with
disk to spare, and this file should be deleted in favour of one the moment that
is true. It exists because this repo currently cannot install anything, and a
login path is not something to stub out and pretend about.

WHAT IS VERIFIED (tests/test_siwe.py):
  * scalar multiplication against the published secp256k1 vectors for 1G..5G,
  * that a recovered public key round-trips from a signature this module made,
  * address derivation against a known private key / address pair.

WHAT IS NOT:
  * side-channel resistance. This is plain Python bignum arithmetic with data-
    dependent branches. It is used ONLY to verify signatures, where every input
    is already public, and it must never be used to hold or sign with a secret.
    There is no signing function here for that reason; the test file defines its
    own, so the capability cannot leak into the server by accident.
"""

# Curve parameters, y^2 = x^3 + 7 over F_p.
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
B = 7
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)


def is_on_curve(point):
    if point is None:
        return True
    x, y = point
    return (y * y - x * x * x - A * x - B) % P == 0


def point_add(p1, p2):
    """Affine addition on secp256k1. None is the point at infinity."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and (y1 + y2) % P == 0:
        return None

    if p1 == p2:
        # Tangent: lambda = 3x^2 / 2y  (a = 0, so the ax term drops out)
        lam = (3 * x1 * x1) * pow(2 * y1, P - 2, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, P - 2, P) % P

    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def point_mul(k, point):
    """Double-and-add. Not constant time -- see the module docstring."""
    k %= N
    if k == 0 or point is None:
        return None

    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


def decompress_y(x, odd):
    """The curve point with this x and the requested y parity, or None.

    p % 4 == 3 for secp256k1, so the square root is a single exponentiation.
    Returns None when x is not on the curve, which is a malformed signature
    rather than a failed login and must be reported as such.
    """
    alpha = (pow(x, 3, P) + A * x + B) % P
    beta = pow(alpha, (P + 1) // 4, P)
    if pow(beta, 2, P) != alpha:
        return None
    return beta if (beta % 2 == 1) == odd else P - beta


def recover_public_key(msg_hash: bytes, r: int, s: int, recovery_id: int):
    """Recover the public key that produced (r, s) over `msg_hash`.

    Returns (x, y), or None if the signature does not correspond to any point.

    Q = r^-1 (sR - eG), where R is the curve point whose x-coordinate is r and
    whose y parity comes from the recovery id.
    """
    if not (0 < r < N and 0 < s < N):
        return None
    if recovery_id not in (0, 1, 2, 3):
        return None

    # recovery_id >= 2 means r was reduced mod n; astronomically rare, handled
    # for completeness rather than because it has ever been seen.
    x = r + N if recovery_id >= 2 else r
    if x >= P:
        return None

    y = decompress_y(x, odd=bool(recovery_id & 1))
    if y is None:
        return None

    R = (x, y)
    if point_mul(N, R) is not None:      # R must be of order n
        return None

    e = int.from_bytes(msg_hash, "big")
    r_inv = pow(r, N - 2, N)

    # Q = r^-1 * (s*R - e*G)
    point = point_add(point_mul(s, R), point_mul(N - (e % N), G))
    Q = point_mul(r_inv, point)

    return Q if Q is not None and is_on_curve(Q) else None


def public_key_bytes(public_key) -> bytes:
    """Uncompressed 64-byte encoding (x || y), which is what Ethereum hashes."""
    x, y = public_key
    return x.to_bytes(32, "big") + y.to_bytes(32, "big")
