"""Consent has to hold where it is inconvenient, or it is decoration.

These tests are the cases where honouring consent costs something: it makes an
episode unusable, it invalidates data already collected, it means refusing an
export somebody wants. A consent system that only works when nothing is at stake
has not been tested at all.

The four that matter:

  a later yes does not cover earlier frames -- people agree once they know what
  was recorded, and treating a subsequent yes as retroactive makes "they
  consented" meaningless;

  revocation reaches data already collected, or it is a preference about future
  collection rather than a right;

  an export that drops someone says so, because downstream a quiet omission
  looks like a complete recording;

  and when dropping the person doing the manipulating would leave objects moving
  by themselves, the export is refused rather than shipped -- that is not a
  shorter demonstration, it is a false one, and it would teach a policy
  something untrue.
"""
import datetime as _dt
import json
import pathlib

import pytest

import episodes as ep


def _t(offset_seconds):
    base = _dt.datetime(2026, 9, 26, 12, 0, tzinfo=_dt.timezone.utc)
    return base + _dt.timedelta(seconds=offset_seconds)


def _episode(actors=("alice",), frames=30, with_grasp=True, started_at=None):
    e = ep.Episode("e1", room="lab", instruction="Place the ligand in the pocket",
                   started_at=started_at or _t(0))
    for i in range(frames):
        e.add_frame(i * 0.1,
                    {a: {"head": {"p": [0, 1.6, 0], "q": [0, 0, 0, 1]},
                         "hands": [[0.2, 1.2, -0.3], [-0.2, 1.2, -0.3]]} for a in actors},
                    {"ligand": {"p": [0, 1, -0.5], "q": [0, 0, 0, 1],
                                "held_by": actors[0] if with_grasp else None}})
    if with_grasp:
        e.add_event(0.5, "grab", actors[0], "ligand")
        e.add_event(2.5, "release", actors[0], "ligand")
    return e


def _ledger(**grants):
    """ledger(alice='model_training') -> consent granted before the episode."""
    led = ep.ConsentLedger()
    for client, scope in grants.items():
        led.grant(client, scope, at=_t(-60), display_name=client.title())
    return led


# --------------------------------------------------------------------------- defaults

def test_consent_defaults_to_none():
    """Recording for training is opted into, never out of."""
    assert ep.CONSENT_DEFAULT == "none"
    assert ep.ConsentLedger().scope_at("alice", _t(0)) == "none"


def test_without_consent_nothing_exports():
    out = ep.prepare_export(_episode(), ep.ConsentLedger())

    assert out["allowed"] is False
    assert out["frames"] == []
    assert "No participant consented" in out["refused_reason"]


def test_session_only_consent_does_not_permit_training():
    """The scopes must actually differ, or they are one boolean wearing five hats."""
    out = ep.prepare_export(_episode(), _ledger(alice="session_only"),
                            purpose="model_training")
    assert out["allowed"] is False


def test_a_stronger_scope_covers_a_weaker_purpose():
    out = ep.prepare_export(_episode(), _ledger(alice="redistribution"),
                            purpose="research")
    assert out["allowed"] is True


def test_an_unknown_scope_never_allows_anything():
    assert ep.scope_allows("gold", "research") is False
    assert ep.scope_allows("research", "anything") is False
    with pytest.raises(ValueError):
        ep.ConsentLedger().grant("alice", "sure_whatever")


# --------------------------------------------------------------------------- time

def test_consent_given_later_does_not_cover_earlier_frames():
    """A yes at 14:05 does not reach what happened at 14:00."""
    led = ep.ConsentLedger()
    led.grant("alice", "model_training", at=_t(300))       # after the episode

    out = ep.prepare_export(_episode(started_at=_t(0)), led)
    assert out["allowed"] is False


def test_consent_given_before_the_episode_does_cover_it():
    led = ep.ConsentLedger()
    led.grant("alice", "model_training", at=_t(-1))
    assert ep.prepare_export(_episode(started_at=_t(0)), led)["allowed"] is True


def test_revocation_reaches_data_already_collected():
    """Otherwise it is a preference about future collection, not a right."""
    led = _ledger(alice="model_training")
    assert ep.prepare_export(_episode(), led)["allowed"] is True

    led.revoke("alice")
    after = ep.prepare_export(_episode(), led)

    assert after["allowed"] is False
    assert led.scope_at("alice", _t(0)) == "none"


def test_revoking_one_person_does_not_revoke_another():
    led = _ledger(alice="model_training", bob="model_training")
    led.revoke("alice")

    assert led.scope_at("alice", _t(0)) == "none"
    assert led.scope_at("bob", _t(0)) == "model_training"


# --------------------------------------------------------------------------- partial consent

def test_a_non_consenting_participant_is_removed_and_named():
    """A quiet omission reads downstream as a complete recording."""
    e = _episode(actors=("alice", "bob"))
    out = ep.prepare_export(e, _ledger(alice="model_training", bob="session_only"))

    assert out["allowed"] is True
    excluded = {x["client"] for x in out["consent"]["excluded"]}
    assert excluded == {"bob"}

    # Bob appears in no frame.
    assert all("bob" not in f["actors"] for f in out["frames"])
    assert any("did not consent" in c for c in out["caveats"])


def test_the_caveat_warns_against_reading_gaps_as_inactivity():
    e = _episode(actors=("alice", "bob"))
    out = ep.prepare_export(e, _ledger(alice="model_training", bob="none"))
    assert any("do not treat gaps as inactivity" in c for c in out["caveats"])


def test_removing_the_manipulator_refuses_rather_than_ships_a_fragment():
    """Objects moving with nobody responsible is a false demonstration."""
    e = _episode(actors=("alice", "bob"))
    e.events = [{"t": 0.5, "kind": "grab", "client": "bob", "object": "ligand",
                 "detail": None}]

    out = ep.prepare_export(e, _ledger(alice="model_training", bob="session_only"))

    assert out["allowed"] is False
    assert "not a shorter demonstration" in out["refused_reason"]


def test_too_few_surviving_frames_is_refused():
    e = _episode(actors=("alice",), frames=4, with_grasp=False)
    out = ep.prepare_export(e, _ledger(alice="model_training"))

    assert out["allowed"] is False
    assert "minimum for a usable demonstration" in out["refused_reason"]


# --------------------------------------------------------------------------- the export

def test_a_consented_episode_carries_its_instruction_and_events():
    out = ep.prepare_export(_episode(), _ledger(alice="model_training"))

    assert out["instruction"] == "Place the ligand in the pocket"
    assert {e["kind"] for e in out["events"]} == {"grab", "release"}
    assert out["format"] == ep.FORMAT


def test_the_export_states_what_the_purpose_means():
    out = ep.prepare_export(_episode(), _ledger(alice="model_training"))
    assert out["purpose_meaning"] == ep.SCOPE_MEANING["model_training"]


def test_every_export_carries_the_biometric_notice():
    """Pseudonymisation is not anonymisation for motion traces."""
    out = ep.prepare_export(_episode(), _ledger(alice="model_training"))
    assert "not anonymisation" in out["consent"]["notice"]


def test_writing_refuses_an_episode_that_was_not_allowed(tmp_path):
    """The guard has to be at the filesystem boundary too, not only in review."""
    out = ep.prepare_export(_episode(), ep.ConsentLedger())
    with pytest.raises(PermissionError):
        ep.write_episode(out, str(tmp_path))
    assert list(pathlib.Path(tmp_path).iterdir()) == []


def test_a_written_episode_carries_its_consent_alongside_the_data(tmp_path):
    """A dataset must not be copyable without the terms it was collected under."""
    out = ep.prepare_export(_episode(), _ledger(alice="model_training"))
    written = ep.write_episode(out, str(tmp_path))

    path = pathlib.Path(written["path"])
    assert (path / "consent.json").exists()
    assert (path / "meta.json").exists()
    assert (path / "frames.jsonl").exists()
    assert (path / "events.jsonl").exists()

    consent = json.loads((path / "consent.json").read_text())
    assert consent["consented"][0]["client"] == "alice"

    lines = (path / "frames.jsonl").read_text().strip().split("\n")
    assert len(lines) == written["frames"] == 30
    assert json.loads(lines[0])["actors"]["alice"]["head"]["p"] == [0, 1.6, 0]


def test_the_metadata_documents_the_schema(tmp_path):
    """Whoever converts this to parquet needs to know what the columns mean."""
    out = ep.prepare_export(_episode(), _ledger(alice="model_training"))
    written = ep.write_episode(out, str(tmp_path))
    meta = json.loads((pathlib.Path(written["path"]) / "meta.json").read_text())

    assert "held_by" in meta["schema"]["frame"]
    assert "grab|release" in meta["schema"]["event"]
    assert meta["frame_count"] == 30
