# cybersentinel-ml

The ML side of CyberSentinel: data contract, preprocessing, training, evaluation and XAI.
Training runs offline from scripts. The web application (later phases) only loads
versioned, hash-checked artifacts produced here.

## What exists now (Phase 1)

Only the **data contract**. Nothing here trains or predicts yet.

| Path | What it is |
|---|---|
| `config/schemas/track_a_cicids2017.yaml` | Feature schema for Track A (attack detection, corrected CIC-IDS2017) |
| `config/schemas/track_b_darknet2020.yaml` | Feature schema for Track B (Tor/VPN characterization, CIC-Darknet2020) |
| `config/experiments/*.yaml` | Task definitions: label maps, display text, split, seed, models |
| `config/datasets.yaml` | Dataset sources, citations, terms, expected files (checksums filled after download) |
| `src/cybersentinel_ml/contract/` | Schema loader, manifests, header/feature checks, inference gate |
| `src/cybersentinel_ml/cli.py` | `cybersentinel-ml` command |
| `tests/` | Contract tests (synthetic data only) |

Both schemas are `status: draft`. The inference gate refuses to run on a draft schema.
They become `verified` only after the checks in [docs/VERIFY.md](../docs/VERIFY.md) pass on the real files.

## Setup

```bash
cd ml
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev]"
```

## Commands that work now

```bash
# Validate every schema and experiment config, and cross-check them
.venv/bin/cybersentinel-ml validate-config

# After downloading a dataset: does the real header match the schema?
.venv/bin/cybersentinel-ml check-header \
  --schema config/schemas/track_b_darknet2020.yaml \
  --csv ../data/raw/cic_darknet2020/Darknet.CSV

# Which label strings does the CSV really contain? Are any missing from the label map?
.venv/bin/cybersentinel-ml inspect-labels \
  --csv ../data/raw/cic_darknet2020/Darknet.CSV --column Label \
  --experiment config/experiments/track_b_traffic_type.yaml

# Regenerate the human-readable schema reference
.venv/bin/cybersentinel-ml schema-docs \
  --schema config/schemas/track_a_cicids2017.yaml --out ../docs/schemas/track_a_cicids2017.md

# Tests and lint
.venv/bin/pytest
.venv/bin/ruff check src tests
```

The file name `Darknet.CSV` above is an example. Use whatever name the download has.

## Commands planned for later phases (not implemented yet)

```bash
cybersentinel-ml prepare  --experiment config/experiments/track_a_binary.yaml   # Phase 4
cybersentinel-ml train    --experiment config/experiments/track_a_binary.yaml   # Phase 5
cybersentinel-ml evaluate --run runs/<run_id>                                   # Phase 5
cybersentinel-ml explain  --run runs/<run_id>                                   # Phase 7
```
