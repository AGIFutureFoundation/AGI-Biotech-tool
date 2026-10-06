"""A seeded docking run must repeat exactly, or the benchmark cannot compare anything.

The re-docking benchmark scored 3/11, 5/11 and 6/11 on three consecutive runs
of identical code. Against that spread, a scoring change worth a case or two is
invisible: comparing two scoring functions unseeded means comparing two
different random walks and reading the difference as a result. I nearly did
exactly that -- baseline run 1 (3/11) against fixed run 1 (6/11) looks like a
doubled success rate and is pure noise.

Seeding removes that. Both arms see the same draws, so the difference that
remains is the change.

Requires network (RCSB) and node, and is skipped without either. It is a test
rather than an eval because determinism is a property of our own code: it does
not depend on what the registry says today, only on the arithmetic.
"""
import json
import pathlib
import shutil
import subprocess

import pytest

from conftest import REPO_ROOT

HARNESS = pathlib.Path(__file__).parent / "fixtures" / "seed_determinism.mjs"


@pytest.fixture(scope="module")
def result():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    proc = subprocess.run([node, str(HARNESS)], capture_output=True, text=True,
                          cwd=str(REPO_ROOT), timeout=600)
    if proc.returncode != 0:
        if "fetch failed" in proc.stderr or "ENOTFOUND" in proc.stderr:
            pytest.skip(f"RCSB unreachable: {proc.stderr.strip()[:120]}")
        pytest.fail(f"harness failed:\n{proc.stderr[-1500:]}")
    return proc.stdout


def test_the_same_seed_gives_the_same_poses(result):
    """The property the whole comparison rests on."""
    assert "seed 42 twice  : IDENTICAL" in result, result


def test_a_different_seed_gives_different_poses(result):
    """Otherwise the seed is ignored and every run is secretly the same one."""
    assert "seed 42 vs 43  : differ (good)" in result, result


def test_unseeded_runs_stay_random(result):
    """Seeding is opt-in. Ordinary docking must not become deterministic."""
    assert "unseeded twice : differ (good)" in result, result
