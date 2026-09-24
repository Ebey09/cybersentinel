# ADR 0010: A dataset whose extractor version is not documented can be verified, but never used for inference

- Status: Accepted
- Date: 2026-09-24
- Refines: ADR 0006, ADR 0007

## Context

Every schema records the extractor that produced its training data. Until now the code treated "extractor commit" as either pinned or not, and inferred that from whether the `commit` text contained `[VERIFY]`. Two rules depended on it:

1. The schema validator refused a `verified` schema without a pinned commit.
2. The inference gate's `extractor_pinned` check failed every batch, CSV or PCAP, when the commit was not pinned.

For Track B this is a dead end. CIC-Darknet2020 was produced with an upstream CICFlowMeter version that the sources checked so far do not document, and the timeouts are unknown too (ADR 0005). If that stays true after checking the dataset page and paper, no commit can ever be pinned without making one up. Under the old rules Track B could then never become `verified`, even after its header, labels and features were checked against the real file.

The docs also disagreed with the code. `ML_DATA_CONTRACT.md` said a pinned commit was needed "(Track A)" and that "a verified schema allows CSV training and CSV inference". The gate never allowed Track B inference at all.

Two different questions were mixed together:

- **Is the data what the schema says it is?** Header, labels, feature definitions and ranges. This can be checked on the downloaded file.
- **Can new traffic be turned into the same features?** This needs the exact extractor build and settings. Without them it cannot be checked.

## Decision

1. The extractor gets an explicit `commit_status` with three values:
   - `pinned`: the exact commit is known. `commit` must be a real commit, not a placeholder.
   - `to_verify`: nobody has checked yet. This is the Phase 1 state for both tracks.
   - `not_documented`: checked, with the evidence recorded in `docs/VERIFY.md`, and the dataset authors do not document it. This is a finding, not a guess. `commit` stays a plain description and is never filled with an invented value.
2. A schema can be `verified` with `pinned` or `not_documented`, but not with `to_verify`. Verification is about the data file.
3. `not_documented` rules out parity. The validator refuses `parity.status: demonstrated` and any feature marked `pinned_extractor_only` when the commit is not documented.
4. **The inference gate is unchanged.** It still requires a pinned extractor for every batch. So a track with `not_documented` provenance is limited to **offline training and evaluation on the released dataset files**. Its predictions on uploaded CSVs and on PCAPs stay withheld.
5. Track A must not use `not_documented`. Its extractor is knowable: either the correction authors name the commit, or the corrected CSVs are regenerated with a build pinned by us (V8, ADR 0004, ADR 0006). A test enforces this on the committed schema.
6. Track B stays `to_verify` for now. V25 in `docs/VERIFY.md` decides between `pinned` (if the dataset page or paper names the version) and `not_documented` (if not, with what was checked).

## Why uploaded-CSV inference is also withheld for Track B

An uploaded CSV header can match the schema while its values come from a different CICFlowMeter version, with different flow boundaries and bugs (ADR 0005). With a pinned training extractor, the gate compares the uploader's claimed extractor with the training one and at least warns about unverified claims (ADR 0007). With an undocumented training extractor there is nothing to compare against, so a prediction would rest on an assumption that cannot be checked. Allowing it with a warning would contradict ADR 0007, which rejected "predict with a warning banner" because warnings get ignored.

## Consequences

- Track B can be verified, trained, evaluated and explained offline. Its results describe the released dataset only, which ADR 0002 and `DATASETS.md` already say.
- The platform shows no Track B predictions on uploads until a provenance path exists. The architecture in `PROJECT_PLAN.md` still lists a Track B model in the worker; for uploads the gate withholds it and says why, like any other failed check.
- A future way to score Track B on real traffic needs its own ADR. Examples: replaying held-out rows of the released CSV, identified by file SHA-256, or finding the extractor version.
- `is_pinned` now reads `commit_status`, not the commit text. A `pinned` status with a placeholder commit is rejected on load.
- Both schemas bump to `schema_version` 0.2.0 because the format gained a required field.

## Alternatives considered

- **Invent or guess a commit** (for example "upstream master in 2020"). Rejected: it would make the gate's extractor match meaningless and hide the real uncertainty.
- **Drop the pinned-commit rule for Track B only, in code.** Rejected: it would silently turn "not checked yet" into "fine", and hard-code a track exception instead of recording a finding.
- **Allow Track B CSV inference with a warning.** Rejected for the reason above. Can be revisited with evidence in a new ADR.

## Open verification items

- V25: Track B extractor version and timeouts. Check the CIC-Darknet2020 page and the DIDarknet paper. Record what was checked and the result.

## References

- CIC-Darknet2020 page: https://www.unb.ca/cic/datasets/darknet2020.html
- Upstream CICFlowMeter: https://github.com/ahlashkari/CICFlowMeter
