"""Shared fixtures and module discovery for the agi-bioxr test suite.

The production code under server/ imports its siblings by bare module name
(`from pyrene_apoptotic_discovery import ...`), so server/ and scripts/ must be
on sys.path for anything to import at all. That is done here once, rather than
in each test module.
"""
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SERVER_DIR = REPO_ROOT / "server"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Source directories, in the order the production code expects them.
SOURCE_DIRS = (SERVER_DIR, SCRIPTS_DIR)

for _d in SOURCE_DIRS:
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))


def discover_modules():
    """Every importable .py module under server/ and scripts/.

    Data-driven on purpose: a new module added to either directory is covered by
    the import regression test automatically, with nobody having to remember.

    Returns a list of (package_dir_name, module_name, path) tuples.
    """
    found = []
    for directory in SOURCE_DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.py")):
            if path.name.startswith("__"):
                continue
            found.append((directory.name, path.stem, path))
    return found


def module_ids():
    """Readable pytest parametrize ids like 'server/chem_extract.py'."""
    return [f"{d}/{p.name}" for d, _m, p in discover_modules()]
