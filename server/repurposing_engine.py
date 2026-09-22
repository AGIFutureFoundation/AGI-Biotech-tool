"""Ranked, attributable drug-repurposing hypotheses from the platform's live sources.

This is deliberately not server/molecular_research_pipeline.py, whose
`DrugRepurposingEngine` returns random() and is labelled [SYNTHETIC]. Every
number here traces to a record in ChEMBL, Open Targets, Reactome, STRING or
ClinicalTrials.gov, and every hypothesis carries the identifiers to check it.

Scoring
-------
A hypothesis' score is the **sum of its listed terms, after per-join caps**.
There is no hidden model and no learned weight. SCORING below is the entire
scheme; it is emitted with every report so a reader can disagree with a weight
and re-add the terms by hand. The number is evidence points, ordinal only: it is
not a probability, not an effect size, and a 6.0 is not "twice as likely" as a
3.0. Its only job is to order a worklist.

Two boundaries this module enforces rather than documents
---------------------------------------------------------
* **No dose is ever computed.** `documented_doses()` retrieves dose text
  verbatim from ClinicalTrials.gov records and attaches the NCT id it came from.
  Nothing in this file multiplies, scales, extrapolates or allometrically
  converts a dose, and nothing infers a paediatric dose from an adult one. Dose
  selection needs PK/PD modelling this platform does not have.
* **Combinations are flagged, never asserted.** Two compounds hitting
  complementary targets is a reason to run an experiment. Synergy, antagonism and
  shared toxicity cannot be read off target annotations. `cotarget_flags()`
  returns questions, and says so in every record it emits.
"""
from __future__ import annotations

import datetime as _dt

import db_clients as db
import opentargets_clinical as otc
import repurposing_joins as joins

SCHEMA_VERSION = "1.0"

# --------------------------------------------------------------------------- the scoring scheme

SCORING = {
    "description": "Additive evidence points. Score = sum of terms after per-join caps. "
                   "Ordinal worklist ordering only; not a probability or an effect size.",
    "mechanism": {
        "rationale": "Another drug reaching a clinical stage against the same target is the "
                     "strongest non-trivial evidence that the target is addressable in that disease.",
        "precedent_stage_points": {
            "APPROVAL": 4.0, "PHASE_4": 4.0, "PHASE_3": 3.0, "PHASE_2_3": 2.5,
            "PHASE_2": 2.0, "PHASE_1_2": 1.2, "PHASE_1": 1.0, "EARLY_PHASE_1": 0.6,
            "PHASE_0": 0.6, "UNKNOWN": 0.3,
        },
        "specificity_factor_by_distinct_drugs": {"1": 0.6, "2": 1.0, "3+": 1.2},
        "specificity_rationale":
            "Open Targets lists a drug's *entire* clinical footprint against a target, not the "
            "part attributable to that target. Dipyridamole carries a PDE5A mechanism and also "
            "carries stroke and thrombophlebitis from its antiplatelet use, which has nothing to "
            "do with PDE5A. One drug is therefore weak evidence and gets 0.6x; independent "
            "convergence of two or more drugs on the same target and the same disease is what "
            "makes it evidence, and gets 1.0-1.2x.",
        "action_type_match": 0.5,
        "action_type_opposed": -1.0,
        "complex_component_multiplier": 0.5,
    },
    "structure": {
        "rationale": "A close structural analogue that is an approved drug transfers a prior "
                     "about target engagement, not about efficacy.",
        "metric": f"{joins.SIMILARITY_METRIC} on {joins.FINGERPRINT}",
        "tiers": [[0.85, 2.0], [0.70, 1.2], [0.55, 0.6], [joins.SIMILARITY_FLOOR, 0.25]],
        "cap": 2.0,
    },
    "network": {
        "rationale": "Pathway co-membership and protein interaction connect a compound's target "
                     "to a different disease protein. Genuinely non-obvious and genuinely "
                     "false-positive-prone, so capped below the threshold a hypothesis needs "
                     "to be taken seriously on its own.",
        "reactome_pathway": 0.5,
        "string_high": 0.5,
        "string_medium": 0.25,
        "cap": 1.5,
    },
    "polypharmacology": {
        "rationale": "Two different targets of the same compound independently showing clinical "
                     "precedent for the same disease. Convergence, not promiscuity.",
        "convergent_target_bonus": 1.0,
        "cap": 2.0,
    },
}

# A hypothesis supported only by network terms gets this label however it scores.
SPECULATIVE_CEILING = SCORING["network"]["cap"]


def _mechanism_terms(items):
    """Score one disease's mechanism evidence. Returns (points, terms)."""
    cfg = SCORING["mechanism"]
    terms, drugs_seen, targets_seen = [], set(), set()

    for i in items:
        drugs_seen.add(i["drug_chembl_id"])
        # Keyed on the ChEMBL *target*, not the gene. Keying on the gene counts
        # every subunit of a complex as an independent target and turns one piece
        # of evidence into a 49-fold convergence bonus.
        targets_seen.add(i["target_chembl_id"])

    best = max(items, key=lambda i: i["rank"])
    base = cfg["precedent_stage_points"].get(best["stage"], 0.3)
    n_drugs = len(drugs_seen)
    factor = 0.6 if n_drugs == 1 else (1.0 if n_drugs == 2 else 1.2)

    points = base * factor
    if best.get("is_complex_component"):
        points *= cfg["complex_component_multiplier"]

    terms.append(joins.term(
        "mechanism", "target_precedent",
        f"{best['drug']} ({best['drug_chembl_id']}), which acts on {best['target_symbol']}, "
        f"reached {best['stage']} for this indication.",
        "Open Targets (drugAndClinicalCandidates + drug indications), ChEMBL mechanisms",
        refs={"drug_chembl_id": best["drug_chembl_id"], "target_symbol": best["target_symbol"],
              "ensembl": best["ensembl"], "target_chembl_id": best["target_chembl_id"],
              "stage": best["stage"]},
        points=round(base, 3),
        stage_base_points=round(base, 3)))

    names = sorted({i["drug"] for i in items if i["drug"]})[:6]
    delta = points - base
    if n_drugs == 1:
        terms.append(joins.term(
            "mechanism", "single_precedent_discount",
            f"Only one drug against {best['target_symbol']} has any clinical record for this "
            f"indication, so the stage points are multiplied by {factor}.",
            "Open Targets",
            refs={"distinct_drugs": n_drugs, "drug_chembl_ids": sorted(drugs_seen),
                  "specificity_factor": factor},
            caveat="A drug's indication list is its whole clinical footprint, not the part its "
                   "action on this target is responsible for. With a single precedent there is "
                   "nothing to distinguish a real target effect from an unrelated one.",
            points=round(delta, 3)))
    else:
        terms.append(joins.term(
            "mechanism", "convergent_drugs",
            f"{n_drugs} distinct drugs against {best['target_symbol']} have clinical records for "
            f"this indication ({', '.join(n for n in names if n)}); stage points are multiplied "
            f"by {factor}.",
            "Open Targets",
            refs={"distinct_drugs": n_drugs, "drug_chembl_ids": sorted(drugs_seen),
                  "specificity_factor": factor},
            points=round(delta, 3)))

    if best.get("is_complex_component"):
        terms.append(joins.term(
            "mechanism", "complex_component_discount",
            f"{best['target_symbol']} is one component of the protein complex the mechanism is "
            f"annotated against, not necessarily the pharmacological target; points halved.",
            "ChEMBL target components",
            refs={"target_chembl_id": best["target_chembl_id"]},
            points=round(points - (base * factor), 3)))

    q_actions = {i["query_action_type"] for i in items if i.get("query_action_type")}
    p_actions = {i["precedent_action_type"] for i in items if i.get("precedent_action_type")}
    if q_actions and p_actions:
        if q_actions & p_actions:
            points += cfg["action_type_match"]
            terms.append(joins.term(
                "mechanism", "action_type_match",
                f"The query compound and the precedent act on the target the same way "
                f"({sorted(q_actions & p_actions)[0]}).",
                "ChEMBL mechanism action_type",
                refs={"query_action": sorted(q_actions), "precedent_action": sorted(p_actions)},
                points=cfg["action_type_match"]))
        elif {"INHIBITOR", "ANTAGONIST", "BLOCKER"} & q_actions and \
                {"AGONIST", "ACTIVATOR", "OPENER"} & p_actions or \
                {"AGONIST", "ACTIVATOR", "OPENER"} & q_actions and \
                {"INHIBITOR", "ANTAGONIST", "BLOCKER"} & p_actions:
            points += cfg["action_type_opposed"]
            terms.append(joins.term(
                "mechanism", "action_type_opposed",
                "The query compound modulates this target in the opposite direction to the "
                "precedent drug, so the precedent argues against this hypothesis.",
                "ChEMBL mechanism action_type",
                refs={"query_action": sorted(q_actions), "precedent_action": sorted(p_actions)},
                points=cfg["action_type_opposed"]))

    if len(targets_seen) > 1:
        cfgp = SCORING["polypharmacology"]
        bonus = min((len(targets_seen) - 1) * cfgp["convergent_target_bonus"], cfgp["cap"])
        points += bonus
        terms.append(joins.term(
            "polypharmacology", "convergent_targets",
            f"{len(targets_seen)} distinct annotated targets of this compound independently carry "
            f"clinical precedent for this indication "
            f"({', '.join(sorted({i['target_symbol'] for i in items if i['target_symbol']})[:8])}).",
            "ChEMBL mechanisms + Open Targets",
            refs={"target_chembl_ids": sorted(targets_seen)},
            points=round(bonus, 3)))
    return points, terms


def _structure_terms(items):
    cfg = SCORING["structure"]
    best = max(items, key=lambda i: i["tanimoto"])
    points = 0.0
    for floor, value in cfg["tiers"]:
        if best["tanimoto"] >= floor:
            points = value
            break
    if not points:
        return 0.0, []
    t = joins.term(
        "structure", "approved_analogue",
        f"{best['analogue']} ({best['analogue_chembl_id']}), an approved drug, is "
        f"{best['tanimoto']:.2f} {joins.SIMILARITY_METRIC}-similar to the query compound on "
        f"{joins.FINGERPRINT}, and reached {best['stage']} for this indication.",
        "ChEMBL similarity search (candidate generation) + RDKit (similarity recomputed locally) "
        "+ Open Targets (indication stage)",
        refs={"analogue_chembl_id": best["analogue_chembl_id"], "tanimoto": best["tanimoto"],
              "stage": best["stage"], "analogue_mechanisms": best.get("analogue_targets")},
        caveat="Structural similarity predicts target engagement at best, never efficacy. "
               f"Below ~0.85 {joins.SIMILARITY_METRIC} even shared target activity is a weak prior.",
        points=round(min(points, cfg["cap"]), 3))
    out = [t]
    if best["tanimoto"] >= 0.90:
        out.append(joins.term(
            "structure", "near_identical_analogue",
            f"At {best['tanimoto']:.2f} the analogue is nearly the same molecule by this "
            "fingerprint. Check whether the difference is a stereocentre, a salt or an isotope "
            "before treating this as a repurposing hypothesis rather than a duplicate record.",
            "RDKit", refs={"analogue_chembl_id": best["analogue_chembl_id"]},
            caveat="Fingerprints compress; two molecules this close may still differ in the way "
                   "that matters. Diastereomers are the usual case.",
            points=0.0))
    return min(points, cfg["cap"]), out


def _network_terms(items):
    cfg = SCORING["network"]
    points, terms = 0.0, []
    for item in items:
        if item["kind"] == "reactome_pathway":
            value = cfg["reactome_pathway"]
            statement = (f"{item['compound_target']} and the disease-panel target "
                         f"{item['panel_target']} are both participants in the Reactome pathway "
                         f"'{item['pathway']}' ({item['pathway_id']}).")
            source = "Reactome"
        else:
            value = cfg["string_high"] if item["confidence"] == "high" else cfg["string_medium"]
            statement = (f"{item['compound_target']} and the disease-panel target "
                         f"{item['panel_target']} interact in STRING with combined score "
                         f"{item['score']} ({item['confidence']} confidence).")
            source = "STRING"
        points += value
        terms.append(joins.term(
            "network", item["kind"], statement, source, refs=item,
            caveat="Two different proteins. Pathway co-membership and interaction are not "
                   "mechanism: this connects a compound to a disease without any evidence that "
                   "modulating one protein moves the other.",
            points=value))
    if points > cfg["cap"]:
        scale = cfg["cap"] / points
        for t in terms:
            t["points"] = round(t["points"] * scale, 3)
            t["capped"] = True
        points = cfg["cap"]
    return points, terms


def _status(disease_id, own_indications):
    row = own_indications.get(disease_id)
    if row is None:
        return "novel", None
    if row["stage"] in otc.APPROVED_STAGES:
        return "approved_indication", row
    return "under_investigation", row


def generate_hypotheses(smiles=None, name=None, chembl_id=None, inchikey=None, label=None,
                        panels_module=None, exclude_self=True, include_network=True,
                        min_score=0.0, limit=25, blind_disease_ids=None):
    """Rank repurposing hypotheses for one compound.

    `exclude_self=True` (the default, and what every evaluation uses) removes the
    compound and its salt family from the precedent set, so a hypothesis can never
    be supported by the compound's own clinical record. Without it an approved
    drug trivially "predicts" its own label.

    `blind_disease_ids` exists for the retrospective evaluation in
    scripts/validate_repurposing_recall.py and for nothing else. It hides the
    compound's own record for those diseases so an already-approved second
    indication is not filtered out as known, reconstructing the state of
    knowledge before the repurposing was found. It changes *which* hypotheses are
    returned, never their scores: the evidence was already self-excluded.

    Returns a report dict: identity, scoring scheme, ranked hypotheses, the
    compound's existing indications, diagnostics, and the boundary notices.
    """
    blind = set(blind_disease_ids or ())
    identity = joins.resolve_compound(smiles=smiles, name=name, chembl_id=chembl_id,
                                      inchikey=inchikey, label=label)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "compound": {k: identity[k] for k in
                     ("label", "chembl_id", "name", "smiles", "inchikey", "max_phase", "family")},
        "targets": identity["targets"],
        "mechanisms": identity["mechanisms"],
        "notes": identity["notes"],
        "scoring": SCORING,
        "settings": {"exclude_self": exclude_self, "include_network": include_network,
                     "min_score": min_score, "blinded_disease_ids": sorted(blind)},
        "boundaries": BOUNDARIES,
        "hypotheses": [], "existing_indications": [], "diagnostics": {},
    }
    if identity.get("error"):
        report["error"] = identity["error"]
        return report

    if blind:
        hidden = {k: v for k, v in identity["own_indications"].items() if k in blind}
        identity["own_indications"] = {k: v for k, v in identity["own_indications"].items()
                                       if k not in blind}
        report["blinded"] = [{"disease_id": k, "disease": v["disease"],
                              "actual_stage_hidden": v["stage"]} for k, v in hidden.items()]

    report["existing_indications"] = sorted(
        ({"disease_id": k, "disease": v["disease"], "stage": v["stage"]}
         for k, v in identity["own_indications"].items()),
        key=lambda r: (-otc.PHASE_RANK.get(r["stage"], 0), r["disease"] or ""))

    mech, mech_diag = joins.mechanism_join(identity, exclude_self=exclude_self)
    struct, struct_diag = joins.structure_join(identity)
    net, net_diag = ({}, {"skipped": True})
    if include_network and panels_module is not None:
        net, net_diag = joins.network_join(identity, panels_module)
    report["diagnostics"] = {"mechanism": mech_diag, "structure": struct_diag, "network": net_diag}

    pool = {}
    for dis_id, block in mech.items():
        points, terms = _mechanism_terms(block["items"])
        pool.setdefault(dis_id, {"disease": block["disease"], "points": 0.0, "terms": [],
                                 "by_join": {}})
        pool[dis_id]["points"] += points
        pool[dis_id]["terms"] += terms
    for dis_id, block in struct.items():
        points, terms = _structure_terms(block["items"])
        if not terms:
            continue
        pool.setdefault(dis_id, {"disease": block["disease"], "points": 0.0, "terms": [],
                                 "by_join": {}})
        pool[dis_id]["points"] += points
        pool[dis_id]["terms"] += terms
    for key, block in net.items():
        points, terms = _network_terms(block["items"])
        entry = pool.setdefault(key, {"disease": block["disease"], "points": 0.0, "terms": [],
                                      "by_join": {}})
        entry["points"] += points
        entry["terms"] += terms
        entry["panel"] = block.get("panel")
        entry["panel_target"] = block.get("panel_target")
        entry["pediatric_onset"] = block.get("pediatric_onset")
        entry["unmet_need"] = block.get("unmet_need")

    hypotheses, existing = [], []
    for dis_id, entry in pool.items():
        by_join = {}
        for t in entry["terms"]:
            by_join[t["join"]] = round(by_join.get(t["join"], 0.0) + t.get("points", 0.0), 3)
        status, own = _status(dis_id, identity["own_indications"])
        joins_used = sorted(by_join)
        record = {
            "disease_id": dis_id, "disease": entry["disease"], "status": status,
            "score": round(entry["points"], 3), "score_by_join": by_join,
            "joins": joins_used, "terms": sorted(entry["terms"],
                                                 key=lambda t: -t.get("points", 0.0)),
            "compound": identity.get("name") or identity.get("label"),
            "compound_chembl_id": identity.get("chembl_id"),
        }
        for extra in ("panel", "panel_target", "pediatric_onset", "unmet_need"):
            if entry.get(extra) is not None:
                record[extra] = entry[extra]
        if joins_used == ["network"]:
            record["confidence_label"] = "speculative"
            record["confidence_note"] = (
                "Supported only by pathway/interaction proximity between two different proteins. "
                "No compound in this disease has been shown to act through the query compound's "
                "target. Treat as an experiment to design, not a lead.")
        elif "mechanism" in joins_used:
            record["confidence_label"] = "mechanism-backed"
        else:
            record["confidence_label"] = "structure-only"
            record["confidence_note"] = (
                "No shared-target clinical precedent; the only link is chemical resemblance to an "
                "approved drug. Confirm target engagement before anything else.")
        if own is not None:
            record["existing_record"] = {"stage": own["stage"], "disease": own["disease"],
                                         "source": "Open Targets drug indications"}
        if status == "approved_indication":
            existing.append(record)
        else:
            hypotheses.append(record)

    hypotheses.sort(key=lambda h: (-h["score"], h["disease"] or ""))
    report["hypotheses"] = [h for h in hypotheses if h["score"] >= min_score][:limit]
    report["suppressed_because_already_approved"] = sorted(
        ({"disease_id": r["disease_id"], "disease": r["disease"], "score": r["score"]}
         for r in existing), key=lambda r: -r["score"])[:limit]
    report["counts"] = {
        "candidate_diseases": len(pool),
        "hypotheses_returned": len(report["hypotheses"]),
        "already_approved_suppressed": len(existing),
        "already_under_investigation": sum(1 for h in hypotheses
                                           if h["status"] == "under_investigation"),
        "novel": sum(1 for h in hypotheses if h["status"] == "novel"),
    }
    return report


# --------------------------------------------------------------------------- boundary 1: dosing

DOSE_DISCLAIMER = (
    "DOCUMENTED DOSE, QUOTED FROM A REGISTERED TRIAL RECORD. NOT A RECOMMENDATION. "
    "This platform does not and cannot predict a dose: dose selection requires PK/PD "
    "modelling that does not exist here, and for children an error is a safety event, "
    "not an accuracy problem. The text below is reproduced verbatim from the "
    "ClinicalTrials.gov record cited beside it. It has not been adjusted for weight, "
    "body-surface area, age, renal or hepatic function, formulation or indication, and "
    "it must not be. Read the source record and consult the prescribing information."
)

_DOSE_HINTS = (" mg", "mg/", " mcg", "µg", " g/", " units", " iu", "/kg", "/m2", "/m²",
               " daily", " twice", " once", " bid", " qd", " q12", " q24", "mg)")


def documented_doses(intervention, condition=None, limit=10, pediatric=False):
    """Dose text quoted verbatim from ClinicalTrials.gov intervention descriptions.

    Retrieval and quotation only. Nothing here computes, scales, converts or
    suggests a dose, and no adult figure is ever turned into a paediatric one.
    Every returned string is accompanied by the NCT id it was copied from and by
    DOSE_DISCLAIMER, which callers must render alongside it.
    """
    p = {"pageSize": limit, "countTotal": "true", "query.intr": intervention,
         "fields": "NCTId,BriefTitle,OverallStatus,Phase,Condition,StdAge,"
                   "ArmGroupInterventionName,InterventionName,InterventionDescription,"
                   "ArmGroupLabel,ArmGroupDescription,LeadSponsorName"}
    if condition:
        p["query.cond"] = condition
    if pediatric:
        p["filter.advanced"] = "AREA[StdAge]CHILD"
    d, e = db._get(db.CTGOV, **p)
    if not d:
        return {"disclaimer": DOSE_DISCLAIMER, "records": [], "count": None,
                "error": e or "no response from ClinicalTrials.gov"}

    records = []
    for study in d.get("studies", []):
        ps = study.get("protocolSection", {})
        nct = ps.get("identificationModule", {}).get("nctId")
        quotes = []
        for iv in ps.get("armsInterventionsModule", {}).get("interventions", []) or []:
            for field in ("name", "description"):
                text = (iv.get(field) or "").strip()
                low = text.lower()
                if text and any(h in low for h in _DOSE_HINTS):
                    quotes.append({"field": f"intervention.{field}", "verbatim": text[:600]})
        for arm in ps.get("armsInterventionsModule", {}).get("armGroups", []) or []:
            text = (arm.get("description") or "").strip()
            if text and any(h in text.lower() for h in _DOSE_HINTS):
                quotes.append({"field": "armGroup.description",
                               "arm": arm.get("label"), "verbatim": text[:600]})
        if not quotes:
            continue
        records.append({
            "nct_id": nct, "title": ps.get("identificationModule", {}).get("briefTitle"),
            "status": ps.get("statusModule", {}).get("overallStatus"),
            "phases": ps.get("designModule", {}).get("phases", []),
            "conditions": ps.get("conditionsModule", {}).get("conditions", []),
            "ages": ps.get("eligibilityModule", {}).get("stdAges", []),
            "lead_sponsor": ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name"),
            "url": f"https://clinicaltrials.gov/study/{nct}",
            "quoted_dose_text": quotes,
            "provenance": f"Verbatim from ClinicalTrials.gov record {nct}. Not computed, not adjusted.",
        })
    return {"disclaimer": DOSE_DISCLAIMER, "source": "ClinicalTrials.gov v2",
            "query": {"intervention": intervention, "condition": condition, "pediatric": pediatric},
            "count": d.get("totalCount"), "records": records,
            "computed_values": None,
            "note": "No field in this result was calculated. If you need a dose, it comes from "
                    "the label or the protocol, not from this platform."}


# --------------------------------------------------------------------------- boundary 2: combinations

COMBINATION_DISCLAIMER = (
    "CO-TARGET FLAG, NOT A SYNERGY CLAIM. These two compounds act on different targets "
    "that both have clinical precedent in this indication. That is a reason to run a "
    "combination experiment. It is not evidence of synergy, and it is equally consistent "
    "with additivity, antagonism, or overlapping toxicity that makes the pair unusable. "
    "Synergy is measured (Bliss, Loewe, HSA on a dose-response matrix); it cannot be "
    "inferred from target annotations, and nothing in this platform has measured it."
)


def cotarget_flags(reports, min_score=2.0, limit=25):
    """Pairs of compounds whose hypotheses converge on one indication via different targets.

    Returns questions for the bench, explicitly labelled as such. The output
    contains no synergy score, no predicted combination effect and no ranking by
    expected benefit, because none of those can be derived from what was joined.
    """
    index = {}
    for rep in reports:
        cid = (rep.get("compound") or {}).get("chembl_id")
        cname = (rep.get("compound") or {}).get("name") or (rep.get("compound") or {}).get("label")
        for h in rep.get("hypotheses", []):
            if h["score"] < min_score or "mechanism" not in h["joins"]:
                continue
            targets = sorted({r["refs"].get("target_symbol") for r in h["terms"]
                              if r.get("refs", {}).get("target_symbol")})
            index.setdefault(h["disease_id"], {"disease": h["disease"], "arms": []})["arms"].append(
                {"compound": cname, "chembl_id": cid, "score": h["score"], "targets": targets})

    flags = []
    for dis_id, block in index.items():
        arms = block["arms"]
        for i in range(len(arms)):
            for j in range(i + 1, len(arms)):
                a, b = arms[i], arms[j]
                if a["chembl_id"] == b["chembl_id"] or not a["targets"] or not b["targets"]:
                    continue
                if set(a["targets"]) & set(b["targets"]):
                    continue  # same target: that is not a combination rationale
                flags.append({
                    "disease_id": dis_id, "disease": block["disease"],
                    "compound_a": a["compound"], "targets_a": a["targets"],
                    "compound_b": b["compound"], "targets_b": b["targets"],
                    "individual_scores": {a["compound"]: a["score"], b["compound"]: b["score"]},
                    "claim": "none",
                    "question_for_the_bench": (
                        f"Does combining {a['compound']} ({'/'.join(a['targets'])}) with "
                        f"{b['compound']} ({'/'.join(b['targets'])}) do anything in "
                        f"{block['disease']} that either does alone? Measure it: dose-response "
                        "matrix, Bliss or Loewe, plus a shared-toxicity arm."),
                    "disclaimer": COMBINATION_DISCLAIMER,
                })
    flags.sort(key=lambda f: -max(f["individual_scores"].values()))
    return {"disclaimer": COMBINATION_DISCLAIMER, "flags": flags[:limit],
            "synergy_predicted": False,
            "note": "This function cannot and does not predict combination effects."}


BOUNDARIES = {
    "dosing": {
        "computed": False,
        "policy": "Documented doses are quoted verbatim from ClinicalTrials.gov with their NCT id. "
                  "No dose is computed, scaled, extrapolated or suggested, and no adult dose is "
                  "converted to a paediatric one.",
        "disclaimer": DOSE_DISCLAIMER,
    },
    "combinations": {
        "synergy_predicted": False,
        "policy": "Co-target convergence is flagged as an experiment to run. Synergy, antagonism "
                  "and shared toxicity are measured, not inferred from target annotations.",
        "disclaimer": COMBINATION_DISCLAIMER,
    },
    "score": {
        "is_probability": False,
        "policy": "The score is the sum of the listed terms after per-join caps. Every term names "
                  "its source and identifiers. Ordinal only.",
    },
}
