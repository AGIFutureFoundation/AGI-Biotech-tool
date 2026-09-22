"""The four cross-source joins that produce drug-repurposing hypotheses.

Each join takes a resolved compound and emits *evidence terms*. A term is a
single, checkable statement with the source that supports it and the identifiers
needed to go and look. Terms carry points, but the points are assigned in
repurposing_engine.SCORING, not here -- this module's only job is to find and
attribute the connections.

The joins, strongest evidence first:

  1. mechanism  -- compound -> its ChEMBL-curated mechanism targets -> other drugs
     annotated against the same target (Open Targets) -> the stage those drugs
     reached for each indication. The backbone. Evidence that a target is
     clinically addressable for a disease.

  2. structure  -- compound -> ChEMBL 2D-similarity neighbours -> approved drugs
     among them -> their indications. Similarity is *recomputed locally* with
     RDKit (Morgan radius 2, 2048-bit, Tanimoto) and reported as a number;
     ChEMBL's own similarity search is used only to propose candidates.

  3. network    -- compound's target -> Reactome pathway co-membership or a STRING
     interaction -> a *different* protein that is a curated disease-panel target.
     This is where non-obvious hypotheses come from and where false positives come
     from, in the same proportion. Deliberately capped so it cannot carry a
     hypothesis on its own.

  4. polypharmacology -- two or more distinct mechanism targets of the *same*
     compound independently showing clinical precedent for the same disease.
     Convergence, not merely "this drug is promiscuous".

Nothing here raises. Every join degrades to an empty list and records why.
"""
from __future__ import annotations

import db_clients as db
import opentargets_clinical as otc
import target_identifiers as ti

try:
    from rdkit import Chem, DataStructs, RDLogger
    from rdkit.Chem import rdFingerprintGenerator
    RDLogger.DisableLog("rdApp.*")
    # includeChirality is on deliberately. Without it ECFP4 scores D-mannitol and
    # D-sorbitol as Tanimoto 1.00 -- identical -- and the structural join happily
    # transfers one's indications to the other. Stereochemistry changes
    # pharmacology; a fingerprint that cannot see it is the wrong instrument.
    _FPGEN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048,
                                                       includeChirality=True)
except ImportError:  # pragma: no cover - rdkit is a hard requirement of the venv
    Chem = DataStructs = None
    _FPGEN = None

# The structural join states its metric and threshold, because "similar" without
# a number is not a claim. Morgan/ECFP4 Tanimoto is the default in the field; the
# 0.40 floor is the conventional "possibly related scaffold" line, well below the
# ~0.85 at which shared activity becomes a reasonable prior.
FINGERPRINT = "RDKit Morgan (ECFP4-equivalent), radius 2, 2048 bits, chirality-aware"

# A ChEMBL "target" that is a protein complex with more components than this is
# not a usable gene-level join. Mitochondrial complex I (metformin's annotated
# target) has 51: querying Open Targets for each one costs 51 requests and then
# counts a single piece of evidence 51 times. Such targets are recorded and
# skipped rather than silently expanded.
MAX_COMPLEX_COMPONENTS = 10
SIMILARITY_METRIC = "Tanimoto"
SIMILARITY_FLOOR = 0.40

# Reactome pathways this generic are shared by most of the proteome and carry no
# hypothesis-generating information. Name-matched because the alternative (a
# participant-count lookup per pathway) is one HTTP call per pathway per protein.
GENERIC_PATHWAY_PREFIXES = (
    "metabolism", "signal transduction", "immune system", "disease",
    "gene expression", "signaling by", "cellular responses to",
    "developmental biology", "transport of small molecules", "hemostasis",
    "post-translational protein modification", "membrane trafficking",
    "vesicle-mediated transport", "cell cycle", "programmed cell death",
    "metabolism of proteins", "metabolism of rna", "innate immune system",
    "adaptive immune system", "cytokine signaling in immune system",
)

# A pathway shared by more than this fraction of the proteins examined in one run
# is doing no discriminating work, whatever it is called. Data-driven backstop
# for whatever the name blocklist misses.
PATHWAY_UBIQUITY_LIMIT = 0.25

STRING_HIGH = 0.90
STRING_MEDIUM = 0.70


def term(join, kind, statement, source, refs=None, caveat=None, **extra):
    """One inspectable piece of evidence. `statement` is what a reviewer reads."""
    t = {"join": join, "kind": kind, "statement": statement, "source": source,
         "refs": refs or {}}
    if caveat:
        t["caveat"] = caveat
    t.update(extra)
    return t


# --------------------------------------------------------------------------- compound resolution

def _chembl_raw(chembl_id):
    d, _ = db._get(f"{db.CHEMBL}/molecule/{chembl_id}.json")
    return d or {}


def _family(chembl_id):
    """The molecule's salt/parent family: {parent, members[]}.

    This matters more than it sounds. ChEMBL annotates mechanism of action
    inconsistently across salt forms -- sildenafil's mechanism hangs off the
    citrate (CHEMBL1737) and metformin's off the hydrochloride (CHEMBL1703),
    while the free bases carry none. A resolver that stops at the free base finds
    no mechanism for either drug and the whole engine silently returns nothing.
    """
    raw = _chembl_raw(chembl_id)
    parent = (raw.get("molecule_hierarchy") or {}).get("parent_chembl_id") or chembl_id
    d, _ = db._get(f"{db.CHEMBL}/molecule.json",
                   molecule_hierarchy__parent_chembl_id=parent, limit=20)
    members = [m.get("molecule_chembl_id") for m in (d or {}).get("molecules", [])
               if m.get("molecule_chembl_id")]
    for cid in (chembl_id, parent):
        if cid not in members:
            members.insert(0, cid)
    return {"parent": parent, "members": members}


def resolve_compound(smiles=None, name=None, chembl_id=None, inchikey=None, label=None):
    """Resolve a structure or a name to a ChEMBL identity plus its curated mechanisms.

    Returns {label, chembl_id, name, smiles, inchikey, max_phase, family, mechanisms,
             targets, own_indications, notes[], error?}.

    `targets` is one entry per component gene of every mechanism target, already
    carrying the Ensembl id Open Targets needs. `own_indications` is what this
    compound is already approved for or already in trials for -- the engine
    subtracts it, because restating a drug's own label is not a hypothesis.
    """
    notes = []
    ik = inchikey or (db.inchikey_of(smiles) if smiles else None)

    cid = chembl_id
    if not cid and ik:
        m = db.chembl_molecule(inchikey=ik)
        if isinstance(m, dict) and m.get("chembl_id"):
            cid = m["chembl_id"]
    if not cid and name:
        hits = db.chembl_search(name, limit=5).get("molecules") or []
        named = [h for h in hits if h.get("name")]
        if named:
            cid = named[0]["chembl_id"]
            notes.append(f"resolved by name search on '{name}' -> {cid} ({named[0]['name']}); "
                         "name resolution is weaker than an InChIKey match")

    identity = {"label": label or name or chembl_id or smiles, "chembl_id": cid,
                "smiles": smiles, "inchikey": ik, "name": None, "max_phase": None,
                "family": [], "mechanisms": [], "targets": [], "own_indications": {},
                "notes": notes}
    if not cid:
        identity["error"] = "no ChEMBL molecule matched this compound"
        return identity

    mol = db.chembl_molecule(chembl_id=cid) or {}
    identity.update(name=mol.get("name"), max_phase=mol.get("max_phase"))
    identity["smiles"] = smiles or mol.get("smiles")
    identity["inchikey"] = ik or mol.get("inchikey")

    fam = _family(cid)
    identity["family"] = fam["members"]
    identity["parent_chembl_id"] = fam["parent"]

    seen = set()
    for member in fam["members"]:
        for mech in db.chembl_mechanisms(member) or []:
            key = (mech.get("target_chembl_id"), mech.get("mechanism"), mech.get("action"))
            if key in seen or not mech.get("target_chembl_id"):
                continue
            seen.add(key)
            identity["mechanisms"].append(dict(mech, from_chembl_id=member))
    if identity["mechanisms"] and all(m["from_chembl_id"] != cid for m in identity["mechanisms"]):
        notes.append("mechanism annotations were found on a salt form, not on "
                     f"{cid} itself; targets are inherited from the family")

    identity["skipped_targets"] = []
    for mech in identity["mechanisms"]:
        resolved = ti.genes_for_chembl_target(mech["target_chembl_id"])
        tgt = resolved["target"]
        if len(resolved["genes"]) > MAX_COMPLEX_COMPONENTS:
            identity["skipped_targets"].append({
                "target_chembl_id": mech["target_chembl_id"], "target_name": tgt.get("name"),
                "components": len(resolved["genes"]),
                "reason": f"protein complex with {len(resolved['genes'])} components "
                          f"(limit {MAX_COMPLEX_COMPONENTS}); a gene-level join here would count "
                          "one piece of evidence once per subunit"})
            notes.append(f"mechanism target '{tgt.get('name')}' was not expanded: "
                         f"{len(resolved['genes'])} subunits. Any hypothesis that depended on it "
                         "is absent from this report, not scored low.")
            continue
        for gene in resolved["genes"]:
            identity["targets"].append({
                **gene,
                "target_chembl_id": mech["target_chembl_id"],
                "target_name": tgt.get("name"),
                "target_type": tgt.get("target_type"),
                "mechanism": mech.get("mechanism"),
                "action_type": mech.get("action"),
                "is_complex_component": tgt.get("target_type") == "PROTEIN COMPLEX",
            })
    if any(t["is_complex_component"] for t in identity["targets"]):
        notes.append("at least one mechanism is annotated against a protein complex; "
                     "every component gene is treated as a candidate, which over-counts "
                     "scaffolding subunits that are not the pharmacological target")

    own = otc.drug_indications(identity["family"])
    merged = {}
    for rec in own.values():
        for row in rec.get("indications") or []:
            cur = merged.get(row["disease_id"])
            if cur is None or row["rank"] > cur["rank"]:
                merged[row["disease_id"]] = row
    identity["own_indications"] = merged
    return identity


# --------------------------------------------------------------------------- join 1: mechanism

def mechanism_join(identity, exclude_self=True, max_drugs_per_target=12):
    """Compound -> target -> other drugs on that target -> the diseases they reached.

    `exclude_self` drops the compound and its own salt family from the precedent
    set. That is not cosmetic: with it off, every approved drug trivially
    "predicts" its own label and the engine looks far better than it is. Every
    evaluation in this repo runs with it on.

    Returns (evidence_by_disease, diagnostics).
    """
    by_disease, diag = {}, {"targets_queried": [], "targets_failed": []}
    family = set(identity.get("family") or [])

    for tgt in identity.get("targets", []):
        prec = otc.target_precedent(tgt["ensembl"])
        if prec.get("error"):
            diag["targets_failed"].append({"symbol": tgt.get("symbol"),
                                           "ensembl": tgt["ensembl"], "error": prec["error"]})
            continue
        others = [d for d in prec["drugs"]
                  if not (exclude_self and d["chembl_id"] in family)]
        others.sort(key=lambda d: otc.PHASE_RANK.get(d["max_stage"], 0), reverse=True)
        others = others[:max_drugs_per_target]
        diag["targets_queried"].append({"symbol": prec.get("symbol"), "ensembl": tgt["ensembl"],
                                        "precedent_drugs": len(others)})
        if not others:
            continue

        stages = otc.drug_indications([d["chembl_id"] for d in others])
        for drug in others:
            best = otc.best_stage_by_disease((stages.get(drug["chembl_id"]) or {})
                                             .get("indications") or [])
            action = next((m["action_type"] for m in drug["mechanisms"] if m.get("action_type")), None)
            for dis in drug["diseases"]:
                row = best.get(dis["id"])
                stage = row["stage"] if row else "UNKNOWN"
                bucket = by_disease.setdefault(dis["id"], {"disease": dis["name"], "items": []})
                bucket["items"].append({
                    "target_symbol": prec.get("symbol"), "ensembl": tgt["ensembl"],
                    "target_chembl_id": tgt["target_chembl_id"],
                    "query_action_type": tgt.get("action_type"),
                    "precedent_action_type": action,
                    "drug_chembl_id": drug["chembl_id"], "drug": drug["name"],
                    "drug_type": drug["drug_type"], "stage": stage,
                    "rank": otc.PHASE_RANK.get(stage, 0),
                    "is_complex_component": tgt.get("is_complex_component", False),
                    "mechanism": (drug["mechanisms"] or [{}])[0].get("mechanism"),
                })
    return by_disease, diag


# --------------------------------------------------------------------------- join 2: structure

def _tanimoto(smiles_a, smiles_b):
    if _FPGEN is None or not smiles_a or not smiles_b:
        return None
    a, b = Chem.MolFromSmiles(smiles_a), Chem.MolFromSmiles(smiles_b)
    if a is None or b is None:
        return None
    return round(DataStructs.TanimotoSimilarity(_FPGEN.GetFingerprint(a),
                                                _FPGEN.GetFingerprint(b)), 3)


def structural_analogues(smiles, chembl_threshold=70, limit=25, approved_only=True):
    """ChEMBL similarity neighbours, re-scored locally and filtered to approved drugs.

    ChEMBL's similarity endpoint proposes candidates; the similarity that is
    reported and scored is the locally computed one, so the metric is ours and
    stated. Neighbours below SIMILARITY_FLOOR are dropped whatever ChEMBL said.
    """
    if not smiles:
        return [], {"error": "no SMILES for the query compound"}
    res = db.chembl_similar(smiles, similarity=chembl_threshold, limit=limit)
    if res.get("error"):
        return [], {"error": res["error"]}
    out = []
    for mol in res.get("molecules") or []:
        tan = _tanimoto(smiles, mol.get("smiles"))
        if tan is None or tan < SIMILARITY_FLOOR:
            continue
        approved = str(mol.get("max_phase")) in ("4", "4.0")
        if approved_only and not approved:
            continue
        out.append({"chembl_id": mol["chembl_id"], "name": mol.get("name"),
                    "smiles": mol.get("smiles"), "max_phase": mol.get("max_phase"),
                    "tanimoto": tan, "chembl_similarity": mol.get("similarity"),
                    "url": mol.get("url")})
    out.sort(key=lambda m: m["tanimoto"], reverse=True)
    return out, {"candidates": len(res.get("molecules") or []), "kept": len(out)}


def structure_join(identity, min_stage_rank=3):
    """Compound -> similar approved drug -> that drug's indications (phase >= 2).

    Only indications the analogue actually reached phase 2 or beyond are carried
    across; a phase-1 record on a look-alike molecule is not a reason to test
    anything. Returns (evidence_by_disease, diagnostics).
    """
    smiles = identity.get("smiles")
    analogues, diag = structural_analogues(smiles)
    family = set(identity.get("family") or [])
    analogues = [a for a in analogues if a["chembl_id"] not in family]
    diag["analogues"] = [{"chembl_id": a["chembl_id"], "name": a["name"],
                          "tanimoto": a["tanimoto"]} for a in analogues]
    if not analogues:
        return {}, diag

    stages = otc.drug_indications([a["chembl_id"] for a in analogues])
    mechs = {a["chembl_id"]: db.chembl_mechanisms(a["chembl_id"]) for a in analogues[:8]}
    by_disease = {}
    for a in analogues:
        best = otc.best_stage_by_disease((stages.get(a["chembl_id"]) or {}).get("indications") or [])
        for dis_id, row in best.items():
            if row["rank"] < min_stage_rank:
                continue
            bucket = by_disease.setdefault(dis_id, {"disease": row["disease"], "items": []})
            bucket["items"].append({
                "analogue_chembl_id": a["chembl_id"], "analogue": a["name"],
                "tanimoto": a["tanimoto"], "stage": row["stage"], "rank": row["rank"],
                "analogue_targets": [m.get("mechanism") for m in (mechs.get(a["chembl_id"]) or [])][:3],
            })
    return by_disease, diag


# --------------------------------------------------------------------------- join 3: network

def _panel_targets(panels_module):
    """Every disease-panel target that carries a UniProt accession in its evidence record.

    Read-only view over server/disease_panels.py, which another agent owns. Panels
    whose evidence dict does not exist yet are skipped rather than guessed at.
    """
    index = []
    for panel_key in panels_module.list_panels():
        panel = panels_module.get_panel(panel_key) or {}
        evidence = getattr(panels_module, f"{panel_key.upper()}_EVIDENCE", None)
        if not isinstance(evidence, dict):
            continue
        for symbol, ev in evidence.items():
            if not ev.get("uniprot"):
                continue
            index.append({"panel": panel_key, "panel_name": panel.get("name", panel_key),
                          "symbol": symbol, "accession": ev["uniprot"],
                          "indication": ev.get("indication") or panel.get("name"),
                          "tractability": ev.get("tractability"),
                          "unmet_need": ev.get("unmet_need"),
                          "pediatric_onset": ev.get("pediatric_onset")})
    return index


def network_join(identity, panels_module, string_limit=25):
    """Compound target -> Reactome co-membership or STRING interaction -> a panel target.

    The connection is between two *different* proteins, which is the point and
    also the risk: pathway co-membership is not a mechanism. Two filters keep it
    from swamping everything -- a generic-pathway name blocklist and a run-local
    ubiquity cut that drops any pathway shared by more than PATHWAY_UBIQUITY_LIMIT
    of the proteins examined. The engine caps the resulting points on top of that.

    Returns (evidence_by_panel_target, diagnostics).
    """
    targets = identity.get("targets") or []
    if not targets:
        return {}, {"error": "compound has no resolved targets; network join needs one"}

    panel_targets = _panel_targets(panels_module)
    diag = {"panel_targets": len(panel_targets), "pathways_dropped_generic": 0,
            "pathways_dropped_ubiquitous": 0}
    if not panel_targets:
        diag["error"] = "no disease-panel target carries a UniProt accession"
        return {}, diag

    pathways, seen_proteins = {}, set()
    for acc in {t["accession"] for t in targets} | {p["accession"] for p in panel_targets}:
        res = db.reactome_pathways(acc)
        seen_proteins.add(acc)
        for p in res.get("pathways") or []:
            entry = pathways.setdefault(p["id"], {"name": p.get("name"), "accessions": set(),
                                                  "disease": p.get("disease")})
            entry["accessions"].add(acc)

    n_proteins = max(len(seen_proteins), 1)
    usable = {}
    for pid, entry in pathways.items():
        lowered = (entry["name"] or "").lower()
        if any(lowered.startswith(prefix) for prefix in GENERIC_PATHWAY_PREFIXES):
            diag["pathways_dropped_generic"] += 1
            continue
        if len(entry["accessions"]) / n_proteins > PATHWAY_UBIQUITY_LIMIT:
            diag["pathways_dropped_ubiquitous"] += 1
            continue
        usable[pid] = entry
    diag["pathways_usable"] = len(usable)

    partners = {}
    for symbol in {t.get("symbol") for t in targets if t.get("symbol")}:
        res = db.string_partners(symbol, limit=string_limit)
        for p in res.get("partners") or []:
            if not p.get("partner"):
                continue
            key = (symbol, p["partner"].upper())
            partners[key] = max(partners.get(key, 0.0), float(p.get("score") or 0.0))

    by_key = {}
    for tgt in targets:
        for panel in panel_targets:
            if panel["accession"] == tgt["accession"]:
                continue  # same protein: that is the mechanism join, not this one
            items = []
            for pid, entry in usable.items():
                if tgt["accession"] in entry["accessions"] and panel["accession"] in entry["accessions"]:
                    items.append({"kind": "reactome_pathway", "pathway_id": pid,
                                  "pathway": entry["name"], "in_disease": entry.get("disease"),
                                  "url": f"https://reactome.org/content/detail/{pid}"})
            score = partners.get((tgt.get("symbol"), (panel["symbol"] or "").upper()), 0.0)
            if score >= STRING_MEDIUM:
                items.append({"kind": "string_interaction", "score": round(score, 3),
                              "confidence": "high" if score >= STRING_HIGH else "medium",
                              "url": f"https://string-db.org/cgi/network?identifiers="
                                     f"{tgt.get('symbol')}%0d{panel['symbol']}"})
            if not items:
                continue
            key = f"panel:{panel['panel']}:{panel['symbol']}"
            bucket = by_key.setdefault(key, {
                "disease": f"{panel['indication']} ({panel['panel_name']})",
                "panel": panel["panel"], "panel_target": panel["symbol"],
                "pediatric_onset": panel.get("pediatric_onset"),
                "unmet_need": panel.get("unmet_need"), "items": []})
            for item in items:
                bucket["items"].append({**item, "compound_target": tgt.get("symbol"),
                                        "compound_target_accession": tgt["accession"],
                                        "panel_target": panel["symbol"],
                                        "panel_target_accession": panel["accession"]})
    return by_key, diag
