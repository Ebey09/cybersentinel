# CyberSentinel

**Explainable Network Threat Detection and SOC Analysis Platform**

> **Work in progress.** Phase 1 of 15 (ML data contract) is complete. Nothing in this repository trains or serves a model yet. See [Project status](#project-status).

## What this project is

CyberSentinel analyses network flow data, classifies it with machine-learning models, explains each prediction with SHAP, and presents the results the way a SOC analyst works: dashboard, alerts, investigation, report.

The point of the project is to do this **without overclaiming**:

- The system only claims what its training data supports.
- Features seen at inference must be produced the same way as the training features, or the system refuses to predict and says why.
- Evaluation goes beyond accuracy, and includes checks designed to catch leakage and results that look too good.

## Problem statement

Many public "ML intrusion detection" projects report near-perfect accuracy. Common reasons: labelling errors in the dataset, identifiers such as IP addresses or timestamps used as features, random splits that put near-identical flows in train and test, accuracy on imbalanced data, and models trained on one feature extractor but fed features from another. CyberSentinel is built around avoiding those mistakes, and making the remaining limitations visible.

## Two analytical tracks

| | Track A: Attack detection | Track B: Darknet/VPN characterization |
|---|---|---|
| Dataset | Corrected CIC-IDS2017 (Engelen et al.) | CIC-Darknet2020 |
| Output | Benign / attack family, as labelled in the dataset | Tor traffic detected / VPN traffic detected / Non-Tor/Non-VPN traffic; application category |
| Never says | Attack types not in the dataset | That Tor or VPN traffic is malicious |
| PCAP inference | Only after a feature-parity test passes | Not available (extractor version unknown) |

The two tracks have **separate feature schemas** because the datasets were produced with different versions of CICFlowMeter whose features differ in number and definition. Details: [docs/DATASETS.md](docs/DATASETS.md) and [ADR 0005](docs/adr/0005-separate-feature-schema-per-track.md).

## Project status

| Phase | Scope | Status |
|---|---|---|
| 1 | Architecture, repo structure, **ML data contract** | Done |
| 4 | Dataset ingestion and preprocessing | Next |
| 5 | Baseline models and evaluation | Planned |
| 7 | SHAP / XAI | Planned |
| 2, 3, 8 | Backend, database and auth, alert engine | Planned |
| 9, 10, 11 | Dashboard, investigation view, reports | Planned |
| 12 to 15 | Hardening, Docker, CI, documentation | Planned |
| 6 | Deep-learning comparison | Optional |

The ML pipeline is built first because it is the biggest technical risk ([ADR 0009](docs/adr/0009-ml-first-build-order.md)). Full plan: [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md).

## What works today

The data contract, in `ml/`:

- Machine-readable feature schemas for both tracks (`ml/config/schemas/`), documenting every feature's type, unit, meaning, range, missing-value handling, scaling, encoding and PCAP availability
- Experiment configs with explicit label maps and display text (`ml/config/experiments/`)
- Validation code: schema consistency rules, header checks, feature name/order/dtype checks, model and preprocessing manifests, and a **fail-closed inference gate**
- A CLI to check real dataset files against the schemas
- 54 tests on synthetic data

```bash
cd ml
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/pytest
.venv/bin/cybersentinel-ml validate-config
```

Both schemas are **drafts** until they are checked against the real dataset files ([docs/VERIFY.md](docs/VERIFY.md)). The inference gate refuses to run on a draft schema, by design.

## Repository layout

```
ml/          data contract now; preprocessing, training, evaluation, XAI later
docs/        plan, dataset matrix, data contract, pipeline design, ADRs, verification checklist
data/        local datasets (gitignored), synthetic fixtures
models/      local model artifacts (gitignored); model cards
backend/     FastAPI service (Phase 2+)
frontend/    React + TypeScript SOC UI (Phase 9+)
docker/      container definitions (Phase 13, extractor in Phase 4b)
scripts/     helper scripts
tests/e2e/   end-to-end tests (later)
```

## Documentation

- [Project plan and architecture](docs/PROJECT_PLAN.md)
- [Dataset matrix](docs/DATASETS.md)
- [ML data contract](docs/ML_DATA_CONTRACT.md)
- [ML pipeline design](docs/ML_PIPELINE.md)
- [Architecture Decision Records](docs/adr/README.md)
- [Verification checklist](docs/VERIFY.md)

Sections still to be written as the project progresses: screenshots, installation with Docker, configuration, model training and evaluation results, API documentation, testing, limitations, future work.

## Datasets

Datasets are **not** included and are never committed. Download instructions and citations: [data/README.md](data/README.md).

- CIC-IDS2017: Sharafaldin, Habibi Lashkari, Ghorbani, ICISSP 2018. https://www.unb.ca/cic/datasets/ids-2017.html
- Corrections: Engelen, Rimmer, Joosen, IEEE SPW (WTMC) 2021. https://github.com/GintsEngelen/WTMC2021-Code
- CIC-Darknet2020: https://www.unb.ca/cic/datasets/darknet2020.html

## Security

This is a defensive analysis tool. It does not send traffic, scan hosts, or run attacks. See [SECURITY.md](SECURITY.md) for how to report a vulnerability.

## License

MIT. See [LICENSE](LICENSE). Dataset licences and terms are set by their owners and are not covered by this licence.
