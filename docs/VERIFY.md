# Verification Checklist

Every open **[VERIFY]** item in the repo, what exactly to check, and how.
Close an item by recording the evidence (command output, file SHA-256, link) in the "Result" column and in the commit message.

## Before Phase 4 (needs the downloaded data)

| # | Item | How to check | Blocks | Result |
|---|---|---|---|---|
| V1 | Which corrected CIC-IDS2017 release to use (WTMC 2021 or CNS 2022), and whether pre-built CSVs can be downloaded | Visit the authors' project pages linked from https://github.com/GintsEngelen/WTMC2021-Code and https://github.com/GintsEngelen/CNS2022_Code. Their site was unreachable from the environment used to write this. If no CSVs are available, use option 2 in `ml/config/datasets.yaml` (regenerate from PCAP) | Track A schema | |
| V2 | Terms of use for CIC-IDS2017, the correction, and CIC-Darknet2020 | Read the terms on each dataset page. Confirm that publishing aggregate statistics and trained models is allowed | Publishing results | |
| V3 | Track A real CSV header = schema `raw_columns` (currently the fork's 94-column header) | `cybersentinel-ml check-header --schema config/schemas/track_a_cicids2017.yaml --csv <file>` on every CSV of the release | Track A schema | |
| V4 | Track B real CSV header = schema `raw_columns` (currently upstream 84 columns + `Label.1`). In particular: is the second label column literally named `Label` twice? | `cybersentinel-ml check-header --schema config/schemas/track_b_darknet2020.yaml --csv <file>` | Track B schema | |
| V5 | Track A label strings match `track_a_*.yaml` | `cybersentinel-ml inspect-labels --csv <file> --column Label --experiment config/experiments/track_a_binary.yaml` per file | Track A training | |
| V6 | Track B label strings and casing (both label columns) | `inspect-labels` with `--column Label` and with `--column-index <n>` for the second label column, against `track_b_traffic_type.yaml` and `track_b_application_category.yaml` | Track B training | |
| V7 | Class counts for both datasets (papers disagree) | Output of V5/V6, recorded in `docs/DATASETS.md` with file SHA-256 | README numbers | |
| V8 | Engelen fork commit that produced the chosen release | Release notes or authors' page; otherwise pin the commit you build and regenerate (option 2) | Track A `extractor.commit`, parity | |

## During Phase 4 (EDA diagnostics, coded in the data report)

| # | Item | How to check | Blocks | Result |
|---|---|---|---|---|
| V9 | Darknet2020 Active/Idle features contain timestamp-like values (upstream bug) | Distribution of `Active *` / `Idle *`. Values around 1.4e15 to 1.6e15 microseconds look like epoch times from 2014 to 2020. If present, they stay excluded | Track B features | |
| V10 | Darknet2020 PSH/URG directional flag columns are unreliable | Count distinct values and share of zeros per class | Track B features | |
| V11 | Sentinel value for `FWD/Bwd Init Win Bytes` when not observed (expected -1) | Value counts below 0 | Both schemas' ranges | |
| V12 | `* Flag Count` columns: counts or 0/1 indicators | Max value per column | Feature `meaning` text | |
| V13 | `Down/Up Ratio`: integer or float division | Check for non-integer values | Feature `meaning` text | |
| V14 | Observed `Protocol` values (6, 17, others such as 0) | Value counts | `protocol.categories` | |
| V15 | `ICMP Code` / `ICMP Type` value for non-ICMP flows (Track A) | Value counts on TCP/UDP rows; read `BasicFlow.java` in the fork | Whether to include them | |
| V16 | Definition and unit of `Total Connection Flow Time` (Track A) | Read the fork source where it is computed | Whether to include it | |
| V17 | Exact definition of `Fwd/Bwd Seg Size Min` | Read `BasicFlow.java` in both repos | Feature `meaning` text | |
| V18 | Rare Track A classes below `min_class_count` (100) in training | Data report | Multi-class task scope | |

## Before publishing the README

| # | Item | How to check | Result |
|---|---|---|---|
| V19 | Grinsztajn et al. NeurIPS 2022 title and link | Look up the paper | |
| V20 | Citation text requested by each dataset page | Dataset pages | |
| V21 | Python 3.12 wheels available for all Phase 4/5 dependencies (pandas, scikit-learn, xgboost, shap, pyarrow) | `uv pip install` on a clean venv | |

## Parity (Phase 4b, after Milestone A)

| # | Item | How to check | Result |
|---|---|---|---|
| V22 | The fork's Docker image builds and runs | `docker build -t cicflowmeter .` in the fork, then run it on a small PCAP | |
| V23 | Parity test passes for one CIC-IDS2017 day | ADR 0006 procedure, evidence in `ml/results/parity/` | |
| V24 | If regenerating labels: correct `TIME_DIFFERENCE` for the extraction host's timezone | Spot-check known attack windows against the dataset page schedule | |
