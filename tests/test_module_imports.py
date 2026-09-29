"""Priority 1: the regression floor.

Every module under server/ and scripts/ must import cleanly. Nothing more.

This is deliberately the dumbest possible test, because it is the one that would
have caught the three shipped-but-broken modules (auth.py's missing dependency,
disease_panels.py's NameError, server.py's dead code) that eleven "COMPLETE"
markdown docs missed.

Each module is imported in a *subprocess*, for three reasons:
  1. Several modules under scripts/ have no `if __name__ == "__main__"` guard and
     execute a full demo at import time. In-process that pollutes every later
     test; in a subprocess it is contained.
  2. A module that calls sys.exit() or mutates global interpreter state cannot
     take the test runner down with it.
  3. Import order stays independent — no module can be accidentally "fixed" by
     another test having already imported its dependency.
"""
import subprocess
import sys

import pytest

from conftest import REPO_ROOT, SOURCE_DIRS, discover_modules, module_ids

# Generous: some unguarded scripts run a whole demo at import.
IMPORT_TIMEOUT_SECONDS = 120

MODULES = discover_modules()


def test_discovery_found_modules():
    """Guard the guard: if discovery silently returns nothing, every import test
    below would vacuously 'pass'."""
    assert len(MODULES) > 20, (
        f"Only discovered {len(MODULES)} modules under {[str(d) for d in SOURCE_DIRS]}; "
        "discovery is probably broken, which would make the import suite vacuous."
    )


@pytest.mark.parametrize("directory,module_name,path", MODULES, ids=module_ids())
def test_module_imports(directory, module_name, path):
    """`import <module>` must succeed with a zero exit status."""
    env_path = ":".join(str(d) for d in SOURCE_DIRS)
    result = subprocess.run(
        [sys.executable, "-c", f"import {module_name}"],
        cwd=str(REPO_ROOT),
        env={"PYTHONPATH": env_path, "PATH": "/usr/bin:/bin", "HOME": ""},
        capture_output=True,
        text=True,
        timeout=IMPORT_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        # Surface the real traceback tail, not just "non-zero exit".
        tail = "\n".join(result.stderr.strip().splitlines()[-12:])
        pytest.fail(
            f"`import {module_name}` failed (exit {result.returncode})\n"
            f"  file: {path}\n"
            f"--- stderr tail ---\n{tail}"
        )
