"""Content-addressed storage for research artefacts.

An artefact is stored under the SHA-256 of its bytes, so the address *is* the
integrity proof: asking for a hash can only return content that hashes to it,
and identical content stored twice occupies one object. That is what makes a
result citable -- a docking run, a panel snapshot or an inventory can be
referenced by a hash that anyone can recompute, rather than by a filename that
can be edited underneath the reference.

A Merkle root over a set of objects reduces a whole run to one hash, which is
the value worth publishing: a DAO proposal, a lab notebook or a blockchain
transaction can carry 32 bytes instead of a dataset, and anyone holding the
artefacts can prove membership against it.

What this is not: nothing here broadcasts, and no consensus is involved. It
produces a root you *could* anchor on-chain and an inclusion proof that
verifies against it. Anchoring is a separate, deliberate act with a cost, and
this module does not do it or pretend to. js/ledger.js already draws the same
line for the browser-side hash chain and this is its server-side counterpart.
"""
import hashlib
import json
import os
from typing import Dict, List, Optional, Tuple

EMPTY = "0" * 64


def _root_dir() -> str:
    return os.environ.get(
        "AGI_CONTENT_STORE",
        os.path.join(os.path.expanduser("~"), ".cache", "agi-bioxr", "objects"),
    )


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_json(obj) -> str:
    """Hash of a canonical JSON encoding, so key order cannot change the address."""
    return hash_bytes(canonical(obj))


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _path(digest: str) -> str:
    # Two-character prefix directory, as git does, to keep directories small.
    return os.path.join(_root_dir(), digest[:2], digest[2:])


def put(data) -> str:
    """Store bytes or a JSON-able object. Returns its address."""
    raw = data if isinstance(data, bytes) else canonical(data)
    digest = hash_bytes(raw)
    path = _path(digest)

    if os.path.exists(path):
        return digest  # identical content is already here, by definition

    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Write to a temporary name first so an interrupted write cannot leave a
    # file sitting at an address whose content does not hash to it.
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, path)
    return digest


def get(digest: str) -> Optional[bytes]:
    path = _path(digest)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return fh.read()


def get_json(digest: str):
    raw = get(digest)
    return json.loads(raw) if raw is not None else None


def verify(digest: str) -> bool:
    """Recompute the address from the stored bytes. False if absent or altered."""
    raw = get(digest)
    return raw is not None and hash_bytes(raw) == digest


def merkle_root(digests: List[str]) -> str:
    """Root over an ordered list of addresses.

    An odd node is promoted rather than duplicated. Duplicating the last node,
    as Bitcoin does, admits two different lists with the same root; promoting
    avoids that.
    """
    if not digests:
        return EMPTY

    level = list(digests)
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level) - 1, 2):
            nxt.append(hash_bytes(bytes.fromhex(level[i]) + bytes.fromhex(level[i + 1])))
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
    return level[0]


def inclusion_proof(digests: List[str], index: int) -> List[Tuple[str, str]]:
    """Sibling path proving digests[index] is under merkle_root(digests)."""
    if not 0 <= index < len(digests):
        return []

    proof, level, idx = [], list(digests), index
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level) - 1, 2):
            if i == idx:
                proof.append(("right", level[i + 1]))
            elif i + 1 == idx:
                proof.append(("left", level[i]))
            nxt.append(hash_bytes(bytes.fromhex(level[i]) + bytes.fromhex(level[i + 1])))
        if len(level) % 2:
            nxt.append(level[-1])
        idx //= 2
        level = nxt
    return proof


def verify_inclusion(digest: str, proof: List[Tuple[str, str]], root: str) -> bool:
    current = digest
    for side, sibling in proof:
        pair = (sibling, current) if side == "left" else (current, sibling)
        current = hash_bytes(bytes.fromhex(pair[0]) + bytes.fromhex(pair[1]))
    return current == root


def manifest(entries: Dict[str, object], label: str = "") -> Dict:
    """Store each entry and return a manifest carrying the root.

    The manifest is itself stored, so it has an address too. Publishing that one
    address is enough for a holder of the artefacts to verify every member.
    """
    addresses = {name: put(value) for name, value in sorted(entries.items())}
    ordered = [addresses[name] for name in sorted(addresses)]
    root = merkle_root(ordered)

    doc = {
        "label": label,
        "entries": addresses,
        "order": sorted(addresses),
        "merkle_root": root,
        "algorithm": "sha256",
        "note": "Local content-addressed store. Nothing is broadcast and no "
                "consensus is involved; the root is what you would anchor.",
    }
    doc["manifest_address"] = put(doc)
    return doc
