# ADR 0012: Use the published CNS2022 Improved CIC-IDS2017 release, with its extractor commit recorded as unknown

- Status: Accepted
- Date: 2026-09-24
- Refines: ADR 0004 (which corrected release), ADR 0010 (provenance vocabulary)

## Context

ADR 0004 chose the corrected CIC-IDS2017 but left the release open (V1). The CNS2022 authors (Liu, Engelen et al.) publish a labelled CSV release, `CICIDS2017_improved.zip`, from https://intrusion-detection.distrinet-research.be/CNS2022/Datasets/. It contains `monday.csv` to `friday.csv`. Local inspection found 91 columns in every file, with the same header and order in all five.

The Phase 1 Track A schema was written from the fork's current `master` (94 columns). The published release differs:

- It has `id`, `Total TCP Flow Time` and `Attempted Category`.
- It does not have `Bwd Act Data Pkts`, `Bwd Seg Size Min`, `Fwd/Bwd/Total TCP Retrans. Count` or `Total Connection Flow Time`.

What the author materials establish:

- The extractor is the authors' modified CICFlowMeter, https://github.com/GintsEngelen/CICFlowMeter. The CNS2022 documentation lists its fixes: TCP flows end after a mutual FIN exchange, RST ends a TCP flow, Fwd/Bwd bulk feature fixes, UTC timestamps with microsecond precision, ICMP support, Total TCP duration, Fwd/Bwd RST features, and a TCP segmentation offload fix.
- Documented extraction settings: offline mode, flow timeout 120000000, activity timeout 5000000, pcapfix then reordercap (CNS2022_Code README).
- The labelling notebook is `Labelling/CICIDS2017_labelling_fixed_CICFlowMeter.ipynb` in https://github.com/GintsEngelen/CNS2022_Code. Its code adds `id` (a row number, `print_index`) and `Attempted Category` (default -1). It also drops rows containing Infinity or NaN before writing the CSVs.

What they do not establish:

- The exact CICFlowMeter Git commit used to generate the published ZIP. The documentation, README, notebook, commit messages, branches and tags inspected do not name one.
- The notebook revision used for the release. The repository has `5d86184` (2022-10-12), `8b23a1c` (2023-03-30, post-publication fixes) and `7f862bf6f9dcd5b327dfeaff0d68ff29256fb871` (2023-04-27). Nothing ties one of them to the ZIP.

The header of the fork's `FlowFeature.java` is consistent with a range of commits, but a header match, a date or the closest-looking commit is not provenance. The same range contains changes to feature values.

## Decision

1. Track A uses the published CNS2022 release as downloaded. The raw schema describes its actual 91-column layout. No column is renamed.
2. Columns added by the labelling notebook are never model inputs:
   - `id` is an identifier (`row_id`).
   - `Attempted Category` is label-side metadata, declared as a label column, and is never a feature or a training target.
   - "Attempted" flows map to BENIGN as in ADR 0004. There is no separate Attempted class.
3. `Total TCP Flow Time` is kept as an excluded feature until V16 confirms its definition and unit. The six later fork columns are not part of this release and are removed from the Track A raw schema.
4. The extractor commit stays `commit_status: to_verify`, with the reason recorded: author tool identified, exact generation commit not published or documented. It is not `not_documented`, because the tool itself is known and ADR 0010 reserves that status for a track whose extractor cannot be pinned at all. It is not `pinned`, and no commit is inferred.
5. The original archive and its SHA-256 are kept as the reference copy of the data (V7).
6. Regenerating the CSVs from the UNB PCAPs with a pinned fork commit was considered and not chosen now. It remains the path if exact provenance becomes necessary.

## Consequences

- Track A matches the files we actually have, so `check-header` can test the real data (V3).
- **Track A cannot become `verified` yet.** The validator requires a `pinned` (or, for other tracks, `not_documented`) extractor. Until the authors name the commit, or we regenerate with a pinned build, the schema stays `draft`, and the contract blocks training and inference on it.
- PCAP parity for Track A (ADR 0006) also needs a pinned commit. PCAP inference stays blocked.
- The release has no Infinity or NaN rows, because the labelling notebook dropped them. Rows with a zero-duration flow and undefined rates were removed upstream. That is a property of the data, recorded here, not something our pipeline changes.
- `schema_version` goes to 0.3.0. The preprocessing version is unchanged.

## Alternatives considered

- **Regenerate now with a pinned fork commit.** Rejected for now: it needs the raw PCAPs, pcapfix and reordercap, a fork build, and a labelling notebook written for an older header. It stays open.
- **Record a commit from the header-compatible range.** Rejected: that is inference, not provenance.
- **Mark the extractor `not_documented`.** Rejected: the tool is identified. Only the exact commit is missing, and ADR 0010 keeps Track A pinnable.

## Open verification items

- V8: exact CICFlowMeter commit used for the release.
- V26: exact labelling notebook revision used for the release.
- V3: run `check-header` on all five files against schema 0.3.0 (the column order in the schema must be confirmed on the files).
- V5, V7: label strings and counts, SHA-256 of the archive and files.

## References

- CNS2022 documentation: https://intrusion-detection.distrinet-research.be/CNS2022/
- CNS2022 code: https://github.com/GintsEngelen/CNS2022_Code
- Modified CICFlowMeter: https://github.com/GintsEngelen/CICFlowMeter
- Liu, Engelen, Lynar, Essam, Joosen. Error Prevalence in NIDS datasets: A Case Study on CIC-IDS-2017 and CSE-CIC-IDS-2018. IEEE CNS 2022.
