# ADR 0006: PCAP-to-feature parity must be demonstrated before PCAP inference

- Status: Accepted
- Date: 2026-09-24

## Context

A model learns the joint distribution of the features it was trained on. If uploaded PCAPs are turned into features by a different process, even one with the same column names, the model receives inputs from a different distribution and its predictions are not meaningful. This failure is silent: the model still outputs confident probabilities.

Common ways this happens in student projects:

- Training on CICFlowMeter CSVs, then computing "similar" features with Scapy or PyShark.
- Using a Python re-implementation of CICFlowMeter whose flow termination, timeouts or feature formulas differ.
- Using the right tool with different flow/activity timeouts.
- Using a different version of the right tool (ADR 0005 shows how much versions differ).

## Decision

PCAP inference for a track is only enabled when all of the following hold:

1. **Same extractor, pinned.** The platform runs the exact extractor build that produced the training data: same repository, same commit, same flow timeout and activity timeout, and the same PCAP preprocessing steps (for example pcapfix and reordercap if the CNS 2022 release is used). Recorded in `schema.extractor` and in a provenance record attached to every extracted batch.
2. **Same schema.** Extracted CSV header must match `schema.raw_columns` exactly (names and order).
3. **Same preprocessing.** The fitted preprocessing artifact (imputation medians, dropped constant columns, scaling) stored with the model is applied unchanged, and its version must match `schema.preprocessing.version`.
4. **Same feature order.** The frame passed to the model must equal `feature_order` in the model's manifest.
5. **Parity demonstrated.** `schema.parity.status` must be `demonstrated`, backed by evidence.

### Parity test (how "demonstrated" is earned)

1. Take raw PCAP for one day of CIC-IDS2017 (from UNB CIC).
2. Run the platform's extractor container on it.
3. Compare the output with the corrected CSV rows for that day. Match flows by 5-tuple and start time.
4. Report: % of dataset flows matched, % of extracted flows matched, and per-feature agreement (exact for counts, relative tolerance for floats).
5. Pass criteria are fixed **before** running the test and written into the evidence file. Suggested starting point: at least 99% of flows matched both ways and at least 99% of matched flows agree on every included feature. [Thresholds to confirm when the test is built.]
6. The evidence (report JSON, extractor image digest, PCAP SHA-256) is committed under `ml/results/parity/`, and `schema.parity.evidence` points to it.

If the corrected CSVs are regenerated from PCAP with the pinned image in the first place, step 3 compares the platform's container with itself and trivially passes. It still has to be run to prove the container build is the one that made the training data.

## Consequences

- PCAP inference for Track A is blocked until the parity test exists and passes. Until then PCAP uploads get traffic statistics and rule-based alerts only (ADR 0007).
- Track B PCAP inference is blocked indefinitely, because the extractor version and settings used for CIC-Darknet2020 are unknown. Track B is CSV-only.
- The validation code in `cybersentinel_ml.contract` checks names, order, dtypes, missing and unexpected features, preprocessing version, extractor identity and parity status. See `docs/ML_DATA_CONTRACT.md`.

## Alternatives considered

- **Python `cicflowmeter` package.** Easier to install, but a different implementation. Allowed only if it passes the same parity test, which is not expected.
- **Train on features our own extractor makes from the dataset PCAPs.** This is the cleanest option and is option 2 in `ml/config/datasets.yaml`. Cost: large downloads and extraction time.

## References

- Fixed extractor and its Docker instructions: https://github.com/GintsEngelen/CICFlowMeter
- Extractor defaults (flow timeout 120000000, activity timeout 5000000): READMEs of https://github.com/GintsEngelen/WTMC2021-Code and https://github.com/GintsEngelen/CNS2022_Code
