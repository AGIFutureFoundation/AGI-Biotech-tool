"""The guarantees that make server/compound_sourcing.py safe to order from.

This module's output is a procurement document. A person reads it, and then
spends money and handles chemicals on the strength of it. The failure modes that
matter are therefore not crashes -- they are outputs that stay *plausible* while
being wrong:

  1. A near-neighbour quietly appearing where the queried compound should be, so
     a lab orders a different molecule than the one it designed.
  2. A catalogue listing reading as a clinical-grade product.
  3. An empty regulatory_flags list reading as "cleared to buy".
  4. A dollar total that was extrapolated rather than quoted.
  5. A draft RFQ reading as an order that was actually placed.

Each of those is a wrong number or a wrong absence, not an exception, so nothing
upstream would catch it. These tests pin the behaviour that prevents them.

Everything here is offline. db_clients is stubbed at the boundary
(HTTP.json / HTTP.request / pubchem_*) so the real parsing, grouping, flagging
and totalling code runs, but no network does.
"""
import re

import pytest

import compound_sourcing as cs
import db_clients as db


# --------------------------------------------------------------------------- offline stubs

#: A PubChem PUG-View payload with three vendor records spread over two vendors,
#: which is the shape that actually matters: PubChem returns one record per
#: depositor substance, so a single vendor recurs with different catalogue
#: numbers and must be collapsed without losing any of them.
VENDOR_CATEGORIES = {
    "SourceCategories": {
        "Categories": [
            {
                "Category": "Chemical Vendors",
                "Sources": [
                    {"SourceName": "Acme Fine Chemicals", "SourceURL": "https://acme.example",
                     "SourceDetail": "Acme", "RegistryID": "ACM-001",
                     "SourceRecordURL": "https://acme.example/ACM-001", "SID": 111},
                    {"SourceName": "Acme Fine Chemicals", "SourceURL": "https://acme.example",
                     "SourceDetail": "Acme", "RegistryID": "ACM-002",
                     "SourceRecordURL": "https://acme.example/ACM-002", "SID": 112},
                    {"SourceName": "Beta Reagents", "SourceURL": "https://beta.example",
                     "SourceDetail": "Beta", "RegistryID": "BR-9", "SID": 113},
                ],
            },
            # A non-vendor category that must never be read as a supplier.
            {"Category": "Research and Development",
             "Sources": [{"SourceName": "Some University Lab", "RegistryID": "X"}]},
        ]
    }
}


@pytest.fixture
def offline(monkeypatch):
    """Stub every db_clients entry point compound_sourcing reaches for.

    Returns a dict the test can mutate to steer identity resolution, so each
    test states the world it is asserting about rather than sharing one.
    """
    world = {
        "identify": {"cid": 2244, "title": "Aspirin",
                     "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
                     "smiles": "CC(=O)Oc1ccccc1C(=O)O", "formula": "C9H8O4",
                     "mw": 180.16, "match": "exact", "synonyms": ["acetylsalicylic acid"]},
        "categories": VENDOR_CATEGORIES,
        "categories_error": None,
        "mcule_results": [],
        "similar_cids": [],
        "properties": {},
    }

    def fake_json(method, url, params=None, **kw):
        if "pug_view" in url:
            if world["categories_error"]:
                return None, world["categories_error"]
            return world["categories"], None
        if "mcule.com" in url:
            return {"results": world["mcule_results"]}, None
        raise AssertionError(f"unstubbed HTTP call: {method} {url}")

    def fake_request(method, url, **kw):
        raise AssertionError(f"unstubbed HTTP.request: {method} {url}")

    def fake_properties(cids):
        """Property records for a CID lookup.

        _resolve() takes a different branch for cid= than for smiles=/name=, so
        this has to answer with a full record, not a bare CID. Unless a test
        pins a specific CID in world["properties"], the record is derived from
        world["identify"] -- which keeps the two resolution paths describing the
        same compound instead of silently diverging.
        """
        out = []
        for c in cids:
            if c in world["properties"]:
                out.append(world["properties"][c])
                continue
            base = world["identify"]
            out.append({"CID": c, "Title": base.get("title"),
                        "InChIKey": base.get("inchikey"), "SMILES": base.get("smiles"),
                        "MolecularFormula": base.get("formula"),
                        "MolecularWeight": str(base["mw"]) if base.get("mw") else None})
        return out

    monkeypatch.setattr(db.HTTP, "json", fake_json)
    monkeypatch.setattr(db.HTTP, "request", fake_request)
    monkeypatch.setattr(db, "pubchem_identify", lambda **kw: dict(world["identify"]))
    monkeypatch.setattr(db, "pubchem_properties", fake_properties)
    monkeypatch.setattr(db, "pubchem_similar",
                        lambda smiles, threshold=90, limit=5: {"cids": world["similar_cids"]})
    # MCULE_API_KEY leaking in from the developer's environment would change the
    # price path under test, so it is removed for every test in this module.
    monkeypatch.delenv("MCULE_API_KEY", raising=False)
    return world


# --------------------------------------------------------------------------- 1. no silent substitution

def test_unknown_compound_is_not_sourceable_and_lists_no_vendor(offline):
    """A novel design must come back empty-handed, not with somebody else's vendors.

    This is the single most dangerous substitution: a compound PubChem has never
    seen resolving to the nearest thing it has, and a lab ordering that instead.
    """
    offline["identify"] = {"cid": None, "match": "none"}

    rec = cs.source_compound(smiles="CC(C)(C)N1C=NC2=C1C(=O)NC(=O)N2C", label="AGI-novel-1")

    assert rec["sourceable"] is False
    assert rec["vendors"] == []
    assert rec["vendor_count"] == 0
    assert rec["price_status"] == "no_supplier"
    # And it must say *why*, in terms that do not read as a failure of the run.
    assert any("NOT an error" in n for n in rec["notes"])


def test_source_compound_never_calls_the_similarity_endpoint(offline, monkeypatch):
    """Exact identity only -- enforced at the seam, not just by convention.

    If a future edit adds a similarity fallback inside source_compound(), this
    fails, which is the point: the substitution guarantee should not depend on
    somebody re-reading the docstring.
    """
    offline["identify"] = {"cid": None, "match": "none"}

    def forbidden(*a, **kw):
        raise AssertionError("source_compound reached for a structural neighbour")

    monkeypatch.setattr(db, "pubchem_similar", forbidden)
    rec = cs.source_compound(smiles="CCO", label="whatever")
    assert rec["sourceable"] is False


def test_neighbours_are_labelled_as_different_molecules(offline):
    """Every neighbour record must carry its own disclaimer, not rely on the caller."""
    offline["similar_cids"] = [1983, 3672]
    offline["properties"] = {
        1983: {"CID": 1983, "Title": "Acetaminophen", "SMILES": "CC(=O)Nc1ccc(O)cc1",
               "InChIKey": "RZVAJINKPMORJF-UHFFFAOYSA-N"},
        3672: {"CID": 3672, "Title": "Ibuprofen", "SMILES": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
               "InChIKey": "HEFNNWSXXWATRW-UHFFFAOYSA-N"},
    }

    out = cs.similar_available_compounds("CC(=O)Oc1ccccc1C(=O)O")

    assert "DIFFERENT MOLECULES" in out["warning"]
    assert len(out["neighbours"]) == 2
    for n in out["neighbours"]:
        assert n["is_not_your_compound"] is True
    # The query itself is echoed so a reader can see what these are neighbours *of*.
    assert out["query_smiles"] == "CC(=O)Oc1ccccc1C(=O)O"


def test_neighbour_records_are_not_bom_lines(offline):
    """A neighbour must not be shaped like something bill_of_materials would accept.

    Structural: if a neighbour ever grew the keys of a BOM line, a caller
    splicing the two lists together would silently produce an orderable line for
    a molecule nobody asked for.
    """
    offline["similar_cids"] = [1983]
    offline["properties"] = {1983: {"CID": 1983, "Title": "Acetaminophen",
                                    "InChIKey": "RZVAJINKPMORJF-UHFFFAOYSA-N"}}

    neighbour = cs.similar_available_compounds("CC(=O)Oc1ccccc1C(=O)O")["neighbours"][0]

    for orderable_key in ("line_cost", "amount_mg_requested", "sourceable"):
        assert orderable_key not in neighbour


# --------------------------------------------------------------------------- 2. catalogue != clinical

def test_every_vendor_carries_the_grade_caveat(offline):
    """PubChem has no purity/grade field, so every listing must say so on its face."""
    rec = cs.source_compound(cid=2244, label="Aspirin")

    assert rec["sourceable"] is True
    for v in rec["vendors"]:
        assert v["grade_caveat"] == cs.GRADE_CAVEAT
        # The fields a buyer needs and PubChem cannot supply are present-but-None,
        # never absent: an absent key reads as "not applicable", None reads as "unknown".
        for unknown in ("price", "pack_size", "purity", "grade", "lead_time"):
            assert v[unknown] is None
    assert set(rec["fields_not_available"]) == {"price", "pack_size", "purity",
                                                "grade", "lead_time"}


def test_vendors_are_grouped_without_losing_catalogue_numbers(offline):
    """Dedup by vendor must keep every catalogue number: a lab orders by number."""
    rec = cs.source_compound(cid=2244)

    assert rec["vendor_count"] == 2          # two vendors
    assert rec["vendor_records"] == 3        # from three PubChem records
    acme = next(v for v in rec["vendors"] if v["vendor"] == "Acme Fine Chemicals")
    assert acme["catalog_numbers"] == ["ACM-001", "ACM-002"]
    assert acme["sids"] == [111, 112]


def test_non_vendor_categories_are_not_read_as_suppliers(offline):
    """Only the 'Chemical Vendors' category is a supplier; a research lab is not."""
    rec = cs.source_compound(cid=2244)
    assert all(v["vendor"] != "Some University Lab" for v in rec["vendors"])


# --------------------------------------------------------------------------- 3. flags are advisory

def test_watchlist_hit_is_advisory_and_never_a_clearance(offline):
    """A flagged compound carries the disclaimer on the flag itself."""
    flags = cs.regulatory_flags(inchikey="PJMPHNIQZUBGLI-UHFFFAOYSA-N")

    assert len(flags) == 1
    assert flags[0]["category"] == "controlled_substance"
    assert flags[0]["match_basis"] == "inchikey_skeleton"
    assert flags[0]["disclaimer"] == cs.REGULATORY_DISCLAIMER
    assert "NOT evidence that a compound is unrestricted" in cs.REGULATORY_DISCLAIMER


def test_no_flag_is_not_a_clearance(offline):
    """The empty case is the dangerous one: it must be empty, not a 'cleared' record."""
    assert cs.regulatory_flags(inchikey="BSYNRYMUTXBXSQ-UHFFFAOYSA-N", name="Aspirin") == []


def test_flag_matches_salts_and_stereoisomers_of_the_same_parent(offline):
    """Skeleton matching is the whole point: a hydrochloride is still controlled.

    Scheduling attaches to the parent, so a flag keyed on the full InChIKey would
    miss every salt form -- which is how most of these are actually sold.
    """
    parent = cs.regulatory_flags(inchikey="VCKUSRYTPJJLNI-UHFFFAOYSA-N")
    salt = cs.regulatory_flags(inchikey="VCKUSRYTPJJLNI-ABCDEFGHIJ-N")

    assert parent and salt
    assert parent[0]["note"] == salt[0]["note"]


def test_name_fallback_is_reported_as_a_weaker_basis(offline):
    """A name match must not masquerade as a structural one."""
    flags = cs.regulatory_flags(name="thalidomide")

    assert len(flags) == 1
    assert flags[0]["match_basis"] == "name"
    assert flags[0]["category"] == "restricted_distribution"


def test_a_compound_is_flagged_once_even_when_several_fields_match(offline):
    """Name + synonym + InChIKey all hitting must not produce three identical flags."""
    flags = cs.regulatory_flags(inchikey="UEJJHQNACJXSKW-UHFFFAOYSA-N",
                                name="Thalidomide", synonyms=["thalidomide", "Contergan"])
    assert len(flags) == 1


def test_name_matching_is_word_bounded(offline):
    """Pins a real limitation rather than implying the name list is exhaustive.

    ``\\bfentanyl\\b`` does not match inside 'norfentanyl' or 'carfentanil'. That
    is a deliberate trade-off -- a substring match on these fragments would flag
    unrelated compounds -- but it means the name path has false negatives, which
    is exactly why REGULATORY_DISCLAIMER says absence of a flag proves nothing.
    """
    assert cs.regulatory_flags(name="fentanyl citrate")      # bounded word: matches
    assert cs.regulatory_flags(name="norfentanyl") == []     # substring: does not


def test_every_name_fragment_points_at_a_real_watchlist_entry():
    """A typo in _WATCH_NAMES would KeyError at flag time, on a restricted compound.

    Data integrity, checked once here rather than discovered in production on the
    one code path where being wrong matters most.
    """
    for fragment, skeleton in cs._WATCH_NAMES.items():
        assert skeleton in cs._WATCHLIST, f"{fragment!r} -> unknown skeleton {skeleton!r}"


def test_watchlist_keys_are_inchikey_skeletons():
    """14 uppercase letters. A full InChIKey here would silently never match."""
    for skeleton in cs._WATCHLIST:
        assert re.fullmatch(r"[A-Z]{14}", skeleton), skeleton


def test_restricted_compound_is_called_out_in_its_own_record(offline):
    """The flag must surface in notes too -- a reader skimming notes must not miss it."""
    offline["identify"] = {"cid": 5288826, "title": "Morphine",
                           "inchikey": "BQJCRHHNABKAKU-KBQPJGBKSA-N",
                           "smiles": "CN1CC[C@]23...", "match": "exact", "synonyms": []}

    rec = cs.source_compound(cid=5288826, label="Morphine")

    assert rec["regulatory_flags"]
    assert any("RESTRICTED" in n for n in rec["notes"])


# --------------------------------------------------------------------------- 4. no invented money

def test_unpriced_bom_reports_zero_and_says_why(offline):
    """0.0 must be readable as 'nothing was priced', never as 'nothing costs anything'."""
    bom = cs.bill_of_materials([{"cid": 2244, "label": "Aspirin"}])

    s = bom["summary"]
    assert s["priced_lines"] == 0
    assert s["estimated_total"] == 0.0
    assert s["currency"] is None          # no currency on a total that isn't money
    assert bom["price_status"] == "unavailable"
    assert any("not because anything is free" in c for c in bom["caveats"])


def test_total_covers_states_its_own_coverage(offline):
    """The total is always accompanied by what fraction of lines it covers."""
    bom = cs.bill_of_materials([{"cid": 2244, "label": "A"}, {"cid": 1983, "label": "B"}])
    assert bom["summary"]["total_covers"] == "0 of 2 lines"


def test_unpriced_lines_are_never_extrapolated_from_priced_ones(offline, monkeypatch):
    """One real quote must not spread across the other lines."""
    monkeypatch.setattr(cs, "mcule_prices", lambda mid, amount_mg=10: {
        "provider": "Mcule", "available": True, "price_source": "Mcule API (live quote)",
        "prices": [{"amount_mg": 10, "price": 42.0, "currency": "USD"}]})
    offline["mcule_results"] = [{"mcule_id": "MCULE-1", "url": "https://mcule.example/1",
                                 "smiles": "CC(=O)Oc1ccccc1C(=O)O"}]

    bom = cs.bill_of_materials([{"cid": 2244, "label": "A"}, {"cid": 1983, "label": "B"}])

    assert bom["summary"]["priced_lines"] == 2
    assert bom["summary"]["estimated_total"] == 84.0
    # Every counted dollar traces to a named source on its own line.
    for line in bom["lines"]:
        if line["line_cost"] is not None:
            assert line["line_cost_source"] == "Mcule API (live quote)"


def test_partial_pricing_is_announced(offline, monkeypatch):
    """A total covering some lines must say so rather than presenting as complete."""
    calls = {"n": 0}

    def sometimes(mid, amount_mg=10):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"provider": "Mcule", "available": True, "price_source": "Mcule API",
                    "prices": [{"amount_mg": 10, "price": 10.0, "currency": "USD"}]}
        return {"provider": "Mcule", "available": False, "prices": [], "price": None}

    monkeypatch.setattr(cs, "mcule_prices", sometimes)
    offline["mcule_results"] = [{"mcule_id": "MCULE-1", "url": "u", "smiles": "s"}]

    bom = cs.bill_of_materials([{"cid": 2244, "label": "A"}, {"cid": 1983, "label": "B"}])

    assert bom["price_status"] == "partial"
    assert bom["summary"]["estimated_total"] == 10.0
    assert any("have NOT been estimated" in c for c in bom["caveats"])


def test_failed_lookup_is_not_silently_counted_as_unavailable(offline):
    """A network failure must be distinguishable from a genuine absence of suppliers.

    Both produce sourceable=False, and conflating them would let an outage read
    as 'no vendor sells this'.
    """
    offline["categories_error"] = "connection refused"

    bom = cs.bill_of_materials([{"cid": 2244, "label": "Aspirin"}])

    assert bom["summary"]["lookup_failed"] == 1
    assert any("may understate availability" in c for c in bom["caveats"])


def test_restricted_lines_are_named_in_the_bom_caveats(offline):
    """A buyer reading only the summary must still see which lines are restricted."""
    offline["identify"] = {"cid": 5288826, "title": "Morphine",
                           "inchikey": "BQJCRHHNABKAKU-KBQPJGBKSA-N", "match": "exact",
                           "synonyms": []}

    bom = cs.bill_of_materials([{"cid": 5288826, "label": "Morphine"}])

    assert bom["summary"]["restricted_lines"] == 1
    assert any("RESTRICTED COMPOUNDS ON THIS BOM" in c and "Morphine" in c
               for c in bom["caveats"])


def test_duplicate_compounds_are_costed_once(offline):
    """The same compound listed twice must not double the total."""
    bom = cs.bill_of_materials([{"cid": 2244, "label": "A"}, {"cid": 2244, "label": "A again"}])
    assert bom["summary"]["compounds"] == 1


def test_zinc_is_recorded_as_a_rejected_price_source():
    """The rejection is evidence-bearing, so the evidence must survive in the code.

    ZINC returns a constant price=240/10mg across unrelated compounds -- a schema
    default, not a quote. Anyone re-adding it should have to read why it went.
    """
    zinc = cs.PRICING_EVIDENCE["zinc_catalogs"]
    assert "REJECTED" in zinc["verdict"]
    assert "price field discarded at parse" in zinc["verdict"]
    assert all(p["provider"] != "ZINC" or not p["configured"] for p in cs.price_providers())


def test_mcule_reports_itself_unavailable_without_a_key(offline):
    """No key must mean no price -- never a guess, and it must name the variable."""
    q = cs.mcule_prices("MCULE-1")
    assert q["available"] is False
    assert q["price"] is None
    assert q["env_var"] == "MCULE_API_KEY"


# --------------------------------------------------------------------------- 5. RFQ is not an order

def test_rfq_states_that_nothing_was_sent(offline):
    """The draft must be unmistakably a draft, on the document itself."""
    bom = cs.bill_of_materials([{"cid": 2244, "label": "Aspirin"}])
    rfq = cs.request_for_quote(bom, requester="A Person", organisation="A Lab")

    blob = repr(rfq)
    assert "not an order" in cs.RFQ_BOUNDARY
    assert "cannot send it" in cs.RFQ_BOUNDARY
    assert cs.RFQ_BOUNDARY in blob


def test_bom_states_the_ordering_boundary(offline):
    """The BOM itself says nothing was purchased or reserved."""
    bom = cs.bill_of_materials([{"cid": 2244, "label": "Aspirin"}])
    assert "not an order" in bom["ordering_boundary"]
    assert bom["grade_caveat"] == cs.GRADE_CAVEAT
    assert bom["regulatory_disclaimer"] == cs.REGULATORY_DISCLAIMER


def test_unsourceable_lines_do_not_reach_the_rfq(offline):
    """You cannot ask a vendor to quote something no vendor lists."""
    offline["identify"] = {"cid": None, "match": "none"}

    bom = cs.bill_of_materials([{"smiles": "CCOCC", "label": "AGI-novel"}])
    rfq = cs.request_for_quote(bom)

    assert bom["summary"]["not_sourceable"] == 1
    assert "AGI-novel" not in repr(rfq.get("vendors", rfq))
