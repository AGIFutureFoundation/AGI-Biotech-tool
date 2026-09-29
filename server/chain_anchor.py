"""Anchor a research record's Merkle root on Monad, without ever holding a key.

content_store.py already reduces a run to one Merkle root and notes that the
root "is what you would anchor". js/ledger.js says the same of its hash chain.
This module closes that loop.

What anchoring actually buys, stated precisely so nobody oversells it:

  It proves a specific byte-for-byte record EXISTED by a certain block, and that
  it has not changed since. That is a timestamp and a tamper-evidence seal.

  It does NOT make the contents true. A docking score that was a placeholder
  before it was anchored is a placeholder that now has a block number next to
  it. Permanence is not evidence.

That distinction is the reason for the hard rule below: a record carrying
SYNTHETIC values is refused by default. Anchoring is irreversible and confers
visible authority -- "verified on-chain" -- and handing that authority to
placeholder numbers is the worst failure this repo could ship. Synthetic records
can still be anchored, but only by passing ``allow_synthetic=True``, which
stamps the refusal reason into the payload itself so it travels with the record.

KEY HANDLING: there is none, by design. This module builds an UNSIGNED
transaction for a person to review and sign in their own wallet. It cannot
broadcast, holds no private key, and touches no account -- the same boundary
compound_sourcing.request_for_quote() draws around a purchase order.

EXERCISED / NOT EXERCISED, recorded rather than implied:
  - Payload construction, ABI encoding, selectors, EIP-55: covered by
    tests/test_chain_anchor.py against published vectors. Verified.
  - Live RPC reads (verify_anchor, suggested_fees): NOT exercised against a
    Monad node in the environment this was written in. The request shape follows
    standard Ethereum JSON-RPC, which Monad implements, but no live 200 has been
    seen. Treat the parse as unverified until it has.
"""
import datetime as _dt
import json
import urllib.error
import urllib.request

import synthetic_provenance as sp
from keccak import event_topic, keccak256, selector, to_checksum_address

SCHEMA_VERSION = "1.0"

# --------------------------------------------------------------------------- networks

#: Chain parameters as published in Monad's developer documentation.
#: Chain IDs are load-bearing: a wrong one produces a signature that is either
#: rejected or, worse, valid on a different chain. Sourced, not remembered.
NETWORKS = {
    "monad-mainnet": {
        "name": "Monad Mainnet", "chain_id": 143,
        "rpc": "https://rpc.monad.xyz",
        "explorer": "https://monadscan.com",
        "currency": {"symbol": "MON", "decimals": 18},
        "source": "https://docs.monad.xyz/developer-essentials/network-information",
    },
    "monad-testnet": {
        "name": "Monad Testnet", "chain_id": 10143,
        "rpc": "https://rpc.testnet.monad.xyz",
        "explorer": "https://testnet.monadscan.com",
        "currency": {"symbol": "MON", "decimals": 18},
        "source": "https://chainlist.org/chain/10143",
    },
}

#: Testnet on purpose. Anchoring to mainnet costs real money and is permanent;
#: that should be a decision someone types, not a default they inherit.
DEFAULT_NETWORK = "monad-testnet"

ANCHOR_BOUNDARY = (
    "THIS IS AN UNSIGNED TRANSACTION FOR A HUMAN TO REVIEW AND SIGN. It has not been "
    "signed, broadcast or submitted, no key was used or requested, and this software "
    "cannot send it. Nothing is on-chain until you sign this in your own wallet."
)

ANCHOR_MEANING = (
    "An anchored root proves this exact record existed by the block it landed in and "
    "has not changed since. It is a timestamp and a tamper seal. It is NOT evidence "
    "that the contents are correct, that any experiment was run, or that any number "
    "in the record was measured rather than generated."
)

SYNTHETIC_REFUSAL = (
    "REFUSED: this record contains SYNTHETIC placeholder values. Anchoring is permanent "
    "and reads as authority -- an anchored placeholder becomes a placeholder that looks "
    "blockchain-verified. Replace the synthetic fields with measured values, or pass "
    "allow_synthetic=True to anchor it with that fact recorded on the payload."
)

# --------------------------------------------------------------------------- registry ABI

#: contracts/ProvenanceRegistry.sol. Signatures are canonical (no names, no
#: spaces); the selector and topic below are derived, never transcribed.
ANCHOR_SIGNATURE = "anchor(bytes32,string)"
ANCHORED_EVENT = "Anchored(address,bytes32,string,uint256)"

ANCHOR_SELECTOR = selector(ANCHOR_SIGNATURE)
ANCHORED_TOPIC = event_topic(ANCHORED_EVENT)

#: Marker for the contract-free mode: a plain transaction whose calldata is
#: this tag followed by the 32-byte root. Costs one transaction and no
#: deployment, at the price of no indexed events.
BARE_TAG = b"AGIBIOXR\x01"


def _hex32(root: str) -> bytes:
    """A 32-byte Merkle root as bytes, rejecting anything the wrong size."""
    raw = str(root).lower().removeprefix("0x")
    if len(raw) != 64 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError(
            f"a Merkle root must be 32 bytes of hex (64 chars); got {len(raw)} chars: {root!r}")
    return bytes.fromhex(raw)


def encode_anchor_calldata(root: str, label: str = "") -> str:
    """ABI-encode anchor(bytes32,string) -- selector, head, then tail.

    Hand-encoded rather than pulled from a library: the layout is fixed and
    small, and the test file checks it offset by offset.
    """
    root_bytes = _hex32(root)
    label_bytes = str(label).encode()

    head = root_bytes                                   # arg 0: bytes32, inline
    head += (64).to_bytes(32, "big")                    # arg 1: offset to tail (2 words)

    tail = len(label_bytes).to_bytes(32, "big")
    if label_bytes:                                     # right-pad to a word boundary
        padding = (-len(label_bytes)) % 32
        tail += label_bytes + b"\x00" * padding

    return ANCHOR_SELECTOR + (head + tail).hex()


def encode_bare_calldata(root: str) -> str:
    """Contract-free calldata: tag + 32-byte root, for anchoring with no deploy."""
    return "0x" + (BARE_TAG + _hex32(root)).hex()


# --------------------------------------------------------------------------- building the payload

def _root_of(record):
    """Accept a manifest, a content_store root, or a bare 0x-hex string."""
    if isinstance(record, str):
        return record, None
    if isinstance(record, dict):
        root = record.get("merkle_root") or record.get("root")
        if root:
            return root, record
    raise ValueError(
        "expected a content_store manifest with a 'merkle_root', or a 32-byte hex root")


def _record_is_synthetic(manifest):
    """Does this record hold placeholder values? Resolved through the store.

    A content_store manifest's ``entries`` map names to ADDRESSES, not values,
    so inspecting the manifest itself finds only hex digests and always reports
    clean. The gate has to fetch what those addresses point at.

    Returns (synthetic, unresolved) where `unresolved` names entries whose
    objects could not be read. An unreadable entry is reported rather than
    assumed innocent: the caller is told the check was incomplete.
    """
    if manifest is None:
        return False, []

    entries = manifest.get("entries")
    if not isinstance(entries, dict):
        return sp.is_synthetic(manifest), []

    # Anything outside `entries` (labels, notes) is still worth checking.
    synthetic = sp.is_synthetic({k: v for k, v in manifest.items() if k != "entries"})
    unresolved = []

    import content_store

    for name, address in entries.items():
        if not (isinstance(address, str) and len(address) == 64):
            synthetic = synthetic or sp.is_synthetic(address)
            continue
        try:
            obj = content_store.get_json(address)
        except (ValueError, OSError):
            obj = None
        if obj is None:
            unresolved.append(name)
            continue
        synthetic = synthetic or sp.is_synthetic(obj)

    return synthetic, unresolved


def anchor_payload(record, network=DEFAULT_NETWORK, registry_address=None, label="",
                   from_address=None, allow_synthetic=False):
    """Build the unsigned transaction that would anchor `record`'s Merkle root.

    `record` is a content_store.manifest() dict (or a bare root). With
    `registry_address` the payload calls ProvenanceRegistry.anchor(); without
    one it falls back to contract-free calldata, which needs no deployment.

    Returns a dict carrying the unsigned tx, what it means, what it does not
    mean, and -- if the record was synthetic -- that fact, recorded inline so it
    cannot be separated from the thing being anchored.
    """
    if network not in NETWORKS:
        raise ValueError(f"unknown network {network!r}; known: {sorted(NETWORKS)}")
    net = NETWORKS[network]
    root, manifest = _root_of(record)
    root = "0x" + _hex32(root).hex()

    synthetic, unresolved = _record_is_synthetic(manifest)
    if synthetic and not allow_synthetic:
        return {
            "schema_version": SCHEMA_VERSION,
            "anchored": False, "refused": True, "reason": SYNTHETIC_REFUSAL,
            "merkle_root": root, "network": network,
            "unsigned_transaction": None,
            "anchor_meaning": ANCHOR_MEANING,
        }

    if registry_address:
        to = to_checksum_address(registry_address)
        data = encode_anchor_calldata(root, label)
        mode = "registry"
    else:
        to = None
        data = encode_bare_calldata(root)
        mode = "bare_calldata"

    tx = {
        "from": to_checksum_address(from_address) if from_address else None,
        "to": to,
        "value": "0x0",
        "data": data,
        "chainId": net["chain_id"],
    }

    payload = {
        "schema_version": SCHEMA_VERSION,
        "prepared_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "anchored": False,                 # nothing is anchored until a human signs
        "refused": False,
        "mode": mode,
        "merkle_root": root,
        "label": label or None,
        "network": {"key": network, **{k: net[k] for k in
                                       ("name", "chain_id", "rpc", "explorer", "source")}},
        "unsigned_transaction": tx,
        "boundary": ANCHOR_BOUNDARY,
        "anchor_meaning": ANCHOR_MEANING,
        "next_steps": [
            "Review the calldata: the last 32 bytes (registry mode: bytes 4-36) are the root.",
            f"Sign and send it from a wallet on {net['name']} (chain id {net['chain_id']}).",
            "Keep the returned transaction hash next to the manifest.",
            "Re-check it later with verify_anchor(tx_hash, expected_root).",
        ],
        "caveats": [],
    }

    if tx["to"] is None:
        payload["caveats"].append(
            "No registry address given, so this is contract-free calldata. It is cheap and "
            "needs no deployment, but emits no indexed event: you must keep the transaction "
            "hash yourself, because nothing can look it up by root.")
    if synthetic:
        payload["synthetic"] = True
        payload["caveats"].append(
            "ANCHORING SYNTHETIC DATA: this record contains placeholder values and is being "
            "anchored anyway because allow_synthetic=True. " + SYNTHETIC_REFUSAL)
    if unresolved:
        payload["unresolved_entries"] = sorted(unresolved)
        payload["caveats"].append(
            f"INCOMPLETE CHECK: {len(unresolved)} entr"
            f"{'y' if len(unresolved) == 1 else 'ies'} could not be read back from the content "
            f"store ({', '.join(sorted(unresolved))}), so they were NOT screened for synthetic "
            "values. Absence of a refusal above does not cover them.")
    if network == "monad-mainnet":
        payload["caveats"].append(
            "MAINNET: this costs real MON and is permanent. There is no unanchor.")
    return payload


# --------------------------------------------------------------------------- read-only verification

def _rpc(network, method, params, timeout=15):
    """One JSON-RPC call. Read-only: nothing here can change chain state."""
    net = NETWORKS[network]
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    req = urllib.request.Request(
        net["rpc"], data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "User-Agent": "agi-bioxr-chain-anchor/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if "error" in out:
        return None, f"RPC error: {out['error']}"
    return out.get("result"), None


def verify_anchor(tx_hash, expected_root, network=DEFAULT_NETWORK):
    """Read a transaction back and confirm it carries `expected_root`.

    The whole point of anchoring is being able to check it later, from the
    chain, without trusting this repo. Failure to reach the node is reported as
    'unknown', never as 'not anchored' -- an outage is not a disproof.
    """
    want = "0x" + _hex32(expected_root).hex()
    tx, err = _rpc(network, "eth_getTransactionByHash", [tx_hash])
    if err:
        return {"verified": None, "status": "unreachable", "error": err,
                "note": "Could not reach the node. This is NOT evidence the anchor is absent.",
                "expected_root": want, "network": network, "tx_hash": tx_hash,
                "anchor_meaning": ANCHOR_MEANING, "parse_verified": False}
    if tx is None:
        return {"verified": False, "status": "not_found", "expected_root": want,
                "network": network, "tx_hash": tx_hash,
                "note": "No such transaction on this network. Check you are on the right chain.",
                "anchor_meaning": ANCHOR_MEANING, "parse_verified": False}

    data = (tx.get("input") or "").lower()
    found = want.removeprefix("0x") in data
    receipt, _ = _rpc(network, "eth_getTransactionReceipt", [tx_hash])
    mined = bool(receipt and receipt.get("blockNumber"))

    return {
        "verified": bool(found and mined),
        "status": ("confirmed" if found and mined else
                   "root_present_but_pending" if found else "root_absent"),
        "expected_root": want,
        "root_found_in_calldata": found,
        "block_number": int(receipt["blockNumber"], 16) if mined else None,
        "tx_hash": tx_hash,
        "from": tx.get("from"),
        "to": tx.get("to"),
        "network": network,
        "explorer_url": f"{NETWORKS[network]['explorer']}/tx/{tx_hash}",
        "anchor_meaning": ANCHOR_MEANING,
        "parse_verified": False,   # see the module docstring: no live 200 seen yet
    }


def anchor_status(payload):
    """One honest line about where a payload stands. Never claims more than it has."""
    if payload.get("refused"):
        return "REFUSED -- not anchored, and no transaction was built."
    if not payload.get("anchored"):
        return ("UNSIGNED -- a transaction has been prepared but nothing is on-chain. "
                "Sign it in your own wallet to anchor.")
    return "ANCHORED."
