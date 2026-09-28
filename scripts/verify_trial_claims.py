#!/usr/bin/env python3
"""Re-ask ClinicalTrials.gov whether every trial the longevity panel cites still says what we claim.

scripts/verify_panel_citations.py does this for literature. This does it for the
registry, which drifts faster: a trial that was NOT_YET_RECRUITING when a record
was written starts recruiting, a status flips to TERMINATED, an age range is
amended. None of that edits itself in our panel, so a note reading "completed"
quietly becomes false while every identifier still resolves.

Three things are checked per record, all of them claims we actually make:

  the NCT id resolves at all -- an id that 404s is a citation to nothing;

  `pediatric_enrollment` against the registry's own stdAges. This flag decides
  which targets appear in pediatric_targets(), so getting it wrong silently
  changes what the panel says about children;

  a status word appearing in the note against overallStatus. 28 of the 46 notes
  assert a registry status in prose, and prose does not re-resolve.

A network failure is a FAILURE, not a skip. A claim that could not be checked
has not been verified, and reporting it as passing is the exact habit this
repository exists to avoid.

    .venv/bin/python scripts/verify_trial_claims.py
    .venv/bin/python scripts/verify_trial_claims.py --seed-bad   # prove it bites
    .venv/bin/python scripts/verify_trial_claims.py --nct NCT03895528
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))

import longevity_panel as lp  # noqa: E402

API = "https://clinicaltrials.gov/api/v2/studies"
FIELDS = ("protocolSection.identificationModule,protocolSection.statusModule,"
          "protocolSection.eligibilityModule")

# Status words a note may assert. Matched case-insensitively against the
# registry's overallStatus, with the registry's underscore form normalised, so
# "completed 1992" and "COMPLETED" agree.
STATUS_WORDS = ("NOT_YET_RECRUITING", "RECRUITING", "ACTIVE_NOT_RECRUITING",
                "APPROVED_FOR_MARKETING", "TERMINATED", "WITHDRAWN",
                "SUSPENDED", "UNKNOWN", "COMPLETED", "ENROLLING_BY_INVITATION")
# Longest first, and deliberately so. Alternation in `re` is first-match-wins,
# so listing RECRUITING before ACTIVE_NOT_RECRUITING makes "active, not
# recruiting" read as a claim of RECRUITING -- which is the opposite status.
# That false positive is exactly what this checker would otherwise report as
# drift, sending someone to "fix" a record that was already right.
# The separator also allows a comma, because prose writes "active, not
# recruiting" where the registry writes ACTIVE_NOT_RECRUITING.
_STATUS = re.compile(
    "|".join(w.replace("_", "[_, ]+")
             for w in sorted(STATUS_WORDS, key=len, reverse=True)),
    re.IGNORECASE)


def fetch(nct_id, timeout=30, attempts=3):
    """Fetch one study. Retries transient transport errors, never a 404.

    A dropped TLS connection is not evidence about a trial, and failing a
    correct record because of one turns the checker into noise people learn to
    ignore. A retry that still fails is still a failure, so "a claim that could
    not be checked has not been verified" still holds -- 404 is not retried at
    all, because the registry answered and its answer was "no such study".
    """
    url = f"{API}/{urllib.parse.quote(nct_id)}?fields={FIELDS}"
    req = urllib.request.Request(url, headers={"User-Agent": "agi-bioxr-verify/1.0"})
    last = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read()), None
        except urllib.error.HTTPError as exc:
            return None, f"HTTP {exc.code}"          # the registry answered
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            last = f"{type(exc).__name__}: {exc}"
            if attempt < attempts - 1:
                time.sleep(1.5 * (attempt + 1))
    return None, f"{last} (after {attempts} attempts)"


def asserted_status(note):
    """The registry status a note claims, normalised, or None."""
    if not note:
        return None
    found = _STATUS.search(note)
    if not found:
        return None
    # Collapse whatever separator the prose used back to the registry's form.
    return re.sub(r"[, ]+", "_", found.group(0).upper())


class Report:
    def __init__(self):
        self.rows = []

    def check(self, symbol, nct, kind, ok, detail=""):
        self.rows.append((symbol, nct, kind, ok, detail))
        mark = "ok  " if ok else "FAIL"
        print(f"  {mark} {nct}  {kind}{'  ' + detail if detail else ''}")

    @property
    def failures(self):
        return [r for r in self.rows if not r[3]]


def records(seed_bad=False, only=None):
    out = []
    for symbol, ev in sorted(lp.LONGEVITY_EVIDENCE.items()):
        for trial in ev.get("trials") or []:
            if only and trial["nct_id"] != only:
                continue
            out.append((symbol, dict(trial)))
    if seed_bad:
        # A real, resolvable trial carrying claims the registry contradicts:
        # a status that is not its status and a pediatric flag it does not have.
        # Both must be caught, or the checker cannot fail and proves nothing.
        out.append(("SEEDED", {"nct_id": "NCT00425607", "pediatric_enrollment": False,
                               "note": "seeded control: claimed RECRUITING"}))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed-bad", action="store_true",
                    help="add one deliberately wrong record; the run must fail")
    ap.add_argument("--nct", help="check a single NCT id")
    ap.add_argument("--delay", type=float, default=0.3,
                    help="seconds between requests (default: %(default)s)")
    args = ap.parse_args()

    rows = records(seed_bad=args.seed_bad, only=args.nct)
    if not rows:
        sys.exit(f"no trial records matched {args.nct!r}")

    print(f"checking {len(rows)} trial record(s) against {API}\n")
    report = Report()
    cache = {}

    for symbol, trial in rows:
        nct = trial["nct_id"]
        print(f"{symbol}")
        if nct not in cache:
            cache[nct] = fetch(nct)
            time.sleep(args.delay)
        data, err = cache[nct]

        if data is None:
            report.check(symbol, nct, "resolves", False, err or "no response")
            continue
        report.check(symbol, nct, "resolves", True)

        protocol = data.get("protocolSection", {})
        status = (protocol.get("statusModule") or {}).get("overallStatus")
        ages = (protocol.get("eligibilityModule") or {}).get("stdAges") or []

        claimed_pediatric = bool(trial.get("pediatric_enrollment"))
        registry_pediatric = "CHILD" in ages
        report.check(symbol, nct, "pediatric_enrollment",
                     claimed_pediatric == registry_pediatric,
                     f"panel={claimed_pediatric} registry={registry_pediatric} "
                     f"stdAges={ages or 'none'}")

        claimed_status = asserted_status(trial.get("note"))
        if claimed_status:
            report.check(symbol, nct, "status in note",
                         claimed_status == (status or "").upper(),
                         f"note says {claimed_status}, registry says {status}")

    failures = report.failures
    print(f"\n{len(report.rows) - len(failures)}/{len(report.rows)} checks passed")

    if args.seed_bad:
        seeded = [f for f in failures if f[0] == "SEEDED"]
        if not seeded:
            sys.exit("\nSEED FAILED: the deliberately wrong record passed. "
                     "This checker cannot fail and therefore proves nothing.")
        print(f"seeded control was caught ({len(seeded)} failure(s)) -- the checker bites")

    if failures:
        print(f"\n{len(failures)} failing check(s):")
        for symbol, nct, kind, _ok, detail in failures:
            print(f"  {symbol} {nct} {kind}: {detail}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
