"""Keccak-256 (Ethereum's hash), in pure Python, with no dependencies.

Why this file exists rather than an import:

``hashlib.sha3_256`` is NOT Keccak-256. NIST changed the padding byte between
the Keccak submission (0x01) and the final SHA-3 standard (0x06), so the two
produce completely different digests for the same input. Ethereum froze on the
original Keccak. Reaching for hashlib here would produce function selectors,
event topics and address checksums that are all subtly, silently wrong -- valid
hex of the right length that no node would ever agree with.

pycryptodome/eth-hash would also do, but this module is ~70 lines, has to be
right only once, and is pinned against the published Keccak test vectors in
tests/test_chain_anchor.py. That is cheaper than a dependency on a machine where
disk is scarce.

Correctness is checked against known-answer vectors, not assumed.
"""

MASK = (1 << 64) - 1
RATE_BYTES = 136          # 1088-bit rate for Keccak-256
PAD_BYTE = 0x01           # original Keccak padding; SHA-3 uses 0x06

_RC = (
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
)

# Rotation offsets, indexed [x][y].
_ROT = (
    (0, 36, 3, 41, 18),
    (1, 44, 10, 45, 2),
    (62, 6, 43, 15, 61),
    (28, 55, 25, 21, 56),
    (27, 20, 39, 8, 14),
)


def _rol(value, n):
    n %= 64
    return ((value << n) | (value >> (64 - n))) & MASK


def _keccak_f(a):
    """The Keccak-f[1600] permutation, in place on a 5x5 lane array."""
    for rnd in range(24):
        # theta
        c = [a[x][0] ^ a[x][1] ^ a[x][2] ^ a[x][3] ^ a[x][4] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rol(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                a[x][y] ^= d[x]

        # rho (rotate) and pi (permute) in one pass
        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = _rol(a[x][y], _ROT[x][y])

        # chi
        for x in range(5):
            for y in range(5):
                a[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y] & MASK) & b[(x + 2) % 5][y])

        # iota
        a[0][0] ^= _RC[rnd]
    return a


def keccak256(data) -> bytes:
    """Keccak-256 digest of `data` (bytes, bytearray or str)."""
    if isinstance(data, str):
        data = data.encode()
    data = bytes(data)

    # Pad: 0x01 ... 0x80, collapsing to 0x81 when the block has one byte free.
    padlen = RATE_BYTES - (len(data) % RATE_BYTES)
    padded = data + bytes([PAD_BYTE] + [0] * (padlen - 2) + [0x80]) if padlen > 1 \
        else data + bytes([PAD_BYTE | 0x80])

    state = [[0] * 5 for _ in range(5)]
    for offset in range(0, len(padded), RATE_BYTES):
        block = padded[offset:offset + RATE_BYTES]
        for i in range(RATE_BYTES // 8):
            lane = int.from_bytes(block[i * 8:i * 8 + 8], "little")
            state[i % 5][i // 5] ^= lane
        _keccak_f(state)

    out = bytearray()
    for i in range(4):                       # 4 lanes = 32 bytes
        out += state[i % 5][i // 5].to_bytes(8, "little")
    return bytes(out)


def keccak256_hex(data) -> str:
    """Keccak-256 as a 0x-prefixed hex string."""
    return "0x" + keccak256(data).hex()


def selector(signature: str) -> str:
    """Solidity function selector: first 4 bytes of keccak256 of the signature.

    `signature` is the canonical form with no spaces or argument names, e.g.
    "anchor(bytes32,string)".
    """
    return "0x" + keccak256(signature).hex()[:8]


def event_topic(signature: str) -> str:
    """Topic0 for a Solidity event: the full keccak256 of the signature."""
    return keccak256_hex(signature)


def to_checksum_address(address: str) -> str:
    """EIP-55 mixed-case checksum form of a 20-byte hex address.

    The checksum is what catches a mistyped address before it swallows funds,
    so it is derived here rather than trusting whatever case came in.
    """
    raw = address.lower().removeprefix("0x")
    if len(raw) != 40 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError(f"not a 20-byte hex address: {address!r}")
    digest = keccak256(raw).hex()
    return "0x" + "".join(
        c.upper() if c.isalpha() and int(digest[i], 16) >= 8 else c
        for i, c in enumerate(raw)
    )
