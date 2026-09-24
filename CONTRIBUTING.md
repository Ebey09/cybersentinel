# Contributing

This is a personal portfolio project, but it is run like a team project so the process is visible.

## Workflow

1. Open or pick an issue. Every change links to one.
2. Branch from `main`: `phase-NN-short-topic` (for example `phase-04-data-ingestion`) or `fix/short-topic`.
3. Keep commits small. Use [Conventional Commits](https://www.conventionalcommits.org/):
   `feat(ml): ...`, `fix(contract): ...`, `docs(adr): ...`, `test: ...`, `chore: ...`, `ci: ...`
4. Open a pull request using the template. Once CI is added, it must pass before merge. Until then, run the checks below locally.
5. Merge phase PRs with a merge commit (not squash), so the small, logical commits stay visible in history.

## Local setup (Phase 1)

```bash
pip install pre-commit        # or: uv tool install pre-commit
pre-commit install
cd ml
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev]"
```

## Before opening a PR

```bash
make lint      # ruff check + format check
make test      # pytest
make validate  # cybersentinel-ml validate-config
pre-commit run --all-files
```

## Rules specific to this project

- **Never commit dataset rows, PCAPs or model binaries.** Test data must be synthetic.
- **Schemas are the contract.** Any change to a file in `ml/config/schemas/` must bump `schema_version`, regenerate `docs/schemas/*.md` (`cybersentinel-ml schema-docs`), and explain the reason in the PR. A change to preprocessing rules bumps `preprocessing.version`.
- **No invented numbers.** Dataset statistics and model metrics in docs must come from a committed results file or command output, with the input file's SHA-256.
- **Track B vocabulary.** Track B output must never describe Tor/VPN traffic as malicious, an attack, a threat or malware. Tests enforce this.
- **Record decisions.** Significant design decisions get an ADR in `docs/adr/`.
- **Mark uncertainty.** Anything not yet confirmed is tagged `[VERIFY]` and listed in `docs/VERIFY.md`.
- Style: ruff (lint + format), line length 110, type hints on public functions.
