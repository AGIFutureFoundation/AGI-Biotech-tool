"""The deployment image, checked as a file rather than by building it.

docs/investor-brief.html offers pharma "an agent-operable workspace behind
their own firewall". Until the Dockerfile existed there was no way to put it
there. These tests guard the properties of that file which would regress
silently -- a build still succeeds, the server still starts, and the thing that
broke is only visible to whoever gets breached or whoever cannot run the
benchmark.

Building the image is NOT done here. It needs a daemon, pulls ~3 GB of wheels
and takes several minutes, which is not a unit test. The build was verified by
hand when the file was written: 85 module imports pass inside the image, the
server answers 200 on / and /api/health, it runs as uid 10001, and Docker's
healthcheck reports healthy. What follows keeps the file from drifting away
from the thing that was verified.
"""
import pathlib
import re

import pytest

from conftest import REPO_ROOT

DOCKERFILE = pathlib.Path(REPO_ROOT) / "Dockerfile"
DOCKERIGNORE = pathlib.Path(REPO_ROOT) / ".dockerignore"

pytestmark = pytest.mark.skipif(not DOCKERFILE.exists(), reason="no Dockerfile")

DF = DOCKERFILE.read_text() if DOCKERFILE.exists() else ""
DI = DOCKERIGNORE.read_text() if DOCKERIGNORE.exists() else ""


def _directives(text, name):
    """Lines of one Dockerfile instruction, comments stripped."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#") or not s:
            continue
        if s.upper().startswith(name + " "):
            out.append(s[len(name):].strip())
    return out


# ------------------------------------------------------------------ security

def test_no_signing_secret_is_baked_into_the_image():
    """A default JWT_SECRET ships every deployment the same signing key.

    server/auth.py warns when it is unset and the warning says how to set it.
    An ENV here would silence that warning for everyone and hand every customer
    an identical key -- which is worse than the missing-secret state it looks
    like it fixes, because nothing complains.
    """
    for env in _directives(DF, "ENV"):
        key = env.split("=")[0].split()[0]
        assert key != "JWT_SECRET", f"the image bakes a signing key: {env}"
    assert "JWT_SECRET=" not in DF.replace("JWT_SECRET is deliberately not set", "")


def test_the_image_does_not_run_as_root():
    users = _directives(DF, "USER")
    assert users, "no USER directive; the container would run as root"
    assert users[-1] != "root" and not users[-1].startswith("0"), \
        f"final USER is {users[-1]!r}"


def test_the_key_directory_and_env_files_never_enter_the_build_context():
    """A build context is sent to the daemon whole and lands in the image.

    .keys/ holds the Ed25519 signing key this repository generates on first
    run. Copying a developer's key into a published image would give every
    deployment the author's identity.
    """
    for secret in (".keys", ".env"):
        assert any(line.strip() == secret or line.strip() == secret + "/"
                   for line in DI.splitlines()), \
            f"{secret} is not excluded by .dockerignore"
    assert "!.env.example" in DI, "the example env file should stay available"


# ------------------------------------------------------- it has to still work

def test_the_benchmark_structures_stay_in_the_build_context():
    """Excluding them would save 4.5 MB and break the offline benchmark.

    They were committed precisely so `node evals/redock.mjs` runs without the
    network. An image that has to reach the RCSB cannot run the benchmark in an
    air-gapped deployment, which is where the customers this image exists for
    would run it.
    """
    for line in DI.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith("!") or not s:
            continue
        assert not s.startswith("evals"), \
            f".dockerignore excludes {s!r}, which takes the cached structures with it"


def test_node_is_installed_because_half_the_suite_needs_it():
    """An image that cannot run `make jstest` cannot run the gate."""
    assert re.search(r"\bnodejs\b", DF), \
        "node is not installed; the JavaScript half of the test suite cannot run"


def test_the_venv_is_preserved_rather_than_flattened():
    """Every command in this repository is written as `.venv/bin/python`.

    The Makefile says why: the system interpreter has neither RDKit nor pytest,
    and several modules degrade quietly when an import fails, so the wrong
    interpreter produces a passing run that proves nothing. Flattening the venv
    into system Python would make the documented commands wrong inside the one
    place a customer runs them.
    """
    assert "venv" in DF, "no virtualenv created"
    assert ".venv/bin/python" in DF, "the entrypoint does not use the venv interpreter"


def test_the_server_binds_a_reachable_interface_in_the_container():
    """127.0.0.1 is right on a laptop and makes the container unreachable.

    A published port forwards to the container's own interface, so a server
    bound to loopback inside answers nothing from outside. This is not a
    loosening of the repository default: the isolation --host 127.0.0.1 gives on
    a laptop is given by the container boundary instead.
    """
    cmd = _directives(DF, "CMD")
    assert cmd, "no CMD; the image has no default process"
    assert "0.0.0.0" in cmd[-1], f"server would be unreachable from outside: {cmd[-1]}"


def test_the_default_host_in_the_repository_is_still_loopback():
    """The container's choice must not have been made by changing the app."""
    src = (pathlib.Path(REPO_ROOT) / "server" / "server.py").read_text()
    assert 'ap.add_argument("--host", default="127.0.0.1")' in src, \
        "the server's own default is no longer loopback"
