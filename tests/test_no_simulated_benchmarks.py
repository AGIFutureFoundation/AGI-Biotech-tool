"""No module may produce a performance number out of `sleep`.

server/load_testing.py ran its "workflow" as four
`await asyncio.sleep(random.uniform(...))` calls and then reported throughput,
success rate and a breaking point. Every one of those measured the event loop.
It was live, not dead: scripts/test_phase5_scaling.py called it and printed the
numbers. The whitepaper had to carry a paragraph warning readers not to believe
its own repository.

Deleting it fixes today. This stops it coming back, and stops the same shape
appearing somewhere new -- which is the realistic failure, because a sleep-based
harness is the easiest thing in the world to write when a real one is hard.

Why it was deleted rather than repaired: one real docking call is 2.4-6.5 s of
CPU-bound NumPy, so an asyncio concurrency harness over it would report a
different fiction rather than a measurement. Real throughput work needs process
parallelism and a fixed receptor set, and that is a project, not a patch.
"""
import ast
import os
import pathlib

import pytest

from conftest import REPO_ROOT

SOURCE_DIRS = ["server", "scripts"]

# Names of a COMPUTED RATE, which is the thing that cannot come from a sleep.
#
# The first version of this list held bare "throughput", and it was wrong twice
# in one run: it flagged agent_orchestrator.py for a task named
# 'high_throughput_dock' and performance_optimization.py for a docstring bullet
# reading "Async I/O for better throughput". Neither reports a figure. A check
# that cries wolf gets switched off, so the rule is now the per-unit-time forms
# only -- a name shaped like a measurement, not a word that appears near one.
PERF_WORDS = ("throughput_per_second", "ops_per_second", "operations_per_second",
              "requests_per_second", "workflows_per_hour", "per_second_rate",
              "breaking_point")


# Files where a sleep legitimately sits next to a rate name, each with the
# reason. An allowlist with a required reason is the honest mechanism: it makes
# adding one a deliberate act that a reviewer can read, rather than something
# achieved by quietly weakening the rule for everybody.
ALLOWED = {
    "test_production_hardening.py":
        "the sleeps are the measured durations fed to MetricsCollector, not a "
        "stand-in for work; the figure is the collector's arithmetic under test "
        "and the line that prints it says so",
}


def _python_files():
    for d in SOURCE_DIRS:
        root = pathlib.Path(REPO_ROOT) / d
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.py")):
            yield p


def test_the_sleep_based_load_harness_is_gone():
    assert not (pathlib.Path(REPO_ROOT) / "server" / "load_testing.py").exists(), \
        "server/load_testing.py is back; its throughput numbers measure asyncio.sleep"


def test_nothing_imports_it():
    """Imports and attribute access, not prose.

    A substring search over the file flagged this repository's own explanation
    of why the module was deleted -- the third time in this session a check has
    matched a comment about the defect instead of the defect.
    """
    for p in _python_files():
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for n in names:
                assert "load_testing" not in n, (
                    f"{p.relative_to(REPO_ROOT)}:{node.lineno} imports the deleted "
                    "sleep-based harness")


@pytest.mark.parametrize("path", list(_python_files()), ids=lambda p: p.name)
def test_no_module_sleeps_and_calls_the_result_a_measurement(path):
    """A file may sleep. A file may report throughput. Not both.

    Deliberately not a grep for `asyncio.sleep`: sleeping is legitimate --
    backoff, polling, rate limiting against a public API, all of which this
    repository does. What is never legitimate is standing in for the work and
    then reporting how fast the work was.
    """
    if path.name in ALLOWED:
        assert ALLOWED[path.name].strip(), f"{path.name} is exempt with no reason given"
        pytest.skip(f"allowed: {ALLOWED[path.name]}")

    src = path.read_text()
    tree = ast.parse(src)

    sleeps = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "attr", None) or getattr(fn, "id", None)
        if name == "sleep":
            sleeps.append(node.lineno)
    if not sleeps:
        return

    lowered = src.lower()
    reported = [w for w in PERF_WORDS if w in lowered]
    assert not reported, (
        f"{path.relative_to(REPO_ROOT)} calls sleep() at line(s) {sleeps} and also "
        f"reports {reported}. If the sleep stands in for the work, the figure is a "
        f"measurement of sleep. If it does not, rename the figure so a reader can "
        f"tell the difference.")


def test_the_whitepaper_no_longer_warns_about_its_own_harness():
    """The paragraph was honest. It should not need to exist any more."""
    wp = (pathlib.Path(REPO_ROOT) / "docs" / "WHITE_PAPER.md").read_text()
    assert "load_testing.py` still simulates" not in wp, \
        "the whitepaper still describes the harness as present"


def test_every_exemption_names_a_file_that_exists():
    """A stale allowlist entry is a hole nobody can see."""
    names = {p.name for p in _python_files()}
    for allowed in ALLOWED:
        assert allowed in names, (
            f"{allowed} is exempted but no longer exists; remove the entry so the "
            "allowlist cannot quietly cover a future file with the same name")
