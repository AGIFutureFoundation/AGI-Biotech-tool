"""What state is this instance actually in?

The previous health endpoint returned ``{"ok": true}`` whenever the process was
running, alongside a set of dependency flags nobody interpreted. That is the
shape of health check that causes outages rather than catching them: RDKit
missing means no compound parsing, no descriptors and no depiction, and the
endpoint said ok. A probe wired to it would report green through a deployment
where most of the app did not work.

So this distinguishes three states, and the middle one is the point:

  ok          everything a caller might reasonably expect is present
  degraded    the process is up and serving, but a named capability is gone
  unavailable something required to do anything useful is missing

DEGRADED IS NOT OK. A load balancer may keep sending traffic to a degraded
instance -- that is a reasonable policy and the payload supports it -- but the
operator has to be able to see it, and `status` must never say ok while
something is broken. Each missing dependency names what stops working, because
"rdkit: false" tells an operator at 3am nothing at all.

It also reports posture rather than only liveness: whether this instance is
emitting synthetic placeholder values, and whether chain anchoring is
configured. Both change how output should be read, and neither is visible from
the outside otherwise.
"""
import datetime as _dt
import os
import time

SCHEMA_VERSION = "1.0"

STARTED_AT = time.time()

#: dependency -> (what it enables, what is lost without it, required?)
#:
#: "Required" means the app cannot do its core job -- load a structure and show
#: it. Everything else degrades a feature without stopping the product.
DEPENDENCIES = {
    "rdkit": ("compound parsing, descriptors, 2D depiction, SMILES repair",
              "Compounds cannot be parsed or drawn. Structure viewing still works.",
              False),
    "openmm": ("molecular dynamics",
               "MD cannot run. Docking and scoring are unaffected.", False),
    "pdbfixer": ("structure preparation for MD",
                 "MD cannot prepare a receptor, so MD is unavailable.", False),
    "pypdf": ("PDF ingestion for the compound inventory",
              "Compound collections cannot be imported from PDF.", False),
    "bigquery": ("AlphaFold metadata queries over BigQuery",
                 "That one query path is unavailable; every other source still works.",
                 False),
}


def _uptime():
    return round(time.time() - STARTED_AT, 1)


def report(have, rooms=0, jobs=0, synthetic_active=None, version=None):
    """Assemble the health payload.

    `have` is the server's dependency map. `synthetic_active` says whether this
    instance is currently producing placeholder values; None means unknown,
    which is reported as unknown rather than guessed either way.
    """
    missing, degraded_by = {}, []
    for name, (enables, lost, required) in DEPENDENCIES.items():
        if have.get(name):
            continue
        missing[name] = {"enables": enables, "impact": lost, "required": required}
        degraded_by.append(name)

    required_missing = [n for n in degraded_by if DEPENDENCIES[n][2]]

    if required_missing:
        status = "unavailable"
        summary = ("Missing a required dependency: "
                   + ", ".join(sorted(required_missing)) + ".")
    elif degraded_by:
        status = "degraded"
        summary = (f"Serving, but {len(degraded_by)} capabilit"
                   f"{'y is' if len(degraded_by) == 1 else 'ies are'} unavailable: "
                   + ", ".join(sorted(degraded_by)) + ".")
    else:
        status = "ok"
        summary = "All optional capabilities present."

    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        # Kept for callers that predate this shape, but it now means what it
        # says: false as soon as anything is degraded, rather than tracking
        # only whether the process is alive.
        "ok": status == "ok",
        "serving": status != "unavailable",
        "summary": summary,
        "uptime_seconds": _uptime(),
        "checked_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "version": version or os.environ.get("BIODAO_VERSION") or "unversioned",
        "capabilities": {name: bool(have.get(name)) for name in DEPENDENCIES},
        "missing": missing,
        "load": {"rooms": rooms, "md_jobs": jobs},
        "posture": _posture(synthetic_active),
    }
    return payload


def _posture(synthetic_active):
    """Facts that change how this instance's output should be read."""
    anchoring = bool(os.environ.get("BIODAO_ANCHOR_NETWORK"))
    return {
        "synthetic_values_active": synthetic_active,
        "synthetic_note": (
            "Unknown: this instance has not been asked to produce a result yet."
            if synthetic_active is None else
            "This instance is emitting placeholder values; they print with a "
            "[SYNTHETIC] marker and must not be reported as results."
            if synthetic_active else
            "No placeholder values have been produced by this instance."),
        "chain_anchoring_configured": anchoring,
        "anchoring_note": (
            "Anchoring is configured. Nothing is ever signed or broadcast by this "
            "server; it only prepares unsigned transactions."
            if anchoring else
            "Not configured. No chain is contacted."),
        "price_providers_configured": bool(os.environ.get("MCULE_API_KEY")),
    }


def status_code(payload):
    """HTTP status for a probe.

    503 only when the instance genuinely cannot serve. A degraded instance
    returns 200 so a load balancer keeps it in rotation -- the operator learns
    about it from `status`, not by losing capacity during an incident.
    """
    return 503 if payload["status"] == "unavailable" else 200
