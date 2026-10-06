"""Where a compound can be bought, from whom, and what is actually known about cost.

This module answers a procurement question, not a scientific one: given a
structure, is it purchasable, from which vendors, under which catalogue numbers,
and what would it cost. It is built on the same live-or-say-so principle as
server/db_clients.py -- a provider is live, or it reports itself unavailable and
names the environment variable that would enable it. Nothing here invents a
price, and nothing here places an order.

What is live and keyless
------------------------
* **PubChem chemical vendors** (PUG-View ``categories``). Real, free, no key.
  For ibuprofen (CID 3672) this returns 178 vendor records, each carrying
  ``SourceName``, ``RegistryID`` (the vendor's own catalogue number),
  ``SourceRecordURL`` (a direct product page) and ``SID``. This is genuine
  availability and genuine catalogue routing.
* **Mcule keyless lookup** (``/api/v1/search/lookup/``). Resolves a SMILES or
  InChIKey to Mcule IDs and product URLs. Corroborates availability and yields
  the identifier a human needs to request a quote.

What PubChem does NOT carry, verified by inspection
---------------------------------------------------
Price, pack size, purity, grade and lead time are absent from the vendor
records. They are not sparse -- they are not in the schema. Any cost number in
this module therefore has to name its source, and when there is no source the
field is reported missing rather than filled.

The pricing decision, and the evidence behind it
------------------------------------------------
**Programmatic pricing is key-gated. This module does not ship a free price
source, because there is no honest one.** Each candidate was exercised
before being accepted or rejected (see PRICING_EVIDENCE):

* **Mcule** ``/compound/<id>/prices/`` -> HTTP 401 "Authentication credentials
  were not provided." Key-gated. Implemented as a key-gated provider.
* **MolPort** ``/api/chemical-search/search`` -> HTTP 200 with
  ``"Username or password is incorrect!"``. Credential-gated.
* **ChemSpace** ``/auth/token`` exists and is POST-only. Token-gated.
* **ZINC (CartBlanche22)** is free and keyless and *looks* like the answer: its
  substance records carry a ``catalogs`` list with a ``price`` field. **It is
  rejected as a price source.** Every catalogue entry for every substance tested
  reports the identical tuple ``price=240, quantity=10, unit='mg',
  shipping='6 weeks'`` -- across 29 catalogues for ZINC000000000039, 152 for
  ZINC000000001234 and 281 for ZINC000019632618. A constant that does not vary
  by vendor, by compound or by pack size is a schema default, not a quote.
  Passing it through as "cost" would have produced exactly the plausible,
  uniform, entirely fictional totals this module exists to prevent. ZINC may
  still be used for purchasability annotation; its price field is discarded at
  the parse boundary and never reaches a record.

So: **availability is free and real; price is not.** When no price provider is
configured, a bill of materials says so per line and in its totals, and the
actionable output is a structured request for quotation that a human sends.

Three boundaries this module enforces rather than documents
-----------------------------------------------------------
* **It never places an order.** There is no cart, no checkout, no vendor
  authentication, no purchase submission. ``request_for_quote()`` produces a
  document a person reads, checks and sends themselves.
* **It never silently substitutes a molecule.** A compound absent from every
  catalogue returns zero offers. Structural neighbours are available only from
  ``similar_available_compounds()``, which is a separate call whose every record
  carries ``is_not_your_compound=True``; neighbours are never merged into a BOM
  line. Ordering a near-neighbour by accident is the failure mode that makes a
  sourcing tool worse than no sourcing tool.
* **It never presents a research chemical as a clinical product.** PubChem
  carries no purity or grade, so every offer reports ``grade=None`` and
  ``GRADE_CAVEAT``. Catalogue ibuprofen is not pharmaceutical-grade ibuprofen,
  and on a paediatric research platform that distinction is not pedantry.

Regulatory status is flagged, never determined. Legal status cannot be read
off these APIs -- PubChem's "Governmental Organizations" sources were checked
for fentanyl (CID 3345), ketamine (CID 3821) and ibuprofen (CID 3672) and carry
no DEA or scheduling signal at all. ``regulatory_flags()` therefore matches a
small, explicit, non-exhaustive curated watchlist and says loudly that it is
advisory and not legal advice. Its job is to stop a restricted compound
appearing on a BOM as a routine purchase, not to clear one for purchase.

Environment: MCULE_API_KEY (optional; enables Mcule price quotes).
"""
from __future__ import annotations

import datetime as _dt
import os
import re

import db_clients as db

SCHEMA_VERSION = "1.0"

PUG_VIEW = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"
MCULE = "https://mcule.com/api/v1"
ZINC = "https://cartblanche22.docking.org"

VENDOR_CATEGORY = "Chemical Vendors"

GRADE_CAVEAT = (
    "Catalogue listing only. PubChem carries no purity, grade, salt form, pack size or "
    "lead time. Assume research-grade unless the vendor's own documentation states "
    "otherwise; do not treat as pharmaceutical/GMP grade without a CoA from the vendor."
)

NO_PRICE_REASON = (
    "No price provider is configured. PubChem vendor records contain no price field. "
    "Set MCULE_API_KEY to enable Mcule quotes, or send the request_for_quote() output "
    "to the listed vendors."
)

# Recorded so the pricing decision can be re-checked rather than taken on trust.
# Each entry is what the endpoint actually returned when exercised.
PRICING_EVIDENCE = {
    "mcule_prices": {
        "url": f"{MCULE}/compound/<mcule_id>/prices/",
        "observed": 'HTTP 401 {"detail":"Authentication credentials were not provided."}',
        "verdict": "key-gated", "env_var": "MCULE_API_KEY",
    },
    "molport": {
        "url": "https://api.molport.com/api/chemical-search/search",
        "observed": 'HTTP 200 {"Result":{"Status":2,"Message":"Username or password is incorrect!"}}',
        "verdict": "credential-gated", "env_var": "MOLPORT_USERNAME / MOLPORT_PASSWORD",
    },
    "chemspace": {
        "url": "https://api.chem-space.com/auth/token",
        "observed": "HTTP 405 on GET; endpoint exists and is POST-only, token required",
        "verdict": "token-gated", "env_var": "CHEMSPACE_API_KEY",
    },
    "zinc_catalogs": {
        "url": f"{ZINC}/substance/<zinc_id>.json",
        "observed": "price=240, quantity=10, unit='mg', shipping='6 weeks' identical across "
                    "29/152/281 catalogue entries for ZINC000000000039 / ZINC000000001234 / "
                    "ZINC000019632618",
        "verdict": "REJECTED as a price source: constant schema default, not a quote. "
                   "Purchasability annotation only; price field discarded at parse.",
        "env_var": None,
    },
}


# --------------------------------------------------------------------------- regulatory watchlist

REGULATORY_DISCLAIMER = (
    "ADVISORY ONLY, NOT LEGAL ADVICE AND NOT EXHAUSTIVE. Controlled-substance scheduling, "
    "licensing and export control cannot be determined from these APIs and vary by "
    "jurisdiction. Absence of a flag here is NOT evidence that a compound is unrestricted. "
    "Clear every purchase with your institution's controlled-substances officer, EHS and "
    "import/export compliance before ordering."
)

# Keyed by InChIKey skeleton (the first 14-character block), which is the connectivity
# layer: it matches salts, stereoisomers and hydrates of the same parent, which is what
# a procurement flag should do. Curated from public scheduling and handling references.
_WATCHLIST = {
    # --- Controlled substances (US CSA schedules cited; other jurisdictions differ) ---
    "PJMPHNIQZUBGLI": ("controlled_substance", "Fentanyl: US CSA Schedule II. DEA registration and licensed handling required."),
    "VCKUSRYTPJJLNI": ("controlled_substance", "Ketamine: US CSA Schedule III. Licensed handling required."),
    "BQJCRHHNABKAKU": ("controlled_substance", "Morphine: US CSA Schedule II. DEA registration required."),
    "ZPUCINDJVBIVPJ": ("controlled_substance", "Cocaine: US CSA Schedule II. DEA registration required."),
    "DUGOZIWVEXMGBE": ("controlled_substance", "Methylphenidate: US CSA Schedule II."),
    "KWTSXDURSIMDCE": ("controlled_substance", "Amphetamine: US CSA Schedule II."),
    "AAOVKJBEBIDNHE": ("controlled_substance", "Diazepam: US CSA Schedule IV."),
    "DDLIGBOFAVUZHB": ("controlled_substance", "Midazolam: US CSA Schedule IV."),
    "DDBREPKUVSBGFI": ("controlled_substance", "Phenobarbital: US CSA Schedule IV."),
    "GVGLGOZIDCSQPN": ("controlled_substance", "Pentobarbital: US CSA Schedule II."),
    # --- Restricted distribution / REMS / severe teratogens ---
    "UEJJHQNACJXSKW": ("restricted_distribution", "Thalidomide: severe teratogen; REMS-restricted distribution. Not obtainable as a routine catalogue purchase for human use."),
    "GOTYRUGSSMKFNF": ("restricted_distribution", "Lenalidomide: thalidomide analogue; teratogen; REMS-restricted distribution."),
    "UVSMNLNDYGZFPF": ("restricted_distribution", "Pomalidomide: thalidomide analogue; teratogen; REMS-restricted distribution."),
    "SHGAZHPCJJPHSC": ("restricted_distribution", "Retinoic acid (tretinoin/isotretinoin): potent teratogen; pregnancy-prevention programme applies to clinical supply."),
    # --- Cytotoxic / hazardous handling (not controlled, but not a routine purchase) ---
    "AOJJSUZBOXZQNB": ("hazardous_cytotoxic", "Doxorubicin: cytotoxic antineoplastic. NIOSH hazardous drug; containment and trained handling required."),
    "FBOZXECLQNJBKD": ("hazardous_cytotoxic", "Methotrexate: cytotoxic antimetabolite and teratogen. NIOSH hazardous drug."),
    "LXZZYRPGZAFOLE": ("hazardous_cytotoxic", "Cisplatin: cytotoxic antineoplastic. NIOSH hazardous drug."),
    "RCINICONZNJXQF": ("hazardous_cytotoxic", "Paclitaxel: cytotoxic antineoplastic. NIOSH hazardous drug."),
    "OGWKCGZFUXNPDA": ("hazardous_cytotoxic", "Vincristine: cytotoxic antineoplastic; fatal if given intrathecally. NIOSH hazardous drug."),
    "VJJPUSNTGOMMGY": ("hazardous_cytotoxic", "Etoposide: cytotoxic antineoplastic. NIOSH hazardous drug."),
    "AHJRHEGDXFFMBM": ("hazardous_cytotoxic", "Carmustine: cytotoxic alkylating agent. NIOSH hazardous drug."),
}

# Name fragments are a fallback for compounds whose structure did not resolve. Deliberately
# coarse and deliberately secondary: a name match is reported with match_basis="name".
_WATCH_NAMES = {
    "fentanyl": "PJMPHNIQZUBGLI", "ketamine": "VCKUSRYTPJJLNI", "morphine": "BQJCRHHNABKAKU",
    "cocaine": "ZPUCINDJVBIVPJ", "methylphenidate": "DUGOZIWVEXMGBE", "amphetamine": "KWTSXDURSIMDCE",
    "diazepam": "AAOVKJBEBIDNHE", "midazolam": "DDLIGBOFAVUZHB", "phenobarbital": "DDBREPKUVSBGFI",
    "pentobarbital": "GVGLGOZIDCSQPN", "thalidomide": "UEJJHQNACJXSKW", "lenalidomide": "GOTYRUGSSMKFNF",
    "pomalidomide": "UVSMNLNDYGZFPF", "tretinoin": "SHGAZHPCJJPHSC", "isotretinoin": "SHGAZHPCJJPHSC",
    "doxorubicin": "AOJJSUZBOXZQNB", "methotrexate": "FBOZXECLQNJBKD", "cisplatin": "LXZZYRPGZAFOLE",
    "paclitaxel": "RCINICONZNJXQF", "vincristine": "OGWKCGZFUXNPDA", "etoposide": "VJJPUSNTGOMMGY",
    "carmustine": "AHJRHEGDXFFMBM",
}


def regulatory_flags(inchikey=None, name=None, synonyms=()):
    """Advisory restriction flags for a compound. Never a clearance.

    Matching is on the InChIKey skeleton (salt- and stereo-insensitive) first, then on
    name/synonym text. Returns a list of flag records; an empty list means *not on this
    list*, which is explicitly not the same as unrestricted.
    """
    flags, seen = [], set()

    def add(skeleton, basis, matched):
        if skeleton in seen:
            return
        seen.add(skeleton)
        category, note = _WATCHLIST[skeleton]
        flags.append({"category": category, "note": note, "match_basis": basis,
                      "matched_on": matched, "disclaimer": REGULATORY_DISCLAIMER})

    if inchikey:
        skel = str(inchikey).split("-")[0].upper()
        if skel in _WATCHLIST:
            add(skel, "inchikey_skeleton", inchikey)

    for text in [name, *(synonyms or [])]:
        if not text:
            continue
        low = str(text).lower()
        for frag, skel in _WATCH_NAMES.items():
            if re.search(rf"\b{re.escape(frag)}\b", low):
                add(skel, "name", text)
    return flags


# --------------------------------------------------------------------------- PubChem vendors (live)

def _pug_view_categories(cid):
    d, e = db.HTTP.json("GET", f"{PUG_VIEW}/categories/compound/{cid}/JSON")
    if d is None:
        return None, e
    return (d.get("SourceCategories") or {}).get("Categories") or [], e


def pubchem_vendors(cid, limit=None):
    """Chemical vendors listing this CID, deduplicated by vendor.

    PubChem returns one record per depositor *substance*, so the same vendor appears
    repeatedly with different catalogue numbers (ibuprofen: 178 records). Records are
    grouped by vendor name; every distinct catalogue number and product URL is kept,
    because a lab ordering needs the specific catalogue number, not just the vendor.

    Returns {'cid', 'vendor_count', 'record_count', 'vendors': [...], 'error'?}.
    """
    cats, err = _pug_view_categories(cid)
    if cats is None:
        return {"cid": cid, "vendor_count": 0, "record_count": 0, "vendors": [],
                "error": err or "no response from PubChem"}

    raw = [s for c in cats if c.get("Category") == VENDOR_CATEGORY for s in (c.get("Sources") or [])]
    grouped = {}
    for s in raw:
        vendor = (s.get("SourceName") or "").strip()
        if not vendor:
            continue
        g = grouped.setdefault(vendor, {
            "vendor": vendor, "vendor_url": s.get("SourceURL"),
            "pubchem_source": s.get("SourceDetail"), "catalog_numbers": [], "product_urls": [],
            "sids": [], "price": None, "price_source": None, "pack_size": None, "purity": None,
            "grade": None, "lead_time": None,
        })
        for key, field in (("catalog_numbers", "RegistryID"), ("product_urls", "SourceRecordURL")):
            val = s.get(field)
            if val and val not in g[key]:
                g[key].append(val)
        if s.get("SID") and s["SID"] not in g["sids"]:
            g["sids"].append(s["SID"])

    vendors = sorted(grouped.values(), key=lambda v: (-len(v["catalog_numbers"]), v["vendor"].lower()))
    for v in vendors:
        v["listings"] = len(v["catalog_numbers"]) or 1
        v["grade_caveat"] = GRADE_CAVEAT
    return {"cid": cid, "vendor_count": len(vendors), "record_count": len(raw),
            "vendors": vendors[:limit] if limit else vendors, "source": "PubChem PUG-View",
            "fields_not_available": ["price", "pack_size", "purity", "grade", "lead_time"]}


# --------------------------------------------------------------------------- Mcule (live lookup)

def mcule_lookup(smiles=None, inchikey=None, limit=5):
    """Keyless Mcule catalogue lookup. Returns Mcule IDs and product URLs, no prices.

    Exercised without credentials: the lookup endpoint answers, the price endpoint 401s.
    """
    query = inchikey or smiles
    if not query:
        return {"hits": [], "error": "no identifier given"}
    d, e = db.HTTP.json("GET", f"{MCULE}/search/lookup/", params={"query": query})
    if d is None:
        return {"hits": [], "provider": "Mcule", **({"error": e} if e else {})}
    hits = [{"mcule_id": r.get("mcule_id"), "url": r.get("url"), "smiles": r.get("smiles")}
            for r in (d.get("results") or [])][:limit]
    return {"hits": hits, "provider": "Mcule", "queried": query,
            "note": "Catalogue presence only. Mcule pricing requires MCULE_API_KEY."}


def mcule_prices(mcule_id, amount_mg=10):
    """Real Mcule price quotes. Key-gated.

    Without MCULE_API_KEY this reports itself unavailable and names the variable, in the
    same style as the rest of the platform's providers. It does not estimate.

    NOT EXERCISED: no MCULE_API_KEY was available in the environment this was written in,
    so the authenticated response shape is taken from Mcule's published API and has not
    been confirmed against a live 200. Treat the parse as unverified until it is.
    """
    key = os.environ.get("MCULE_API_KEY")
    if not key:
        return {"provider": "Mcule", "available": False, "prices": [], "env_var": "MCULE_API_KEY",
                "reason": "MCULE_API_KEY is not set; Mcule price quotes are unavailable.",
                "price": None}
    status, text = db.HTTP.request(
        "GET", f"{MCULE}/compound/{mcule_id}/prices/", params={"amount": amount_mg}, ttl=False)
    if status is None:
        return {"provider": "Mcule", "available": False, "prices": [], "price": None,
                "reason": text, "verified": False}
    if status >= 400:
        return {"provider": "Mcule", "available": False, "prices": [], "price": None,
                "reason": f"HTTP {status} from Mcule", "verified": False}
    import json as _json
    try:
        d = _json.loads(text)
    except ValueError:
        return {"provider": "Mcule", "available": False, "prices": [], "price": None,
                "reason": "unparseable response from Mcule", "verified": False}
    rows = [{"amount_mg": r.get("amount"), "price": r.get("price"), "currency": r.get("currency", "USD"),
             "purity": r.get("purity"), "delivery_days": r.get("delivery_time")}
            for r in (d.get("best_prices") or d.get("results") or [])]
    return {"provider": "Mcule", "available": True, "prices": rows, "mcule_id": mcule_id,
            "price_source": "Mcule API (live quote)", "verified_parse": False}


def price_providers():
    """Which price providers are configured right now, and what would enable the others."""
    out = [{"provider": "Mcule", "configured": bool(os.environ.get("MCULE_API_KEY")),
            "env_var": "MCULE_API_KEY", "status": "implemented, key-gated, parse unverified"}]
    for name in ("molport", "chemspace"):
        ev = PRICING_EVIDENCE[name]
        out.append({"provider": name.capitalize(), "configured": False, "env_var": ev["env_var"],
                    "status": f"not implemented ({ev['verdict']}); no credentials to exercise it"})
    out.append({"provider": "ZINC", "configured": False, "env_var": None,
                "status": "rejected as a price source: " + PRICING_EVIDENCE["zinc_catalogs"]["verdict"]})
    return out


# --------------------------------------------------------------------------- sourcing one compound

def _resolve(smiles=None, inchikey=None, name=None, cid=None):
    """Identity resolution. Exact only -- never falls back to a similar structure."""
    if cid:
        props = (db.pubchem_properties([cid]) or [{}])[0]
        return {"cid": cid, "title": props.get("Title"), "inchikey": props.get("InChIKey"),
                "smiles": props.get("SMILES"), "formula": props.get("MolecularFormula"),
                "mw": float(props["MolecularWeight"]) if props.get("MolecularWeight") else None,
                "match": "exact" if props else "none"}
    ident = db.pubchem_identify(smiles=smiles, inchikey=inchikey, name=name,
                                synonyms=8, activity=False, similar=False)
    return {"cid": ident.get("cid"), "title": ident.get("title"), "inchikey": ident.get("inchikey"),
            "smiles": ident.get("smiles") or smiles, "formula": ident.get("formula"),
            "mw": ident.get("mw"), "match": ident.get("match"),
            "synonyms": ident.get("synonyms", []), **({"error": ident["error"]} if ident.get("error") else {})}


def source_compound(smiles=None, inchikey=None, name=None, cid=None, label=None,
                    vendor_limit=10, use_mcule=True, price=True):
    """Full sourcing report for ONE compound: identity, vendors, prices, restrictions.

    Exact identity only. A compound PubChem does not know returns
    ``sourceable=False`` with an empty vendor list. It never substitutes a neighbour --
    call ``similar_available_compounds()`` explicitly if that is wanted.
    """
    rec = {
        "schema_version": SCHEMA_VERSION,
        "label": label or name or inchikey or (smiles[:40] if smiles else None) or cid,
        "query": {"smiles": smiles, "inchikey": inchikey, "name": name, "cid": cid},
        "retrieved_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "identity": None, "sourceable": False, "vendor_count": 0, "vendors": [],
        "offers_with_price": 0, "price_status": "unknown", "prices": [],
        "regulatory_flags": [], "grade_caveat": GRADE_CAVEAT, "notes": [],
    }

    ident = _resolve(smiles=smiles, inchikey=inchikey, name=name, cid=cid)
    rec["identity"] = ident

    rec["regulatory_flags"] = regulatory_flags(
        inchikey=ident.get("inchikey") or inchikey,
        name=name or ident.get("title"), synonyms=ident.get("synonyms", ()))

    if not ident.get("cid"):
        rec["notes"].append(
            "Not found in PubChem by exact structure/identifier. No vendor can be listed for it. "
            "This is the expected result for a novel design and is NOT an error.")
        rec["price_status"] = "no_supplier"
        return rec

    vend = pubchem_vendors(ident["cid"], limit=vendor_limit)
    if vend.get("error"):
        rec["notes"].append(f"PubChem vendor lookup failed: {vend['error']}")
        rec["price_status"] = "lookup_failed"
        return rec

    rec["vendors"] = vend["vendors"]
    rec["vendor_count"] = vend["vendor_count"]
    rec["vendor_records"] = vend["record_count"]
    rec["sourceable"] = vend["vendor_count"] > 0
    rec["fields_not_available"] = vend["fields_not_available"]

    if use_mcule and (ident.get("inchikey") or ident.get("smiles")):
        mc = mcule_lookup(smiles=ident.get("smiles"), inchikey=ident.get("inchikey"))
        rec["mcule"] = mc
        if mc.get("hits"):
            rec["notes"].append(f"Mcule lists {len(mc['hits'])} matching catalogue entr"
                                f"{'y' if len(mc['hits']) == 1 else 'ies'} (no price without a key).")

    if not rec["sourceable"]:
        rec["price_status"] = "no_supplier"
        rec["notes"].append("PubChem knows this compound but lists no chemical vendor for it.")
        return rec

    if price:
        quotes = []
        mc_hits = (rec.get("mcule") or {}).get("hits") or []
        if mc_hits:
            q = mcule_prices(mc_hits[0]["mcule_id"])
            quotes.append(q)
        rec["prices"] = [q for q in quotes if q.get("prices")]
        rec["offers_with_price"] = sum(len(q.get("prices") or []) for q in quotes)
        if rec["offers_with_price"]:
            rec["price_status"] = "quoted"
        else:
            rec["price_status"] = "unavailable_no_provider"
            rec["notes"].append(NO_PRICE_REASON)
    else:
        rec["price_status"] = "not_requested"

    if rec["regulatory_flags"]:
        rec["notes"].append(
            f"RESTRICTED: {len(rec['regulatory_flags'])} advisory flag(s). This compound must not "
            "be treated as a routine catalogue purchase; see regulatory_flags.")
    return rec


def similar_available_compounds(smiles, threshold=90, limit=5, vendor_limit=3):
    """Purchasable structural neighbours. Explicitly NOT the queried compound.

    A separate call on purpose. Every record carries ``is_not_your_compound=True`` and a
    warning, and nothing here is ever merged into a BOM line. A neighbour is a lead for a
    chemist to consider, not a substitute to order.
    """
    near = db.pubchem_similar(smiles, threshold=threshold, limit=limit)
    out = {"query_smiles": smiles, "threshold_pct": threshold, "neighbours": [],
           "warning": "THESE ARE DIFFERENT MOLECULES FROM THE ONE YOU ASKED FOR. They are "
                      "structural neighbours offered as leads. Never order one as a "
                      "substitute for the query compound.",
           **({"error": near["error"]} if near.get("error") else {})}
    for props in db.pubchem_properties(near.get("cids", [])):
        cid = props.get("CID")
        v = pubchem_vendors(cid, limit=vendor_limit)
        out["neighbours"].append({
            "is_not_your_compound": True, "cid": cid, "title": props.get("Title"),
            "smiles": props.get("SMILES"), "inchikey": props.get("InChIKey"),
            "vendor_count": v.get("vendor_count", 0), "vendors": v.get("vendors", []),
            "regulatory_flags": regulatory_flags(inchikey=props.get("InChIKey"), name=props.get("Title")),
        })
    return out


# --------------------------------------------------------------------------- bill of materials

def bill_of_materials(compounds, vendor_limit=5, price=True, use_mcule=True, label_key=None):
    """Cost a research plan: what is sourceable, from where, and what is unknown.

    ``compounds`` is a list of dicts. Each may carry any of ``smiles``/``canonical_smiles``/
    ``canonical``, ``inchikey``, ``name``, ``cid``, plus an optional ``label`` and
    ``amount_mg``. Inventory records from data/extracted_compound_inventory.json are
    accepted as-is.

    The totals are deliberately unflattering. ``estimated_total`` is only ever a real sum
    of real quotes, and ``priced_lines``/``unpriced_lines`` always accompany it, so a BOM
    that priced nothing reports a total of 0.0 over 0 priced lines rather than a plausible
    number. There is no extrapolation from a priced line to an unpriced one.
    """
    lines, seen = [], set()
    for c in compounds:
        smi = c.get("smiles") or c.get("canonical_smiles") or c.get("canonical")
        ik = c.get("inchikey") or (c.get("profile") or {}).get("inchikey")
        name, cid = c.get("name"), c.get("cid")
        label = c.get(label_key) if label_key else None
        label = label or c.get("label") or name or c.get("compound_id") or c.get("id")

        key = (smi, ik, name, cid)
        if key in seen:
            continue
        seen.add(key)

        rec = source_compound(smiles=smi, inchikey=ik, name=name, cid=cid, label=str(label),
                              vendor_limit=vendor_limit, use_mcule=use_mcule, price=price)
        rec["amount_mg_requested"] = c.get("amount_mg")
        rec["line_cost"] = None          # only ever set from a real quote
        rec["line_cost_source"] = None
        for q in rec.get("prices") or []:
            for p in q.get("prices") or []:
                if p.get("price") is not None:
                    rec["line_cost"] = p["price"]
                    rec["line_cost_source"] = q.get("price_source")
                    break
            if rec["line_cost"] is not None:
                break
        lines.append(rec)

    sourceable = [l for l in lines if l["sourceable"]]
    unsourceable = [l for l in lines if not l["sourceable"]]
    priced = [l for l in lines if l["line_cost"] is not None]
    restricted = [l for l in lines if l["regulatory_flags"]]
    failed = [l for l in lines if l["price_status"] == "lookup_failed"]

    providers = price_providers()
    configured = [p["provider"] for p in providers if p["configured"]]

    bom = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "summary": {
            "compounds": len(lines),
            "sourceable": len(sourceable),
            "not_sourceable": len(unsourceable),
            "lookup_failed": len(failed),
            "priced_lines": len(priced),
            "unpriced_lines": len(lines) - len(priced),
            "restricted_lines": len(restricted),
            "estimated_total": round(sum(l["line_cost"] for l in priced), 2) if priced else 0.0,
            "currency": "USD" if priced else None,
            "total_covers": f"{len(priced)} of {len(lines)} lines",
        },
        "price_providers_configured": configured or None,
        "price_status": ("partial" if priced and len(priced) < len(lines)
                         else "complete" if priced else "unavailable"),
        "lines": lines,
        "grade_caveat": GRADE_CAVEAT,
        "regulatory_disclaimer": REGULATORY_DISCLAIMER,
        "ordering_boundary": "This is a sourcing document, not an order. Nothing here has been "
                             "purchased, reserved or submitted to any vendor.",
        "caveats": [],
    }

    if not priced:
        bom["caveats"].append(
            f"NO PRICING: 0 of {len(lines)} lines carry a price. {NO_PRICE_REASON} "
            "The total below is 0.0 because nothing was priced, not because anything is free.")
    elif len(priced) < len(lines):
        bom["caveats"].append(
            f"PARTIAL PRICING: the total covers {len(priced)} of {len(lines)} lines. "
            "The remaining lines have no price and have NOT been estimated.")
    if unsourceable:
        bom["caveats"].append(
            f"{len(unsourceable)} compound(s) have no listed supplier. For novel designs this is "
            "expected: they would have to be custom-synthesised, which is quoted separately and "
            "is not costed here.")
    if restricted:
        names = ", ".join(sorted({str(l["label"]) for l in restricted}))
        bom["caveats"].append(
            f"RESTRICTED COMPOUNDS ON THIS BOM: {names}. These are not routine purchases. "
            + REGULATORY_DISCLAIMER)
    if failed:
        bom["caveats"].append(
            f"{len(failed)} line(s) could not be checked because a lookup failed. They are counted "
            "as not sourceable, which may understate availability. Re-run when the network is up.")
    return bom


# --------------------------------------------------------------------------- request for quotation

RFQ_BOUNDARY = (
    "THIS IS A DRAFT REQUEST FOR A HUMAN TO REVIEW AND SEND. It is not an order, it has not "
    "been sent to anyone, and this software cannot send it. No vendor has been contacted and "
    "no account, cart or purchase system has been touched."
)


def request_for_quote(bom, requester=None, organisation=None, purpose=None):
    """Turn a BOM into a per-vendor RFQ a person checks and sends themselves.

    This is the actionable output when pricing is unavailable, which is the normal case.
    It asks the vendor for exactly what the free APIs cannot give: price, pack size,
    purity, grade, lot documentation and lead time.
    """
    by_vendor = {}
    for line in bom.get("lines", []):
        if not line.get("sourceable"):
            continue
        for v in line.get("vendors", []):
            entry = by_vendor.setdefault(v["vendor"], {
                "vendor": v["vendor"], "vendor_url": v.get("vendor_url"), "items": []})
            entry["items"].append({
                "compound": line["label"],
                "pubchem_cid": (line.get("identity") or {}).get("cid"),
                "inchikey": (line.get("identity") or {}).get("inchikey"),
                "catalog_numbers": v.get("catalog_numbers", []),
                "product_urls": v.get("product_urls", []),
                "amount_requested_mg": line.get("amount_mg_requested"),
                "restrictions_flagged": [f["category"] for f in line.get("regulatory_flags", [])],
            })

    questions = [
        "Unit price and available pack sizes for the quantity indicated.",
        "Purity (% and method) and whether a Certificate of Analysis is supplied.",
        "Grade: research/reagent vs pharmaceutical/GMP, and the applicable specification.",
        "Salt form, solvate and actual free-base content.",
        "Lead time, stock location and whether the item is in stock or made to order.",
        "Any licence, permit, end-use declaration or export documentation required.",
        "Shipping, cold-chain and hazardous-goods handling requirements and cost.",
    ]

    restricted = [l for l in bom.get("lines", []) if l.get("regulatory_flags")]
    return {
        "schema_version": SCHEMA_VERSION,
        "document_type": "request_for_quotation_draft",
        "boundary": RFQ_BOUNDARY,
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "requester": requester, "organisation": organisation, "purpose": purpose,
        "vendors": sorted(by_vendor.values(), key=lambda v: -len(v["items"])),
        "vendor_count": len(by_vendor),
        "questions_for_vendor": questions,
        "compliance_note": (
            f"{len(restricted)} item(s) on this request carry advisory restriction flags. "
            "Confirm your institution's authorisation BEFORE sending this request. "
            + REGULATORY_DISCLAIMER) if restricted else REGULATORY_DISCLAIMER,
        "grade_note": GRADE_CAVEAT,
        "not_covered": [l["label"] for l in bom.get("lines", []) if not l.get("sourceable")],
    }


def render_bom_text(bom, max_vendors=3):
    """Plain-text BOM for a terminal or an email. Same honesty as the JSON."""
    s = bom["summary"]
    out = [
        "BILL OF MATERIALS - compound sourcing",
        f"generated {bom['generated_utc']}  schema {bom['schema_version']}",
        "",
        f"  compounds          {s['compounds']}",
        f"  sourceable         {s['sourceable']}",
        f"  not sourceable     {s['not_sourceable']}",
        f"  restricted         {s['restricted_lines']}",
        f"  priced lines       {s['priced_lines']} of {s['compounds']}",
        f"  estimated total    {s['estimated_total']} {s['currency'] or '(no currency: nothing priced)'}"
        f"   [covers {s['total_covers']}]",
        f"  price providers    {bom['price_providers_configured'] or 'none configured'}",
        "",
    ]
    for line in bom["lines"]:
        ident = line.get("identity") or {}
        head = f"- {line['label']}"
        if ident.get("cid"):
            head += f"  (CID {ident['cid']}{', ' + ident['title'] if ident.get('title') else ''})"
        out.append(head)
        if line["sourceable"]:
            names = ", ".join(v["vendor"] for v in line["vendors"][:max_vendors])
            more = line["vendor_count"] - min(max_vendors, len(line["vendors"]))
            out.append(f"    vendors: {line['vendor_count']}  ({names}{f', +{more} more' if more > 0 else ''})")
            first = line["vendors"][0] if line["vendors"] else None
            if first and first.get("catalog_numbers"):
                out.append(f"    e.g. {first['vendor']} cat# {first['catalog_numbers'][0]}")
            out.append(f"    price:   {line['line_cost'] if line['line_cost'] is not None else 'NOT AVAILABLE'}"
                       + ("" if line["line_cost"] is not None else "  (no price provider configured)"))
        else:
            out.append("    vendors: NONE - no supplier lists this structure")
        for f in line.get("regulatory_flags", []):
            out.append(f"    ** {f['category'].upper()}: {f['note']}")
    if bom.get("caveats"):
        out += ["", "CAVEATS"] + [f"  ! {c}" for c in bom["caveats"]]
    out += ["", bom["ordering_boundary"]]
    return "\n".join(out)
