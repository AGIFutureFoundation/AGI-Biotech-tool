"""Starting and stopping the server should never look like a crash.

Both of these were real, and both were found by a person hitting them rather
than by anything in the suite:

  Starting a second copy on a busy port ended in a twelve-line traceback
  finishing `OSError: [Errno 48] Address already in use`. Everything needed to
  act on it -- what is holding the port, that it may be the server you already
  started, how to use another one -- was absent. The common case is that the
  thing holding the port is your own server, already serving the page you
  wanted, and the traceback reads as a failure.

  Ctrl+C printed a KeyboardInterrupt traceback. Under a supervisor the signal
  is SIGTERM, which was not handled at all, so the process died mid-request
  with the listening socket still open.

Note what is deliberately NOT done: SO_REUSEPORT is not set. HTTPServer already
sets SO_REUSEADDR, so a busy port is never a lingering TIME_WAIT socket -- it is
a live process, and letting a second server bind alongside it would split
traffic between two copies silently, which is worse than the error.
"""
import os
import pathlib
import signal
import socket
import subprocess
import sys
import time

import pytest

from conftest import REPO_ROOT

SERVER = pathlib.Path(REPO_ROOT) / "server" / "server.py"
PY = pathlib.Path(REPO_ROOT) / ".venv" / "bin" / "python"


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_listening(port, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as s:
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.2)
    return False


def _wait_gone(port, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as s:
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return True
        time.sleep(0.2)
    return False


@pytest.fixture(scope="module")
def server_module():
    import importlib
    return importlib.import_module("server")


# --------------------------------------------------------------------------- the message

def test_the_busy_port_message_leads_with_the_likely_cause(server_module):
    """Usually it is your own server, already serving the page you wanted."""
    msg = server_module._port_in_use_message("127.0.0.1", 8800)

    assert "already in use" in msg
    assert "you do not need to start it again" in msg
    assert "http://localhost:8800/" in msg


def test_the_message_offers_both_ways_out(server_module):
    msg = server_module._port_in_use_message("127.0.0.1", 8800)

    assert "pkill -f 'server/server.py --port 8800'" in msg
    assert "--port 8801" in msg          # the next port, not a placeholder


def test_the_message_survives_lsof_being_unavailable(server_module, monkeypatch):
    """lsof is not guaranteed, and a missing holder must not cost the advice."""
    monkeypatch.setattr(server_module, "_holder_of", lambda port: None)
    msg = server_module._port_in_use_message("127.0.0.1", 9999)

    assert "held by" not in msg
    assert "pkill" in msg                # still actionable


def test_the_holder_lookup_never_raises(server_module):
    """Returns a description or None; an unknown port must not blow up."""
    assert server_module._holder_of(_free_port()) is None


# --------------------------------------------------------------------------- starting

@pytest.mark.skipif(not PY.exists(), reason="venv interpreter not present")
def test_a_busy_port_explains_itself_instead_of_a_traceback():
    """The regression, end to end: start a server, then start another on it."""
    port = _free_port()
    first = subprocess.Popen([str(PY), str(SERVER), "--port", str(port)],
                             cwd=str(REPO_ROOT), stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    try:
        assert _wait_listening(port), "first server never came up"

        second = subprocess.run([str(PY), str(SERVER), "--port", str(port)],
                                cwd=str(REPO_ROOT), capture_output=True,
                                text=True, timeout=60)
        output = second.stdout + second.stderr

        assert second.returncode != 0
        assert "Traceback" not in output, f"still tracebacks:\n{output}"
        assert "Address already in use" not in output
        assert f"Port {port} is already in use" in output
    finally:
        first.terminate()
        first.wait(timeout=20)


# --------------------------------------------------------------------------- stopping

@pytest.mark.skipif(not PY.exists(), reason="venv interpreter not present")
@pytest.mark.parametrize("sig,name", [(signal.SIGINT, "SIGINT"), (signal.SIGTERM, "SIGTERM")])
def test_the_server_stops_cleanly_on_a_signal(sig, name):
    """SIGINT is Ctrl+C; SIGTERM is what pkill, systemd and Docker send."""
    port = _free_port()
    proc = subprocess.Popen([str(PY), str(SERVER), "--port", str(port)],
                            cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    try:
        assert _wait_listening(port), "server never came up"
        proc.send_signal(sig)
        out, _ = proc.communicate(timeout=30)

        assert "Traceback" not in out, f"{name} printed a traceback:\n{out}"
        assert f"stopping ({name})" in out
        assert "stopped" in out
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)


@pytest.mark.skipif(not PY.exists(), reason="venv interpreter not present")
def test_the_port_is_free_immediately_after_a_clean_stop():
    """server_close() releases the socket, so a restart does not race TIME_WAIT."""
    port = _free_port()
    proc = subprocess.Popen([str(PY), str(SERVER), "--port", str(port)],
                            cwd=str(REPO_ROOT), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    assert _wait_listening(port)
    proc.terminate()
    proc.wait(timeout=30)

    assert _wait_gone(port), "port still held after the process exited"

    again = subprocess.Popen([str(PY), str(SERVER), "--port", str(port)],
                             cwd=str(REPO_ROOT), stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    try:
        assert _wait_listening(port), "could not rebind the port straight away"
    finally:
        again.terminate()
        again.wait(timeout=20)


# --------------------------------------------------------------------------- not done on purpose

def test_so_reuseport_is_not_enabled():
    """Two servers must not be able to bind one port and split traffic.

    SO_REUSEADDR is already on (HTTPServer sets allow_reuse_address), which is
    why a busy port is always a live process rather than a stale socket. Adding
    SO_REUSEPORT would 'fix' the error by letting a second copy bind alongside
    the first, and requests would then land on whichever the kernel picked --
    a far worse failure than the one being fixed.
    """
    source = (pathlib.Path(REPO_ROOT) / "server" / "server.py").read_text()
    assert "SO_REUSEPORT" not in source
    assert "allow_reuse_port" not in source


# --------------------------------------------------------------------------- the secret

def test_the_jwt_warning_says_how_to_fix_it():
    """A warning that names a variable without showing how to set it is a riddle."""
    import importlib
    import warnings

    import auth

    os.environ.pop("JWT_SECRET", None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(auth)

    messages = [str(w.message) for w in caught]
    secret_warnings = [m for m in messages if "JWT_SECRET" in m]
    assert secret_warnings, "no JWT_SECRET warning was raised"
    assert "export JWT_SECRET=" in secret_warnings[0]


# --------------------------------------------------------------------------- exposure

def test_binding_beyond_loopback_says_so_at_the_moment_it_happens(server_module):
    """The argparse help mentions it; a person starting the server may not read it.

    Almost every /api route takes no token, so --host 0.0.0.0 puts the whole
    surface on the network. That is a reasonable thing to want for a headset,
    and an unreasonable thing to learn afterwards.
    """
    source = (pathlib.Path(REPO_ROOT) / "server" / "server.py").read_text()
    start = source.index('if a.host not in ("127.0.0.1"')
    block = source[start:start + 900]

    assert "requires no token" in block
    assert "127.0.0.1" in block and "localhost" in block and "::1" in block


def test_the_loopback_default_is_unchanged(server_module):
    """The warning is for the opt-in case; it must not become the default."""
    source = (pathlib.Path(REPO_ROOT) / "server" / "server.py").read_text()
    assert 'ap.add_argument("--host", default="127.0.0.1")' in source
