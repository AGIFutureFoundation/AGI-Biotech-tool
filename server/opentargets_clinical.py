"""Open Targets clinical evidence, at the resolution the repurposing joins need.

db_clients.opentargets_target_drugs exists and is correct, but it is built for
display: it sorts each drug's disease list alphabetically and keeps the first
six. For sildenafil that drops "pulmonary arterial hypertension" -- the single
most famous repurposing case there is -- before any scoring can see it. So this
module issues its own queries for the two things the joins need and db_clients
does not expose:

  * target_precedent(ensembl)  -- every drug annotated against a target, with its
    complete disease footprint, not the first six.
  * drug_indications(chembl_ids) -- each indication with the highest clinical
    stage that drug reached *for that indication*, which is what separates "this
    is the label" from "somebody ran a phase 1".

Both go through db_clients.HTTP, so throttling, the SQLite cache and the circuit
breaker are shared with the rest of the platform. Nothing here raises; failures
come back as {"error": ...} with empty collections.
"""
from __future__ import annotations

import db_clients as db

# Open Targets' maxClinicalStage vocabulary, ordered. The numeric rank is used
# for "did this reach further than that", never as a score by itself.
PHASE_RANK = {
    "APPROVAL": 5,
    "PHASE_4": 5,
    "PHASE_3": 4,
    "PHASE_2_3": 3,
    "PHASE_2": 3,
    "PHASE_1_2": 2,
    "PHASE_1": 2,
    "EARLY_PHASE_1": 1,
    "PHASE_0": 1,
    "UNKNOWN": 0,
    None: 0,
}

APPROVED_STAGES = {"APPROVAL", "PHASE_4"}

_TARGET_PRECEDENT_QUERY = """
query($id:String!){
  target(ensemblId:$id){
    id approvedSymbol approvedName
    drugAndClinicalCandidates {
      count
      rows {
        maxClinicalStage
        drug { id name drugType mechanismsOfAction { rows { mechanismOfAction actionType } } }
        diseases { disease { id name } }
      }
    }
  }
}"""


def _gql(query, variables=None):
    d, e = db.HTTP.json("POST", db.OPENTARGETS,
                        json_body={"query": query, "variables": variables or {}})
    if e:
        return None, e
    errs = (d or {}).get("errors")
    if errs:
        return None, "; ".join(str(x.get("message"))[:200] for x in errs[:2])
    return (d or {}).get("data"), None


def target_precedent(ensembl_id):
    """Every drug/clinical candidate acting on one target, with its full disease list.

    Returns {ensembl, symbol, name, count, drugs: [...]}. Each drug carries:
      chembl_id, name, drug_type, max_stage (the drug's overall furthest stage),
      mechanisms [{mechanism, action_type}], and diseases [{id, name}] deduplicated
      by EFO/MONDO id.

    Caveat that the caller must carry into any scoring: `diseases` is the drug's
    *entire* clinical footprint, not the subset attributable to this target. A
    drug with 180 trialled indications contributes 180 weak co-occurrences here.
    Phase and multi-drug convergence are what make this evidence rather than noise.
    """
    data, err = _gql(_TARGET_PRECEDENT_QUERY, {"id": ensembl_id})
    t = (data or {}).get("target")
    if not t:
        return {"ensembl": ensembl_id, "symbol": None, "count": None, "drugs": [],
                "error": err or "no Open Targets record for this Ensembl gene",
                "source": "Open Targets"}
    block = t.get("drugAndClinicalCandidates") or {}
    drugs = []
    for row in block.get("rows") or []:
        drug = row.get("drug") or {}
        if not drug.get("id"):
            continue
        seen, diseases = set(), []
        for item in row.get("diseases") or []:
            dis = item.get("disease") or {}
            if dis.get("id") and dis["id"] not in seen:
                seen.add(dis["id"])
                diseases.append({"id": dis["id"], "name": dis.get("name")})
        moa = (drug.get("mechanismsOfAction") or {}).get("rows") or []
        drugs.append({
            "chembl_id": drug["id"], "name": drug.get("name"), "drug_type": drug.get("drugType"),
            "max_stage": row.get("maxClinicalStage"),
            "mechanisms": [{"mechanism": m.get("mechanismOfAction"),
                            "action_type": m.get("actionType")} for m in moa],
            "diseases": diseases,
            "url": f"https://platform.opentargets.org/drug/{drug['id']}",
        })
    return {"ensembl": ensembl_id, "symbol": t.get("approvedSymbol"), "name": t.get("approvedName"),
            "count": block.get("count"), "drugs": drugs, "source": "Open Targets",
            "url": f"https://platform.opentargets.org/target/{ensembl_id}"}


# Aliased batch: one HTTP round trip for up to BATCH_SIZE drugs. Above ~20 the
# response gets large enough that a timeout is likelier than the saving is worth.
BATCH_SIZE = 12


def drug_indications(chembl_ids):
    """{chembl_id: {name, max_stage, indications: [{stage, rank, disease_id, disease}]}}.

    'stage' is maxClinicalStage *for that indication*, so APPROVAL means the drug
    is approved for it -- the field the engine uses to separate an existing label
    from a repurposing hypothesis.
    """
    ids = [c for c in dict.fromkeys(chembl_ids) if c]
    out = {}
    for start in range(0, len(ids), BATCH_SIZE):
        chunk = ids[start:start + BATCH_SIZE]
        parts = " ".join(
            f'a{i}:drug(chemblId:"{cid}"){{ id name maximumClinicalStage '
            f'indications {{ rows {{ maxClinicalStage disease {{ id name }} }} }} }}'
            for i, cid in enumerate(chunk))
        data, err = _gql("{ " + parts + " }")
        if data is None:
            for cid in chunk:
                out[cid] = {"name": None, "indications": [], "error": err}
            continue
        for i, cid in enumerate(chunk):
            drug = data.get(f"a{i}")
            if not drug:
                out[cid] = {"name": None, "max_stage": None, "indications": [],
                            "error": "no Open Targets drug record"}
                continue
            rows = []
            for r in (drug.get("indications") or {}).get("rows") or []:
                dis = r.get("disease") or {}
                if not dis.get("id"):
                    continue
                stage = r.get("maxClinicalStage")
                rows.append({"stage": stage, "rank": PHASE_RANK.get(stage, 0),
                             "disease_id": dis["id"], "disease": dis.get("name")})
            out[cid] = {"name": drug.get("name"), "max_stage": drug.get("maximumClinicalStage"),
                        "indications": rows, "source": "Open Targets"}
    return out


def best_stage_by_disease(indications):
    """Collapse one drug's indication rows to {disease_id: best row}."""
    best = {}
    for row in indications:
        cur = best.get(row["disease_id"])
        if cur is None or row["rank"] > cur["rank"]:
            best[row["disease_id"]] = row
    return best
