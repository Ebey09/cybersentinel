# Architecture Decision Records

Short records of decisions that shape the project, why they were made, and what they cost.
Format: Context, Decision, Consequences, Alternatives, Open verification items, References.
A superseded ADR is kept and marked, never deleted.

| # | Decision | Status |
|---|---|---|
| [0001](0001-two-separate-analytical-tracks.md) | Two separate analytical tracks, no combined "malicious vs benign" model | Accepted |
| [0002](0002-darknet2020-is-not-attack-data.md) | CIC-Darknet2020 is not treated as attack or malware data | Accepted |
| [0003](0003-cicids2017-for-attack-detection.md) | CIC-IDS2017 is the attack-detection dataset | Accepted |
| [0004](0004-prefer-corrected-cicids2017.md) | Use the corrected CIC-IDS2017 (Engelen et al.), map "Attempted" to BENIGN | Accepted |
| [0005](0005-separate-feature-schema-per-track.md) | One feature schema per track, not one shared canonical schema | Accepted |
| [0006](0006-pcap-feature-parity-is-mandatory.md) | PCAP-to-feature parity must be demonstrated before PCAP inference | Accepted |
| [0007](0007-withhold-predictions-without-parity.md) | Withhold ML predictions (fail closed) when the contract cannot be demonstrated | Accepted |
| [0008](0008-deep-learning-is-optional.md) | Deep learning is an optional comparison, not a default component | Accepted |
| [0009](0009-ml-first-build-order.md) | Build and validate the ML pipeline before the web application | Accepted |
| [0010](0010-undocumented-extractor-provenance.md) | A dataset whose extractor version is not documented can be verified, but never used for inference | Accepted |
| [0011](0011-explicit-positional-renames-for-ambiguous-headers.md) | Ambiguous raw column names are resolved by declared positional renames, never silently | Accepted |
