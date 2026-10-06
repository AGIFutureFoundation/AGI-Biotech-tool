"""No host may receive data from a user of this app without being written down.

The README tells people nothing leaves their machine except lookups they
trigger. Hospitals, nonprofits and companies all ask vendors to evidence exactly
that claim, and the honest answer for most projects is that nobody knows:
endpoints accumulate one convenience at a time, and the sentence in the README
becomes false without anyone deciding to make it false.

This makes the claim checkable. Adding an endpoint without declaring what it is
for and what is sent to it fails the build. That is a deliberate piece of
friction on the one change that is easiest to make thoughtlessly.
"""
import importlib.util
import pathlib

import pytest

from conftest import REPO_ROOT

SCRIPT = pathlib.Path(REPO_ROOT) / "scripts" / "check_egress.py"


@pytest.fixture(scope="module")
def egress():
    spec = importlib.util.spec_from_file_location("check_egress", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_host_in_the_source_is_declared(egress):
    """The gate itself. A new endpoint must come with an explanation."""
    undeclared = sorted(h for h in egress.found_hosts() if h not in egress.DECLARED)
    assert not undeclared, (
        "these hosts can receive data and are not declared in scripts/check_egress.py: "
        + ", ".join(undeclared))


def test_only_one_host_is_contacted_before_the_user_does_anything(egress):
    """Opening the page should tell almost nobody that you exist.

    Pinned as an exact set rather than a count, so adding a font CDN or an
    analytics snippet fails here and has to be argued for rather than noticed
    later by someone reading a network tab.
    """
    hits = egress.found_hosts()
    boot = {h for h, (when, _, _) in egress.DECLARED.items()
            if when == egress.BOOT and h in hits}
    assert boot == {"cdn.jsdelivr.net"}


def test_the_boot_host_is_honest_about_what_it_costs(egress):
    """three.js from a CDN is the weak point in 'runs locally'; say so."""
    _when, _purpose, sent = egress.DECLARED["cdn.jsdelivr.net"]
    assert "trusts whatever this CDN serves" in sent


def test_blockchain_endpoints_are_never_contacted_automatically(egress):
    """Wallets and chains are opt-in. Merely opening the app must not touch one."""
    for host in ("rpc.monad.xyz", "rpc.testnet.monad.xyz", "mcule.com"):
        when, _purpose, _sent = egress.DECLARED[host]
        assert when == egress.NEVER_AUTO, f"{host} is reachable without being configured"


def test_catalogue_entries_are_distinguished_from_real_calls(egress):
    """A directory listing a database is not a request to it.

    Conflating the two would make the inventory look alarming and, worse,
    untrustworthy: a reviewer who checks one entry and finds it is never called
    stops believing the whole table.
    """
    when, _purpose, sent = egress.DECLARED["scholar.google.com"]
    assert when == egress.CATALOGUE
    assert sent == "Nothing."


def test_every_declaration_says_what_is_sent(egress):
    """A host with no stated payload is a declaration that explains nothing."""
    for host, (when, purpose, sent) in egress.DECLARED.items():
        assert purpose.strip(), f"{host} has no stated purpose"
        assert sent.strip(), f"{host} does not say what is sent to it"
        assert when in (egress.BOOT, egress.TRIGGERED, egress.NEVER_AUTO,
                        egress.CATALOGUE), f"{host} has an unknown timing: {when!r}"


def test_the_table_renders_for_the_documentation(egress):
    """The docs quote this; it must not drift from the declarations."""
    table = egress.markdown(egress.found_hosts())
    assert table.startswith("| Host | When | What for | What is sent |")
    assert "`cdn.jsdelivr.net`" in table
    assert table.count("\n") >= len(egress.DECLARED)
