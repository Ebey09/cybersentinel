# Data

Nothing in this folder is committed except this README, `.gitkeep` files and synthetic test fixtures.
**Never commit dataset rows or PCAPs.** `.gitignore` blocks CSV, Parquet and PCAP files outside `data/fixtures/`.

| Folder | Contents |
|---|---|
| `raw/` | Files exactly as downloaded (never modified) |
| `interim/` | Intermediate outputs (for example, extractor output before labelling) |
| `processed/` | Cleaned, split Parquet files written by `cybersentinel-ml prepare` (Phase 4) |
| `fixtures/` | Small **synthetic** files for tests. No real dataset rows |

## Getting the datasets

Registry with sources, terms and citations: `ml/config/datasets.yaml`.

### Track A: corrected CIC-IDS2017

Used: the published **CNS2022 Improved CIC-IDS2017** release, `CICIDS2017_improved.zip` from https://intrusion-detection.distrinet-research.be/CNS2022/Datasets/ (five files, `monday.csv` to `friday.csv`, 91 columns). Keep the archive as downloaded and record its SHA-256. The exact extractor commit is not documented (ADR 0012, V8).

Alternative, not used now: **regenerate from raw PCAPs**. Download the CIC-IDS2017 PCAPs from https://www.unb.ca/cic/datasets/ids-2017.html, run the pinned Engelen CICFlowMeter image (https://github.com/GintsEngelen/CICFlowMeter, flow timeout 120000000, activity timeout 5000000), then label with https://github.com/GintsEngelen/WTMC2021-Code. Watch the `TIME_DIFFERENCE` timezone setting in the labelling script.

Suggested location: `data/raw/cic_ids2017_corrected/`.

### Track B: CIC-Darknet2020

Download from https://www.unb.ca/cic/datasets/darknet2020.html (registration form). [VERIFY] current process and file name.

Suggested location: `data/raw/cic_darknet2020/`.

## After downloading

```bash
sha256sum data/raw/cic_darknet2020/*          # record in ml/config/datasets.yaml
cd ml
.venv/bin/cybersentinel-ml check-header --schema config/schemas/track_b_darknet2020.yaml --csv ../data/raw/cic_darknet2020/<file>
.venv/bin/cybersentinel-ml inspect-labels --csv ../data/raw/cic_darknet2020/<file> --column Label \
    --experiment config/experiments/track_b_traffic_type.yaml
```

Then work through `docs/VERIFY.md`.

## Terms and citation

Follow each dataset owner's terms and cite both the original dataset and the correction. Check whether publishing aggregate statistics and trained models is allowed before doing so (V2).
