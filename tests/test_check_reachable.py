"""The reachability gate must still fail for genuinely dead code.

This check was changed to distinguish a module the app imports (REACHED) from
one only the test and eval suites import (STAGED) from one nothing imports at
all (DEAD). That change exists because two staged modules were being reported
as dead, and the only way to get a green tick was to wire an unfinished module
into the live app -- the opposite of what a gate against dead code should push
anyone toward.

A change like that is exactly how a gate quietly stops gating, so these pin the
teeth rather than the output: a file nothing imports must still fail the build,
and a file imported only by a test must not be silently ignored.
"""
import os
import shutil
import subprocess
import sys

import pytest

from conftest import REPO_ROOT

SCRIPT = os.path.join(REPO_ROOT, "scripts", "check_reachable.py")
PY_BIN = os.path.join(REPO_ROOT, ".venv", "bin", "python")


@pytest.fixture
def repo(tmp_path):
    """A miniature repo with the real script and a tiny js/ tree."""
    root = tmp_path / "repo"
    (root / "js").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "scripts").mkdir()
    shutil.copy(SCRIPT, root / "scripts" / "check_reachable.py")

    (root / "index.html").write_text('<script type="module" src="js/main.js"></script>')
    (root / "js" / "main.js").write_text("import { a } from './used.js';\nconsole.log(a);\n")
    (root / "js" / "used.js").write_text("export const a = 1;\n")
    return root


def run(root):
    r = subprocess.run([PY_BIN, str(root / "scripts" / "check_reachable.py")],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


# ------------------------------------------------------------------ the teeth

def test_a_module_nothing_imports_fails_the_build(repo):
    (repo / "js" / "orphan.js").write_text("export const dead = 1;\n")

    code, out = run(repo)
    assert code == 1, f"a module nothing imports did not fail the gate:\n{out}"
    assert "DEAD" in out and "orphan.js" in out


def test_a_module_imported_only_by_a_test_does_not_fail_the_build(repo):
    (repo / "js" / "staged.js").write_text("export const s = 1;\n")
    (repo / "tests" / "staged.test.mjs").write_text(
        "import { s } from '../js/staged.js';\nconsole.log(s);\n")

    code, out = run(repo)
    assert code == 0, f"a tested module was treated as dead:\n{out}"
    assert "STAGED" in out and "staged.js" in out


def test_a_staged_module_is_never_silent(repo):
    """Staged is a holding state. Unreported, it becomes a hiding place."""
    (repo / "js" / "staged.js").write_text("export const s = 1;\n")
    (repo / "tests" / "staged.test.mjs").write_text("import '../js/staged.js';\n")

    _, out = run(repo)
    assert "staged.js" in out, "a staged module vanished from the report"


def test_dead_and_staged_are_told_apart_in_the_same_run(repo):
    (repo / "js" / "staged.js").write_text("export const s = 1;\n")
    (repo / "js" / "orphan.js").write_text("export const d = 1;\n")
    (repo / "tests" / "staged.test.mjs").write_text("import '../js/staged.js';\n")

    code, out = run(repo)
    assert code == 1, "the dead module should still fail even beside a staged one"
    staged_line = next(l for l in out.splitlines() if "staged.js" in l)
    dead_line = next(l for l in out.splitlines() if "orphan.js" in l)
    assert "STAGED" in staged_line and "DEAD" in dead_line


def test_an_import_of_a_file_that_does_not_exist_still_fails(repo):
    (repo / "js" / "main.js").write_text("import './ghost.js';\n")

    code, out = run(repo)
    assert code == 1
    assert "MISSING" in out and "ghost.js" in out


# ------------------------------------------------------- what counts as staged

def test_a_dynamic_import_from_an_eval_harness_counts(repo):
    """evals/calibrate.mjs reaches its module with `await import(...)`."""
    (repo / "evals").mkdir()
    (repo / "js" / "staged.js").write_text("export const s = 1;\n")
    (repo / "evals" / "calibrate.mjs").write_text(
        "const { s } = await import('../js/staged.js');\n")

    code, out = run(repo)
    assert code == 0, f"a dynamically imported module was called dead:\n{out}"
    assert "STAGED" in out


def test_what_a_staged_module_imports_is_staged_too(repo):
    """Transitively: a helper only a staged module needs is not dead either."""
    (repo / "js" / "staged.js").write_text("import './helper.js';\nexport const s = 1;\n")
    (repo / "js" / "helper.js").write_text("export const h = 1;\n")
    (repo / "tests" / "staged.test.mjs").write_text("import '../js/staged.js';\n")

    code, out = run(repo)
    assert code == 0, f"a staged module's own import was called dead:\n{out}"


def test_an_app_module_is_not_downgraded_to_staged_by_also_having_a_test(repo):
    """used.js is in the app AND tested; it must stay plain reachable."""
    (repo / "tests" / "used.test.mjs").write_text("import '../js/used.js';\n")

    code, out = run(repo)
    assert code == 0
    assert "STAGED" not in out, f"an app module was reported as staged:\n{out}"
