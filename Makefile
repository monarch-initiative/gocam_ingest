ROOTDIR = $(shell pwd)
RUN = poetry run
VERSION = $(shell poetry -C src/gocam_ingest version -s)

### Help ###

define HELP
╭───────────────────────────────────────────────────────────╮
  Makefile for gocam_ingest			    
│ ───────────────────────────────────────────────────────── │
│ Usage:                                                    │
│     make <target>                                         │
│                                                           │
│ Targets:                                                  │
│     help                Print this help message           │
│                                                           │
│     all                 Download, prepare, and transform  │
│     fresh               Clean and install everything      │
│     clean               Clean up build artifacts          │
│     clobber             Clean up generated files          │
│                                                           │
│     install             Poetry install package            │
│     download            Download GOCAM models             │
│     prepare             Convert YAML to JSON              │
│     transform           Run Koza transform                │
│     run                 Full pipeline (download+prepare+transform) │
│                                                           │
│     docs                Generate documentation            │
│                                                           │
│     test                Run all tests                     │
│                                                           │
│     lint                Lint all code                     │
│     format              Format all code                   │
╰───────────────────────────────────────────────────────────╯
endef
export HELP

.PHONY: help
help:
	@printf "$${HELP}"


### Installation and Setup ###

.PHONY: fresh
fresh: clean clobber all

.PHONY: all
all: download prepare transform

.PHONY: install
install: 
	poetry install --with dev


### Documentation ###

.PHONY: docs
docs:
	$(RUN) mkdocs build


### Testing ###

.PHONY: test
test:
	$(RUN) pytest tests


### Running ###

.PHONY: download
download:
	$(RUN) ingest download

.PHONY: prepare
prepare:
	$(RUN) ingest prepare

.PHONY: transform  
transform:
	$(RUN) ingest transform

.PHONY: run
run: download prepare transform


### Linting, Formatting, and Cleaning ###

.PHONY: clean
clean:
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf `find . -name __pycache__` \
		.venv .ruff_cache .pytest_cache **/.ipynb_checkpoints

.PHONY: clobber
clobber:
	# Add any files to remove here
	@echo "Nothing to remove. Add files to remove to clobber target."

.PHONY: lint
lint: 
	$(RUN) ruff check --diff --exit-zero
	$(RUN) black -l 120 --check --diff src tests

.PHONY: format
format: 
	$(RUN) ruff check --fix --exit-zero
	$(RUN) black -l 120 src tests
