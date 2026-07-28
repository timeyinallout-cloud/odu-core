# Build entry point.
#
# The generated artifacts have a strict order: everything derives from
# data/principal_odu.json, so a change there has to flow outward through the
# 256-figure dataset before anything else is rebuilt. Encoding that order here
# means it cannot be got wrong by running the scripts in the wrong sequence.
#
#   make            build everything
#   make test       Python and TypeScript suites
#   make check      validate content files and report verification coverage
#   make clean      remove derived artifacts

PY      := python3
TSC     := ./node_modules/.bin/tsc
DATA    := data/principal_odu.json
DERIVED := data/odu_256.json

.DEFAULT_GOAL := build
.PHONY: build test check clean site web ts kb parity verify serve-site serve-web

build: $(DERIVED) kb site web ts

# Everything downstream depends on this, so it is a real file target rather
# than a phony one — nothing rebuilds if the canonical data has not changed.
$(DERIVED): $(DATA) scripts/generate.py src/odu_core/*.py
	$(PY) scripts/generate.py

## Rebuild the knowledge base from the versioned content files.
kb: $(DERIVED)
	$(PY) scripts/ingest.py

## Generate the knowledge base site.
site: kb
	$(PY) scripts/build_kb_site.py

## Generate the self-contained mnemonic demo page.
web: $(DERIVED)
	$(PY) scripts/build_web.py

## Export the parity fixture, then build and type-check the TypeScript package.
parity: $(DERIVED)
	$(PY) scripts/export_parity.py

ts: parity
	$(TSC) -p ts

test: build
	$(PY) -m pytest tests/ -q
	cd ts && npm test

## Validate without writing: content files parse, and how much is verified.
check: $(DERIVED)
	$(PY) scripts/ingest.py --check
	$(TSC) -p ts --noEmit
	-$(PY) -c "import sys; sys.path.insert(0,'src'); from odu_core.cli import main; sys.exit(main(['verify']))"

## Report verification coverage of the 16 principal figures.
verify:
	$(PY) scripts/verify_odu.py --status

serve-site: site
	$(PY) -m http.server -d site

serve-web: web
	$(PY) -m http.server -d web

# ts/test/fixtures/parity.json is deliberately kept: it is version-controlled,
# and a diff to it during review is how cross-language drift becomes visible.
clean:
	rm -rf site/ web/index.html kb/odu.db ts/dist
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache
	@echo "removed derived artifacts — 'make' rebuilds them"
