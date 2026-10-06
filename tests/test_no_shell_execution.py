"""No module in this repository may hand a string to a shell.

server/agents.py carried execute_bash_job(), whose docstring read "Execute a
bash command in a sandboxed environment". There was no sandbox:
subprocess.run(command, shell=True), one-hour timeout, running as whoever
started the server. Any string reaching it was arbitrary code execution.

Nothing called it, so it did no harm -- but the docstring was the hazard. An
agent framework is a place where somebody eventually wants "let the agent run a
job", and they would have found a helper that claims to be sandboxed and wired
it up. It was removed; this stops it coming back, in that file or any other.

shell=False with a list argv is fine and is what the repo uses elsewhere
(openssl for a dev certificate, lsof to name a port holder). The rule here is
narrow and specific: no shell=True, because that is the form where a string
becomes a command line.
"""
import ast
import pathlib

import pytest

from conftest import REPO_ROOT

SCAN_DIRS = ("server", "scripts", "tests")


def python_files():
    for directory in SCAN_DIRS:
        base = pathlib.Path(REPO_ROOT) / directory
        if base.is_dir():
            for path in sorted(base.rglob("*.py")):
                if "__pycache__" not in path.parts:
                    yield path


def shell_true_calls(path):
    """Every call in `path` passing shell=True, as (line, source) pairs."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                found.append((node.lineno, ast.unparse(node.func)))
    return found


@pytest.mark.parametrize("path", list(python_files()), ids=lambda p: str(p.name))
def test_no_shell_true(path):
    """Parsed, not grepped: a comment mentioning shell=True must not fail this."""
    offenders = shell_true_calls(path)
    assert not offenders, (
        f"{path.relative_to(REPO_ROOT)} passes shell=True: "
        + ", ".join(f"line {line} ({func})" for line, func in offenders)
        + ". Use a list argv with shell=False, or an allowlist.")


def test_the_removed_helper_has_not_returned():
    """By name, because a reintroduction would likely reuse it."""
    for path in python_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.name == "agents.py" or path.name == "test_no_shell_execution.py":
            continue                      # both explain the removal in prose
        assert "def execute_bash_job" not in text, \
            f"{path.relative_to(REPO_ROOT)} redefines execute_bash_job"


def test_the_check_can_fail(tmp_path):
    """A detector nobody has seen fail is a detector nobody should trust."""
    seeded = tmp_path / "seeded.py"
    seeded.write_text("import subprocess\nsubprocess.run(cmd, shell=True)\n")
    assert shell_true_calls(seeded) == [(2, "subprocess.run")]

    clean = tmp_path / "clean.py"
    clean.write_text("import subprocess\n# shell=True in a comment\n"
                     "subprocess.run(['ls'], shell=False)\n")
    assert shell_true_calls(clean) == []
