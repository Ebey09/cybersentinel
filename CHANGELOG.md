# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- ADR 0010: a dataset whose extractor version is not documented can be verified, but never used for inference. Extractor `commit_status` (`pinned`, `to_verify`, `not_documented`) replaces guessing from the commit text
- ADR 0011: ambiguous raw column names (for example a repeated `Label`) are resolved by declared `positional_renames`, never silently. `resolve_raw_header` applies them after an exact header match
- VERIFY V25: Track B extractor version

### Changed
- Both schemas to v0.2.0. Track B's second label column is no longer assumed to be called `Label.1`
- `check-header` accepts a repeated column only when the schema declares it, and prints the declared renames
- Track B application-category label keys marked as placeholders until V6 (`File Transfer` vs `File-Transfer` unresolved)
- `.gitignore` also ignores `*.zip` and `*.PCAP`

## [0.1.0] - Phase 1: ML data contract

### Added
- Repository skeleton, README, SECURITY, CONTRIBUTING, LICENSE (MIT), pre-commit hooks, Makefile, GitHub issue/PR templates, Dependabot config
- Project plan v0.2 with a critical review of v0.1 assumptions
- ADRs 0001-0009: two analytical tracks, Darknet2020 not attack data, CIC-IDS2017 for attacks, corrected release, separate schemas per track, PCAP parity, fail-closed inference, optional deep learning, ML-first order
- Dataset matrix, ML data contract, ML pipeline design, verification checklist
- Feature schemas (draft) for Track A (corrected CIC-IDS2017) and Track B (CIC-Darknet2020)
- Experiment configs: Track A binary and family multi-class; Track B 3-class traffic type, application category, 4-class diagnostic
- `cybersentinel_ml.contract`: schema loader with consistency rules, manifests, header and feature-frame checks, inference gate
- `cybersentinel-ml` CLI: `validate-config`, `check-header`, `inspect-labels`, `schema-docs`
- Contract test suite (synthetic data only)
