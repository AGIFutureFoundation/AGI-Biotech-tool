"""Two people reaching for the same molecule at the same moment.

They cannot settle it between themselves. Each sees itself as first, because
neither has heard from the other yet -- at 12 Hz over SSE, "at the same moment"
covers about 80ms of disagreement. Without an arbiter both clients believe they
have it, both write transforms, and the molecule jitters between two hands while
neither person can work. That is the failure this module exists to prevent, and
it is not a crash: it looks like the app being laggy.

So the server decides, and these tests are about the decisions it makes:

  exactly one of two simultaneous claims wins,
  the loser is told who holds it rather than left retrying blindly,
  a crashed holder does not keep the object forever,
  refreshing does not spam the room with identical messages.

The last one is not cosmetic. A hold is refreshed every frame while someone
drags; broadcasting each refresh would put a message per frame per grab on every
peer's connection, which is precisely the lag the lock was added to avoid.
"""
import importlib
import sys

import pytest

server = importlib.import_module("server")


@pytest.fixture
def r():
    """A fresh room, isolated from the module-level ROOMS dict."""
    return {"subs": [], "state": {}, "grabs": {}}


def claim(r, client, obj="ligand", name=None, now=100.0):
    return server.arbitrate_grab(r, client, obj, "claim", name=name, now=now)


def release(r, client, obj="ligand", now=100.0):
    return server.arbitrate_grab(r, client, obj, "release", now=now)


# --------------------------------------------------------------------------- the race

def test_the_first_claim_wins(r):
    reply, changed = claim(r, "alice", name="Alice")

    assert reply["granted"] is True
    assert reply["holder"] == "alice"
    assert changed is True          # the room needs telling


def test_a_second_claimant_is_refused_and_told_who_has_it(r):
    """Being refused is useless without knowing who to ask."""
    claim(r, "alice", name="Alice")
    reply, changed = claim(r, "bob", name="Bob")

    assert reply["granted"] is False
    assert reply["holder"] == "alice"
    assert reply["holder_name"] == "Alice"
    assert "held by someone else" in reply["reason"]
    assert changed is False         # nothing changed; do not broadcast


def test_exactly_one_of_many_simultaneous_claims_wins(r):
    """The property that matters, stated directly."""
    granted = [claim(r, who, now=100.0)[0]["granted"]
               for who in ("alice", "bob", "carol", "dave")]
    assert granted.count(True) == 1
    assert granted[0] is True


def test_the_holder_can_reclaim_without_losing_it(r):
    """A re-claim from the holder is a refresh, not a contest it might lose."""
    claim(r, "alice", now=100.0)
    reply, changed = claim(r, "alice", now=101.0)

    assert reply["granted"] is True
    assert changed is False         # already theirs; no broadcast


def test_refreshing_extends_the_lease(r):
    claim(r, "alice", now=100.0)
    claim(r, "alice", now=104.0)
    assert r["grabs"]["ligand"]["expires"] == 104.0 + server.GRAB_TTL_SECONDS


def test_refreshing_does_not_broadcast_every_frame(r):
    """A drag refreshes at frame rate; broadcasting each one recreates the lag."""
    claim(r, "alice", now=100.0)
    changes = [claim(r, "alice", now=100.0 + i * 0.05)[1] for i in range(30)]
    assert not any(changes)


# --------------------------------------------------------------------------- releasing

def test_the_holder_can_release(r):
    claim(r, "alice")
    reply, changed = release(r, "alice")

    assert reply["holder"] is None
    assert changed is True
    assert "ligand" not in r["grabs"]


def test_releasing_frees_it_for_someone_else(r):
    claim(r, "alice")
    release(r, "alice")

    reply, _ = claim(r, "bob")
    assert reply["granted"] is True
    assert reply["holder"] == "bob"


def test_a_non_holder_cannot_release_someone_elses_grab(r):
    """Otherwise any peer can yank a molecule out of another person's hand."""
    claim(r, "alice", name="Alice")
    reply, changed = release(r, "bob")

    assert changed is False
    assert r["grabs"]["ligand"]["client"] == "alice"
    assert reply["holder"] == "alice"


def test_releasing_something_you_never_held_is_not_an_error(r):
    """It is the normal outcome of a race you lost; the client should not care."""
    reply, changed = release(r, "bob")
    assert reply["ok"] is True
    assert changed is False


# --------------------------------------------------------------------------- crashes

def test_a_hold_expires_when_nobody_refreshes_it(r):
    """A crashed tab must not hold a molecule until the server restarts."""
    claim(r, "alice", now=100.0)

    reply, _ = claim(r, "bob", now=100.0 + server.GRAB_TTL_SECONDS + 0.1)
    assert reply["granted"] is True
    assert reply["holder"] == "bob"


def test_a_hold_survives_right_up_to_its_deadline(r):
    """The lease must not be so eager that a brief stall steals the object."""
    claim(r, "alice", now=100.0)
    reply, _ = claim(r, "bob", now=100.0 + server.GRAB_TTL_SECONDS - 0.1)
    assert reply["granted"] is False


def test_expiry_does_not_disturb_other_objects(r):
    claim(r, "alice", obj="ligand", now=100.0)
    claim(r, "bob", obj="protein", now=103.0)

    server._expire_grabs(r, now=100.0 + server.GRAB_TTL_SECONDS + 0.1)

    assert "ligand" not in r["grabs"]
    assert r["grabs"]["protein"]["client"] == "bob"


# --------------------------------------------------------------------------- independence

def test_two_objects_can_be_held_by_two_people_at_once(r):
    """The lock is per object; it must not serialise the whole room."""
    a, _ = claim(r, "alice", obj="ligand")
    b, _ = claim(r, "bob", obj="protein")

    assert a["granted"] is True and b["granted"] is True


def test_rooms_created_before_grabs_existed_still_work():
    """An older room dict has no 'grabs' key; room() must not KeyError on it."""
    server.ROOMS["legacy"] = {"subs": [], "state": {}}
    got = server.room("legacy")

    assert got["grabs"] == {}
    server.ROOMS.pop("legacy", None)
