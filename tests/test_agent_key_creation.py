"""The signing key must be created privately, and exactly once.

Two defects in `if not exists: open(path, "w") ... chmod(0o600)`:

  The mode. open() creates 0o666 & ~umask, so 0o644 under the usual 022. The
  chmod lands after the bytes do, and in between any other local account can
  read the key.

  The race. The existence check is not a decision. Two first starts both see
  no file and both write one. The loser keeps a secret that never reached
  disk -- it signs happily until it restarts, loads the winner's key, and
  every signature it issued stops verifying. That failure appears long after
  the race, somewhere else, which is the worst property a bug can have.
"""
import base64
import importlib
import json
import os
import stat
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from conftest import REPO_ROOT

sys.path.insert(0, os.path.join(REPO_ROOT, "server"))


@pytest.fixture
def keydir(tmp_path, monkeypatch):
    """A fresh key directory, with a umask that exposes the mode defect."""
    d = tmp_path / ".keys"
    import agent_protocols as ap
    importlib.reload(ap)
    monkeypatch.setattr(ap, "KEYDIR", str(d))

    old = os.umask(0o022)          # the common default, and the one that bites
    yield d, ap
    os.umask(old)


# ------------------------------------------------------------------ the mode

def test_the_key_file_is_not_readable_by_other_accounts(keydir):
    d, ap = keydir
    ap.Identity()

    mode = os.stat(d / "agent_key.json").st_mode
    assert not mode & stat.S_IRGRP, "group can read the signing key"
    assert not mode & stat.S_IROTH, "every local account can read the signing key"
    assert stat.S_IMODE(mode) == 0o600


def test_the_key_directory_is_private_too(keydir):
    d, ap = keydir
    ap.Identity()

    mode = stat.S_IMODE(os.stat(d).st_mode)
    assert not mode & 0o077, f"key directory is {oct(mode)}"


def test_the_key_is_never_wider_than_0600_even_briefly(keydir, monkeypatch):
    """The window is what matters, so watch the mode at creation, not after.

    Checking st_mode at the end cannot see the defect: the chmod closes the
    window before the assertion runs. So record the mode the moment the file
    is first linked into place.
    """
    d, ap = keydir
    seen = {}
    real_link = os.link

    def watched_link(src, dst, *a, **kw):
        out = real_link(src, dst, *a, **kw)
        seen["mode"] = stat.S_IMODE(os.stat(dst).st_mode)
        return out

    real_open = os.open

    def watched_open(path, flags, mode=0o777, *a, **kw):
        fd = real_open(path, flags, mode, *a, **kw)
        if "agent_key" in str(path) and flags & os.O_CREAT:
            seen.setdefault("mode", stat.S_IMODE(os.stat(path).st_mode))
        return fd

    monkeypatch.setattr(os, "link", watched_link)
    monkeypatch.setattr(os, "open", watched_open)
    ap.Identity()

    assert seen, "the key file was not created through os.open/os.link"
    assert seen["mode"] == 0o600, \
        f"key existed at {oct(seen['mode'])} at creation time, before any chmod"


# ------------------------------------------------------------------ the race

def test_concurrent_first_starts_all_agree_on_one_key(keydir, monkeypatch):
    """Every winner and loser must hold the key that is actually on disk.

    The race has to be forced. Simply starting twelve threads is not a test:
    the window between the existence check and the write is microseconds wide,
    so against the defective version this passed on luck -- it reported "no
    race" about code that has one. A barrier holds every thread at the point
    where it has just seen no key file, and releases them together, so all
    twelve really are first starts.
    """
    d, ap = keydir
    N = 12
    barrier = threading.Barrier(N, timeout=10)
    real_exists = os.path.exists

    def exists_then_wait(path):
        found = real_exists(path)
        if str(path).endswith("agent_key.json") and not found:
            barrier.wait()          # everyone has now decided "it is not there"
        return found

    monkeypatch.setattr(ap.os.path, "exists", exists_then_wait)

    with ThreadPoolExecutor(max_workers=N) as pool:
        identities = list(pool.map(lambda _: ap.Identity(), range(N)))

    on_disk = base64.b64decode(json.loads((d / "agent_key.json").read_text())["secret"])
    mismatched = [i for i in identities if i.secret != on_disk]
    assert not mismatched, (
        f"{len(mismatched)} of {len(identities)} instances hold a secret that is not "
        "the one on disk; their signatures stop verifying after a restart")

    assert len({i.agent_id for i in identities}) == 1, "the service reported several agent ids"


def test_the_loser_adopts_the_winners_key_rather_than_its_own(keydir, monkeypatch):
    """Force the race deterministically: publish a key mid-creation."""
    d, ap = keydir

    rival = base64.b64encode(b"\x01" * 32).decode()
    real_link = os.link

    def link_after_rival(src, dst, *a, **kw):
        if not os.path.exists(dst):                    # the rival gets there first
            with open(dst, "w") as f:
                json.dump({"secret": rival, "created": "2020-01-01T00:00:00Z"}, f)
        return real_link(src, dst, *a, **kw)           # now raises FileExistsError

    monkeypatch.setattr(os, "link", link_after_rival)
    ident = ap.Identity()

    assert base64.b64encode(ident.secret).decode() == rival, \
        "kept its own secret after losing the race; the file says otherwise"


def test_no_temporary_key_file_is_left_behind(keydir):
    d, ap = keydir
    ap.Identity()

    leftovers = [p.name for p in d.iterdir() if p.name != "agent_key.json"]
    assert not leftovers, f"left key material lying around: {leftovers}"


# ------------------------------------------------------------------ unchanged

def test_an_existing_key_is_loaded_not_replaced(keydir):
    d, ap = keydir
    first = ap.Identity()
    second = ap.Identity()

    assert first.secret == second.secret
    assert first.created == second.created
    assert first.agent_id == second.agent_id
