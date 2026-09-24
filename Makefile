ML = ml
PY = $(ML)/.venv/bin

.PHONY: help setup test lint format validate schema-docs clean

help:  ## list targets
	@grep -E "^[a-z-]+:.*##" $(MAKEFILE_LIST) | sed "s/:.*##/  -/"

setup:  ## create the ml virtualenv and install dev dependencies
	cd $(ML) && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e ".[dev]"

test:  ## run ml tests
	cd $(ML) && .venv/bin/pytest

lint:  ## ruff lint + format check
	cd $(ML) && .venv/bin/ruff check src tests && .venv/bin/ruff format --check src tests

format:  ## apply ruff formatting
	cd $(ML) && .venv/bin/ruff format src tests && .venv/bin/ruff check --fix src tests

validate:  ## validate schemas and experiment configs
	$(PY)/cybersentinel-ml validate-config --root .

schema-docs:  ## regenerate docs/schemas from the schema YAMLs
	$(PY)/cybersentinel-ml schema-docs --schema $(ML)/config/schemas/track_a_cicids2017.yaml --out docs/schemas/track_a_cicids2017.md
	$(PY)/cybersentinel-ml schema-docs --schema $(ML)/config/schemas/track_b_darknet2020.yaml --out docs/schemas/track_b_darknet2020.md

clean:  ## remove caches
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
