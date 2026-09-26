"""A health check that says ok while the app is broken is worse than none.

The endpoint this replaces returned {"ok": true} whenever the process was
running. RDKit missing means no compound parsing, no descriptors, no depiction
-- and it still said ok. A probe wired to that reports green through a
deployment where most of the app does not work, which is how a health check
turns into the cause of an outage rather than the warning.

The tests below are mostly about the middle state. Up-or-down is easy; the
failure that actually happens is serving-but-crippled, and the whole value of
this module is refusing to call that ok.
"""
import pytest

import health


FULL = {"rdkit": True, "openmm": True, "pdbfixer": True, "pypdf": True, "bigquery": True}


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("BIODAO_ANCHOR_NETWORK", "MCULE_API_KEY", "BIODAO_VERSION"):
        monkeypatch.delenv(var, raising=False)


# --------------------------------------------------------------------------- the three states

def test_everything_present_is_ok():
    out = health.report(FULL)
    assert out["status"] == "ok"
    assert out["ok"] is True
    assert out["missing"] == {}


def test_a_missing_capability_is_degraded_not_ok():
    """The regression this module exists for."""
    out = health.report({**FULL, "rdkit": False})

    assert out["status"] == "degraded"
    assert out["ok"] is False
    assert out["serving"] is True


def test_degraded_names_what_stopped_working():
    """'rdkit: false' tells an operator at 3am nothing."""
    out = health.report({**FULL, "rdkit": False})
    impact = out["missing"]["rdkit"]["impact"]

    assert "Compounds cannot be parsed" in impact
    assert "Structure viewing still works" in impact      # and what still does


def test_several_missing_capabilities_are_all_listed():
    out = health.report({**FULL, "openmm": False, "pdbfixer": False})

    assert set(out["missing"]) == {"openmm", "pdbfixer"}
    assert "openmm" in out["summary"] and "pdbfixer" in out["summary"]


def test_an_empty_dependency_map_does_not_report_ok():
    """A caller that passes nothing must not accidentally look healthy."""
    assert health.report({})["status"] != "ok"


# --------------------------------------------------------------------------- probes

def test_a_degraded_instance_still_returns_200():
    """A degraded instance should stay in rotation; the operator reads `status`.

    Pulling it out would lose capacity during exactly the incident where
    capacity matters, so degradation is surfaced, not punished.
    """
    out = health.report({**FULL, "rdkit": False})
    assert health.status_code(out) == 200


def test_an_unavailable_instance_returns_503():
    out = dict(health.report(FULL))
    out["status"] = "unavailable"
    assert health.status_code(out) == 503


def test_the_legacy_ok_field_now_tracks_degradation():
    """Callers written against the old shape get a stricter, not looser, answer."""
    assert health.report(FULL)["ok"] is True
    assert health.report({**FULL, "pypdf": False})["ok"] is False


# --------------------------------------------------------------------------- posture

def test_synthetic_posture_is_reported_rather_than_guessed():
    """Unknown must read as unknown, not as 'no placeholders here'."""
    unknown = health.report(FULL, synthetic_active=None)
    assert unknown["posture"]["synthetic_values_active"] is None
    assert "Unknown" in unknown["posture"]["synthetic_note"]


def test_an_instance_emitting_placeholders_says_so():
    out = health.report(FULL, synthetic_active=True)
    note = out["posture"]["synthetic_note"]

    assert out["posture"]["synthetic_values_active"] is True
    assert "must not be reported as results" in note


def test_a_clean_instance_says_so_too():
    out = health.report(FULL, synthetic_active=False)
    assert "No placeholder values" in out["posture"]["synthetic_note"]


def test_anchoring_posture_defaults_to_off():
    posture = health.report(FULL)["posture"]
    assert posture["chain_anchoring_configured"] is False
    assert "No chain is contacted" in posture["anchoring_note"]


def test_configured_anchoring_still_promises_not_to_sign(monkeypatch):
    monkeypatch.setenv("BIODAO_ANCHOR_NETWORK", "monad-testnet")
    posture = health.report(FULL)["posture"]

    assert posture["chain_anchoring_configured"] is True
    assert "Nothing is ever signed or broadcast" in posture["anchoring_note"]


# --------------------------------------------------------------------------- the rest

def test_load_is_reported_for_capacity_planning():
    out = health.report(FULL, rooms=3, jobs=2)
    assert out["load"] == {"rooms": 3, "md_jobs": 2}


def test_uptime_and_version_are_present():
    out = health.report(FULL)
    assert out["uptime_seconds"] >= 0
    assert out["version"] == "unversioned"


def test_version_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv("BIODAO_VERSION", "2026.09.26")
    assert health.report(FULL)["version"] == "2026.09.26"


def test_the_synthetic_flag_tracks_the_process():
    """saw_synthetic() must reflect reality, or the posture is decoration."""
    import warnings

    import synthetic_provenance as sp
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", sp.SyntheticResultWarning)
        sp.SyntheticValue(1.0)
    assert sp.saw_synthetic() is True
