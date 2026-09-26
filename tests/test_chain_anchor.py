"""What must hold before anything from this repo is written to a public chain.

Anchoring is the one action here that cannot be taken back. A wrong hash, a
wrong chain id, or a placeholder number granted the authority of "verified
on-chain" is permanent and public. So the things checked here are the things
that are unrecoverable if wrong:

  * the hash is really Keccak-256 and not SHA3-256 (they differ, silently),
  * the chain ids are the real ones,
  * the calldata carries the root the caller asked for, at the offset a decoder
    will look for it,
  * a SYNTHETIC record is refused rather than immortalised,
  * an unreachable node reports "unknown", never "not anchored".

Everything is offline; the only RPC in the module is stubbed.
"""
import hashlib

import pytest

import chain_anchor as ca
import keccak
import synthetic_provenance as sp


# --------------------------------------------------------------------------- the hash itself

#: Published Keccak-256 vectors. If these drift, every selector, topic and
#: address this module produces is wrong in a way that still looks like valid hex.
KECCAK_VECTORS = [
    ("", "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"),
    ("abc", "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45"),
    ("The quick brown fox jumps over the lazy dog",
     "4d741b6f1eb29cb2a9b9911c82f56fa8d73b04959d3d9d222895df6c0b28aa15"),
]


@pytest.mark.parametrize("message,expected", KECCAK_VECTORS)
def test_keccak_matches_published_vectors(message, expected):
    assert keccak.keccak256(message).hex() == expected


def test_keccak_is_not_sha3():
    """The trap this module exists to avoid, pinned so nobody 'simplifies' it away.

    hashlib.sha3_256 differs from Keccak-256 only in a padding byte, so swapping
    one for the other produces plausible-looking output that no Ethereum node
    would ever agree with.
    """
    assert keccak.keccak256(b"") != hashlib.sha3_256(b"").digest()


@pytest.mark.parametrize("length", [0, 1, 135, 136, 137, 271, 272])
def test_keccak_handles_the_rate_boundary(length):
    """135/136/137 bytes straddle the 136-byte block: the classic padding bug."""
    digest = keccak.keccak256(b"a" * length)
    assert len(digest) == 32


def test_selector_matches_a_known_erc20_signature():
    """transfer(address,uint256) is 0xa9059cbb on every EVM chain in existence."""
    assert keccak.selector("transfer(address,uint256)") == "0xa9059cbb"


@pytest.mark.parametrize("address", [
    "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
    "0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359",
    "0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB",
    "0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb",
])
def test_eip55_checksum_vectors(address):
    """The checksum is what catches a mistyped address before it swallows funds."""
    assert keccak.to_checksum_address(address.lower()) == address
    assert keccak.to_checksum_address(address) == address


def test_bad_address_is_rejected_rather_than_reformatted():
    with pytest.raises(ValueError):
        keccak.to_checksum_address("0xnothex")
    with pytest.raises(ValueError):
        keccak.to_checksum_address("0xdeadbeef")          # too short


# --------------------------------------------------------------------------- chain parameters

def test_chain_ids_are_the_published_ones():
    """A wrong chain id yields a signature valid on some *other* chain."""
    assert ca.NETWORKS["monad-mainnet"]["chain_id"] == 143
    assert ca.NETWORKS["monad-testnet"]["chain_id"] == 10143


def test_every_network_records_where_its_parameters_came_from():
    for key, net in ca.NETWORKS.items():
        assert net["source"].startswith("https://"), key


def test_the_default_network_is_testnet():
    """Spending real money and writing permanently should be typed, not inherited."""
    assert ca.DEFAULT_NETWORK == "monad-testnet"
    payload = ca.anchor_payload("0x" + "11" * 32)
    assert payload["network"]["chain_id"] == 10143


def test_unknown_network_is_refused():
    with pytest.raises(ValueError):
        ca.anchor_payload("0x" + "11" * 32, network="ethereum")


# --------------------------------------------------------------------------- calldata

ROOT = "0x" + "ab" * 32


def test_bare_calldata_contains_the_root_verbatim():
    data = ca.encode_bare_calldata(ROOT)
    assert data.endswith("ab" * 32)
    assert bytes.fromhex(data[2:]).startswith(ca.BARE_TAG)


def test_registry_calldata_places_the_root_where_a_decoder_looks(_=None):
    """ABI layout, offset by offset -- hand-encoded, so hand-checked.

    selector | root (word 0) | offset=0x40 (word 1) | length | padded label
    """
    data = ca.encode_anchor_calldata(ROOT, "run-42")
    raw = bytes.fromhex(data.removeprefix("0x"))

    assert data.startswith(ca.ANCHOR_SELECTOR)
    body = raw[4:]
    assert body[0:32].hex() == "ab" * 32                    # the root, word 0
    assert int.from_bytes(body[32:64], "big") == 64         # tail offset, word 1
    assert int.from_bytes(body[64:96], "big") == 6          # len("run-42")
    assert body[96:102] == b"run-42"
    assert len(body) % 32 == 0                              # word-aligned throughout


def test_empty_label_still_encodes_a_valid_tail():
    body = bytes.fromhex(ca.encode_anchor_calldata(ROOT).removeprefix("0x"))[4:]
    assert int.from_bytes(body[32:64], "big") == 64
    assert int.from_bytes(body[64:96], "big") == 0
    assert len(body) == 96


def test_selector_and_topic_are_derived_not_transcribed():
    """Recomputed here from the signature, so a typo cannot survive in both places."""
    assert ca.ANCHOR_SELECTOR == keccak.selector(ca.ANCHOR_SIGNATURE)
    assert ca.ANCHORED_TOPIC == keccak.event_topic(ca.ANCHORED_EVENT)
    assert len(ca.ANCHORED_TOPIC) == 66


@pytest.mark.parametrize("bad", ["0x1234", "", "0x" + "zz" * 32, "0x" + "ab" * 31])
def test_a_malformed_root_is_refused(bad):
    """A truncated root would anchor something that proves nothing."""
    with pytest.raises(ValueError):
        ca.encode_bare_calldata(bad)


# --------------------------------------------------------------------------- the safety rule

def _synthetic_manifest():
    return {"merkle_root": ROOT, "label": "docking-run",
            "entries": {"best_score": sp.SyntheticValue(-9.4)}}


def test_synthetic_records_are_refused_by_default():
    """The core rule: placeholders must not be handed the authority of the chain."""
    out = ca.anchor_payload(_synthetic_manifest())

    assert out["refused"] is True
    assert out["anchored"] is False
    assert out["unsigned_transaction"] is None       # nothing to sign, even by accident
    assert "SYNTHETIC" in out["reason"]


def test_a_clean_manifest_is_not_refused():
    """The rule must discriminate, not refuse everything."""
    out = ca.anchor_payload({"merkle_root": ROOT, "entries": {"best_score": -9.4}})
    assert out["refused"] is False
    assert out["unsigned_transaction"]["data"].endswith("ab" * 32)


def test_overriding_the_refusal_records_it_on_the_payload():
    """An override must travel with the record, not be lost at the call site."""
    out = ca.anchor_payload(_synthetic_manifest(), allow_synthetic=True)

    assert out["refused"] is False
    assert out["synthetic"] is True
    assert any("ANCHORING SYNTHETIC DATA" in c for c in out["caveats"])


def test_the_payload_says_what_anchoring_does_not_prove():
    """Overselling is the failure mode here, so the disclaimer ships inline."""
    out = ca.anchor_payload(ROOT)
    assert "NOT evidence that the contents are correct" in out["anchor_meaning"]


# --------------------------------------------------------------------------- key boundary

def test_no_transaction_is_ever_signed_or_sent():
    out = ca.anchor_payload(ROOT, from_address="0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed")

    assert out["anchored"] is False
    assert "has not been signed, broadcast or submitted" in out["boundary"]
    tx = out["unsigned_transaction"]
    for forbidden in ("privateKey", "private_key", "signature", "r", "s", "v"):
        assert forbidden not in tx
    assert ca.anchor_status(out).startswith("UNSIGNED")


def test_from_address_is_checksummed():
    out = ca.anchor_payload(ROOT, from_address="0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed")
    assert out["unsigned_transaction"]["from"] == "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"


def test_mainnet_says_it_costs_real_money():
    out = ca.anchor_payload(ROOT, network="monad-mainnet")
    assert any("real MON" in c and "no unanchor" in c for c in out["caveats"])


def test_contract_free_mode_warns_that_it_is_not_indexed():
    out = ca.anchor_payload(ROOT)
    assert out["mode"] == "bare_calldata"
    assert any("emits no indexed event" in c for c in out["caveats"])


# --------------------------------------------------------------------------- verification

def test_an_unreachable_node_is_unknown_not_absent(monkeypatch):
    """An outage must never be reported as 'this was never anchored'."""
    monkeypatch.setattr(ca, "_rpc", lambda *a, **k: (None, "URLError: offline"))

    out = ca.verify_anchor("0x" + "cd" * 32, ROOT)

    assert out["verified"] is None                 # not False
    assert out["status"] == "unreachable"
    assert "NOT evidence the anchor is absent" in out["note"]


@pytest.mark.parametrize("rpc_result,rpc_error", [
    (None, "URLError: offline"),      # unreachable
    (None, None),                     # not found
])
def test_every_verify_result_explains_what_an_anchor_proves(monkeypatch, rpc_result, rpc_error):
    """Every branch, not just the happy one -- a caller reads the same keys each time.

    Regression: the unreachable and not_found branches omitted anchor_meaning,
    and scripts/anchor_run.py crashed with a KeyError on the exact path a user
    hits first, which is an offline check.
    """
    monkeypatch.setattr(ca, "_rpc", lambda *a, **k: (rpc_result, rpc_error))
    out = ca.verify_anchor("0x" + "cd" * 32, ROOT)

    for key in ("anchor_meaning", "expected_root", "status", "verified",
                "tx_hash", "network", "parse_verified"):
        assert key in out, f"{out['status']} branch is missing {key!r}"


def test_a_mined_transaction_carrying_the_root_verifies(monkeypatch):
    def fake_rpc(network, method, params, timeout=15):
        if method == "eth_getTransactionByHash":
            return {"input": ca.encode_bare_calldata(ROOT), "from": "0xabc", "to": None}, None
        return {"blockNumber": "0x1e240"}, None

    monkeypatch.setattr(ca, "_rpc", fake_rpc)
    out = ca.verify_anchor("0x" + "cd" * 32, ROOT)

    assert out["verified"] is True
    assert out["status"] == "confirmed"
    assert out["block_number"] == 123456
    assert out["explorer_url"].startswith("https://testnet.monadscan.com/tx/")


def test_a_transaction_without_the_root_does_not_verify(monkeypatch):
    """The failure that matters: a real, mined tx that anchors something else."""
    other = "0x" + "99" * 32

    def fake_rpc(network, method, params, timeout=15):
        if method == "eth_getTransactionByHash":
            return {"input": ca.encode_bare_calldata(other)}, None
        return {"blockNumber": "0x10"}, None

    monkeypatch.setattr(ca, "_rpc", fake_rpc)
    out = ca.verify_anchor("0x" + "cd" * 32, ROOT)

    assert out["verified"] is False
    assert out["status"] == "root_absent"


def test_a_missing_transaction_is_reported_as_not_found(monkeypatch):
    monkeypatch.setattr(ca, "_rpc", lambda *a, **k: (None, None))
    out = ca.verify_anchor("0x" + "cd" * 32, ROOT)
    assert out["verified"] is False
    assert out["status"] == "not_found"


def test_verification_admits_its_parse_is_unexercised(monkeypatch):
    """No live Monad 200 was seen when this was written; the record says so."""
    monkeypatch.setattr(ca, "_rpc", lambda *a, **k: (
        {"input": ca.encode_bare_calldata(ROOT)}, None))
    assert ca.verify_anchor("0x" + "cd" * 32, ROOT)["parse_verified"] is False


# --------------------------------------------------------------------------- end to end

def test_the_gate_fires_on_a_REAL_manifest_not_just_a_hand_built_one(tmp_path, monkeypatch):
    """Regression: the refusal was inert on the only path that actually matters.

    content_store.manifest() maps entry names to ADDRESSES, not values, so
    inspecting the manifest dict found nothing but hex digests and always
    reported clean. The gate passed its own tests -- which built manifests with
    live values inline -- while doing nothing whatsoever in production.

    This builds the manifest the real way and asserts the refusal fires.
    """
    monkeypatch.setenv("AGI_CONTENT_STORE", str(tmp_path))
    import content_store

    manifest = content_store.manifest(
        {"result.json": {"target": "BCL2", "best_score": sp.SyntheticValue(-9.4)}},
        label="synthetic-run")

    assert "SYNTHETIC" not in str(manifest["entries"]), "entries are addresses, as assumed"

    out = ca.anchor_payload(manifest)
    assert out["refused"] is True
    assert out["unsigned_transaction"] is None


def test_an_entry_that_cannot_be_read_back_is_reported_not_assumed_clean(tmp_path, monkeypatch):
    """A screening that could not run must say so rather than pass silently."""
    monkeypatch.setenv("AGI_CONTENT_STORE", str(tmp_path))
    import content_store

    manifest = content_store.manifest({"result.json": {"score": -9.4}}, label="run")
    manifest["entries"]["missing.json"] = "0" * 64      # never stored

    out = ca.anchor_payload(manifest)

    assert out["refused"] is False                      # nothing synthetic was found
    assert out["unresolved_entries"] == ["missing.json"]
    assert any("INCOMPLETE CHECK" in c for c in out["caveats"])


def test_a_content_store_manifest_anchors_end_to_end(tmp_path, monkeypatch):
    """The real seam: content_store.manifest() -> anchor_payload(), no adapter."""
    monkeypatch.setenv("AGI_CONTENT_STORE", str(tmp_path))
    import content_store

    manifest = content_store.manifest(
        {"result.json": {"target": "BCL2", "score": -9.4}}, label="run-1")
    out = ca.anchor_payload(manifest, label="run-1")

    assert out["refused"] is False
    assert out["merkle_root"] == "0x" + manifest["merkle_root"].removeprefix("0x")
    assert out["unsigned_transaction"]["data"].endswith(
        manifest["merkle_root"].removeprefix("0x"))
