"""Contract tests for content-addressed storage.

The properties that matter are the ones a decentralised claim rests on: an
address must be recomputable from the bytes, tampering must be detectable, and
an inclusion proof must reject anything that is not actually in the set.
"""
import json
import os

import pytest

import content_store as cs


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("AGI_CONTENT_STORE", str(tmp_path / "objects"))


def test_address_is_the_hash_of_the_stored_bytes():
    digest = cs.put(b"docking run")
    assert cs.get(digest) == b"docking run"
    assert cs.hash_bytes(b"docking run") == digest


def test_key_order_does_not_change_the_address():
    """Canonical encoding; otherwise the same result gets two addresses."""
    assert cs.put({"a": 1, "b": 2}) == cs.put({"b": 2, "a": 1})


def test_identical_content_is_stored_once():
    first = cs.put({"compound": "AGI-001"})
    second = cs.put({"compound": "AGI-001"})
    assert first == second


def test_tampering_is_detected():
    """The point of the whole module: altered bytes fail their own address."""
    digest = cs.put({"score": -9.96})
    assert cs.verify(digest)

    path = os.path.join(os.environ["AGI_CONTENT_STORE"], digest[:2], digest[2:])
    with open(path, "wb") as fh:
        fh.write(b"altered")

    assert not cs.verify(digest)


def test_missing_object_verifies_false_rather_than_raising():
    assert cs.verify("f" * 64) is False
    assert cs.get("f" * 64) is None


def test_empty_set_has_a_defined_root():
    assert cs.merkle_root([]) == cs.EMPTY


def test_single_item_root_is_that_item():
    digest = cs.put({"only": True})
    assert cs.merkle_root([digest]) == digest


@pytest.mark.parametrize("count", [2, 3, 4, 5, 8, 9])
def test_inclusion_proof_verifies_for_every_member(count):
    digests = [cs.put({"run": i}) for i in range(count)]
    root = cs.merkle_root(digests)

    for index, digest in enumerate(digests):
        proof = cs.inclusion_proof(digests, index)
        assert cs.verify_inclusion(digest, proof, root), f"member {index} of {count}"


def test_inclusion_proof_rejects_a_non_member():
    digests = [cs.put({"run": i}) for i in range(5)]
    root = cs.merkle_root(digests)
    outsider = cs.put({"run": "not in the set"})

    assert not cs.verify_inclusion(outsider, cs.inclusion_proof(digests, 0), root)


def test_reordering_changes_the_root():
    """Order is part of what the root commits to."""
    digests = [cs.put({"run": i}) for i in range(4)]
    assert cs.merkle_root(digests) != cs.merkle_root(list(reversed(digests)))


def test_odd_node_is_promoted_not_duplicated():
    """Duplicating the last node lets two different lists share a root."""
    a = [cs.put({"run": i}) for i in range(3)]
    duplicated_last = a + [a[-1]]
    assert cs.merkle_root(a) != cs.merkle_root(duplicated_last)


def test_manifest_root_covers_its_entries():
    doc = cs.manifest({"panel": "StJude", "count": 15}, label="run")

    ordered = [doc["entries"][name] for name in doc["order"]]
    assert cs.merkle_root(ordered) == doc["merkle_root"]

    for index, digest in enumerate(ordered):
        assert cs.verify_inclusion(digest, cs.inclusion_proof(ordered, index), doc["merkle_root"])


def test_manifest_is_itself_addressable():
    doc = cs.manifest({"x": 1})
    stored = cs.get_json(doc["manifest_address"])
    assert stored["merkle_root"] == doc["merkle_root"]


def test_manifest_states_that_nothing_is_broadcast():
    """Guards against this being described as a blockchain later."""
    assert "not" in cs.manifest({"x": 1})["note"].lower()
