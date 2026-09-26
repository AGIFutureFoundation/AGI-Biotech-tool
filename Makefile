# One entry point for every check, so an agent, CI and a person all run the
# same thing. Always the venv interpreter: the system python has neither rdkit
# nor pytest, and several modules degrade quietly when an import fails, so the
# wrong interpreter produces a passing run that proves nothing.
PY := .venv/bin/python

.PHONY: help test imports reachable citations verify inventory serve
.DEFAULT_GOAL := help

help:
	@echo "make test       full pytest suite"
	@echo "make imports    every module under server/ and scripts/ imports"
	@echo "make reachable  no orphaned JS modules"
	@echo "make citations  every identifier in all 5 panels resolves (hits the network)"
	@echo "make verify     test + imports + reachable"
	@echo "make inventory  rebuild the compound inventory from FILES=..."
	@echo "make anchor     build an unsigned Monad anchor for RESULTS=..."
	@echo "make serve      run the app on http://localhost:8000"

test:
	$(PY) -m pytest tests/ -q

# The single check that would have caught this repo's three worst bugs: an API
# layer that raised NameError on import, a module missing a typing import, and
# a dependency that was never declared.
imports:
	$(PY) -m pytest tests/test_module_imports.py -q

reachable:
	$(PY) scripts/check_reachable.py

citations:
	@test -f scripts/verify_panel_citations.py \
		|| { echo "scripts/verify_panel_citations.py not present yet"; exit 1; }
	$(PY) scripts/verify_panel_citations.py

verify: test imports reachable

inventory:
	@test -n "$(FILES)" || { echo 'usage: make inventory FILES="a.pdf b.pdf"'; exit 1; }
	$(PY) scripts/build_compound_inventory.py $(FILES)

# Builds an UNSIGNED transaction and stops. No key is read and nothing is sent.
# Exits 1 when the run holds synthetic values, which is a refusal, not an error.
anchor:
	@test -n "$(RESULTS)" || { echo 'usage: make anchor RESULTS=run.json [LABEL=name]'; exit 1; }
	$(PY) scripts/anchor_run.py $(RESULTS) $(if $(LABEL),--label $(LABEL),)

serve:
	$(PY) server/server.py
