# Dataset Matrix

What each dataset is for, what a model trained on it may say, and what it must never say.
Machine-readable details live in `ml/config/datasets.yaml` and the schemas in `ml/config/schemas/`.

Items marked **[VERIFY]** are not confirmed yet. See [VERIFY.md](VERIFY.md) for how to check each one.

## Summary matrix

| | **Track A: Attack detection** | **Track B: Darknet/VPN characterization** |
|---|---|---|
| **Dataset** | CNS2022 Improved CIC-IDS2017 (Liu, Engelen et al.): published `CICIDS2017_improved.zip`, five files `monday.csv` to `friday.csv`, 91 raw columns (ADR 0012) | CIC-Darknet2020 |
| **Purpose** | Detect and classify flows that resemble the attack classes in the corrected dataset | Characterize flows as Tor, VPN or regular traffic, and by application category |
| **Raw labels** | 27 values observed in the five CNS2022 CSVs (V5): `BENIGN`, `FTP-Patator`, `SSH-Patator`, `DoS Hulk`, `DoS GoldenEye`, `DoS Slowloris`, `DoS Slowhttptest`, `Heartbleed`, `Web Attack - Brute Force`, `Web Attack - XSS`, `Web Attack - SQL Injection`, `Infiltration`, `Infiltration - Portscan`, `Portscan`, `DDoS`, `Botnet`, plus 11 `<attack> - Attempted` labels (FTP-Patator, SSH-Patator, the four DoS, the three Web Attack, Infiltration, Botnet). Attempted labels map to BENIGN; there is no Attempted class. `Infiltration - Portscan` maps to our PORTSCAN family: the CNS2022 documentation places it under the Infiltration scenario's "NMAP Portscan" section and describes it as a portscanning attack, and the grouping is our taxonomy decision. The release also has an `Attempted Category` column: label-side metadata, never a feature or a class | First label column (`Label`): Tor, Non-Tor, VPN, Non-VPN. Second label column (raw name [VERIFY], draft assumes a repeated `Label`, ADR 0011): eight application categories, audio streaming, browsing, chat, email, file transfer, P2P, video streaming, VoIP. Strings from the literature; exact raw spelling and casing [VERIFY] (for example `File Transfer` vs `File-Transfer`) |
| **Model tasks** | Binary (BENIGN vs ATTACK); multi-class by attack family | 3-class traffic type (TOR, VPN, REGULAR); 8-class application category; 4-class diagnostic (never deployed) |
| **Features** | 80 CICFlowMeter flow features from the Engelen fork (91-column release header minus 6 identifiers incl. `id`, 2 label-side columns, 3 excluded). Header verified with `check-header` on all five files (V3) | 66 CICFlowMeter flow features from upstream (84-column header plus a second label column, minus 5 identifiers, 2 labels, 12 excluded) [VERIFY against real header] |
| **Excluded from model** | `id` (row number added by the labelling notebook), Flow ID, IPs, source port, timestamp (identifiers or label proxies); `Label` and `Attempted Category` (label side); ICMP Code/Type and Total TCP Flow Time (definitions unconfirmed, V15, V16) | Same identifiers; Active/Idle x8 (possible timestamp leakage from an upstream bug); Fwd/Bwd PSH and URG flags x4 (upstream bug) |
| **Extraction method** | Authors' modified CICFlowMeter (https://github.com/GintsEngelen/CICFlowMeter), offline mode, flow timeout 120 s, activity timeout 5 s, pcapfix then reordercap. **Exact generation commit: unknown / not documented** (V8, `commit_status: to_verify`). Labelled with `CNS2022_Code/Labelling/CICIDS2017_labelling_fixed_CICFlowMeter.ipynb`; known revision `7f862bf6f9dcd5b327dfeaff0d68ff29256fb871` is not confirmed as the release revision (V26). The notebook dropped Infinity/NaN rows before release | CICFlowMeter, upstream, version used by CIC in 2020 unknown [VERIFY V25], timeouts unknown. If it stays undocumented it is recorded as `not_documented`, never guessed (ADR 0010) |
| **PCAP inference** | Allowed only after the parity test passes (ADR 0006), which needs a pinned commit. Blocked for now | Blocked. Extractor version unknown, so parity cannot be shown. Uploaded-CSV inference is withheld too while the extractor is not pinned; the model is trained and evaluated offline on the released CSV only (ADR 0010) |
| **Intended model** | Best of LR / RF / XGBoost on validation; calibrated probabilities; threshold set for a target false-positive rate | Best of LR / RF / XGBoost on validation; calibrated probabilities |
| **Allowed claims** | "This flow resembles `<attack family>` traffic as represented in CIC-IDS2017, with calibrated confidence p." "Top features that pushed the model toward this class were ..." | "Tor traffic detected." "VPN traffic detected." "Non-Tor / Non-VPN traffic." "Application category: Chat." "Policy/risk signal." |
| **Must NOT claim** | Detection of attack types not in the dataset ("zero-day", "APT", "ransomware"); that a flow **is** an attack (only that it resembles one); that lab performance transfers to real networks; that SHAP shows attacker intent or causality | That Tor/VPN traffic is malicious, an attack, a threat, malware or an intrusion; anything about user intent; that Non-Tor vs Non-VPN is a real traffic distinction; performance on PCAPs |
| **Main known limitations** | 2017 lab traffic; tiny rare classes; label assigned by IP and time window; Attempted label is a function of one feature (ADR 0004) | Strong class imbalance (Tor is a small class); Non-Tor and Non-VPN come from different capture sessions; unknown extractor version and possible upstream bugs |

## Track A provenance limitation

The CNS2022 authors identify their modified GintsEngelen/CICFlowMeter implementation and document the fixes applied to it. However, the exact CICFlowMeter Git commit used to generate the published `CICIDS2017_improved.zip` release is not specified in the author materials inspected. The project therefore records the exact extractor commit as undocumented/unknown rather than inferring one. Until that changes, or the CSVs are regenerated with a pinned build, the Track A schema stays `draft` (ADR 0012).

## Why the two tracks are never combined

See [ADR 0001](adr/0001-two-separate-analytical-tracks.md). In short: no shared definition of "malicious", two different extractor versions with different flow definitions ([ADR 0005](adr/0005-separate-feature-schema-per-track.md)), and a real risk of the model learning "which dataset is this row from".

## Class distribution

**Track A file hashes, row counts and raw label counts are recorded below. Track B counts are not recorded yet.** Counts are computed from the downloaded files by `cybersentinel-ml inspect-labels` (now) and by the Phase 4 data report (later), and then copied here with the file SHA-256 they came from. Numbers quoted from papers do not agree with each other (one Darknet2020 paper gives two different totals), so none are hardcoded.

| Dataset file | SHA-256 | Class counts | Source of counts |
|---|---|---|---|
| Track A `monday.csv` (371,624 rows, 91 columns) | `51fe5dc962626efb4ae70dce0303072fb780da0932822b651202ee9c2fbc1aff` | see Track A raw label counts below | `inspect-labels` output |
| Track A `tuesday.csv` (322,078 rows, 91 columns) | `e2a0a5b631dfc6b455cc9f9a88b944110637d70a7f74171473925f76f38b6b0c` | see Track A raw label counts below | `inspect-labels` output |
| Track A `wednesday.csv` (496,641 rows, 91 columns) | `bf46c5f3c792e8817381f724511229569606918eaf07ac986d7a2592b6341bc2` | see Track A raw label counts below | `inspect-labels` output |
| Track A `thursday.csv` (362,076 rows, 91 columns) | `78a4d11eaf473d099e30e71ddb01e0f38218e844c0a9cdd36602145d674af482` | see Track A raw label counts below | `inspect-labels` output |
| Track A `friday.csv` (547,557 rows, 91 columns) | `ebd499e6f23bd59f9cb81bec28178491b02b925fa5640a24215c9437d79482d0` | see Track A raw label counts below | `inspect-labels` output |
| Track A `CICIDS2017_improved.zip` (archive) | `97fdb91d339e2d8cf5627f981b831e5e7e400b981c58181c451a38fd03c48883` (previously hashed by the project owner; not re-hashed in the V3/V5/V7 verification) | n/a | n/a |
| Track B (after download) | | | `inspect-labels` output |

### Track A raw label counts (CNS2022 release)

Raw `Label` values exactly as spelled in the files, counted by `cybersentinel-ml inspect-labels` on each CSV. These are dataset label counts, not model classes: every `- Attempted` label maps to BENIGN in both Track A experiments, and `Attempted Category` is not used. Empty cell = 0.

| Raw label | `monday.csv` | `tuesday.csv` | `wednesday.csv` | `thursday.csv` | `friday.csv` | Total |
|---|---:|---:|---:|---:|---:|---:|
| `BENIGN` | 371,624 | 315,106 | 319,120 | 288,172 | 288,544 | 1,582,566 |
| `FTP-Patator` |  | 3,972 |  |  |  | 3,972 |
| `FTP-Patator - Attempted` |  | 12 |  |  |  | 12 |
| `SSH-Patator` |  | 2,961 |  |  |  | 2,961 |
| `SSH-Patator - Attempted` |  | 27 |  |  |  | 27 |
| `DoS Hulk` |  |  | 158,468 |  |  | 158,468 |
| `DoS Hulk - Attempted` |  |  | 581 |  |  | 581 |
| `DoS GoldenEye` |  |  | 7,567 |  |  | 7,567 |
| `DoS GoldenEye - Attempted` |  |  | 80 |  |  | 80 |
| `DoS Slowloris` |  |  | 3,859 |  |  | 3,859 |
| `DoS Slowloris - Attempted` |  |  | 1,847 |  |  | 1,847 |
| `DoS Slowhttptest` |  |  | 1,740 |  |  | 1,740 |
| `DoS Slowhttptest - Attempted` |  |  | 3,368 |  |  | 3,368 |
| `Heartbleed` |  |  | 11 |  |  | 11 |
| `Web Attack - Brute Force` |  |  |  | 73 |  | 73 |
| `Web Attack - Brute Force - Attempted` |  |  |  | 1,292 |  | 1,292 |
| `Web Attack - XSS` |  |  |  | 18 |  | 18 |
| `Web Attack - XSS - Attempted` |  |  |  | 655 |  | 655 |
| `Web Attack - SQL Injection` |  |  |  | 13 |  | 13 |
| `Web Attack - SQL Injection - Attempted` |  |  |  | 5 |  | 5 |
| `Infiltration` |  |  |  | 36 |  | 36 |
| `Infiltration - Attempted` |  |  |  | 45 |  | 45 |
| `Infiltration - Portscan` |  |  |  | 71,767 |  | 71,767 |
| `Portscan` |  |  |  |  | 159,066 | 159,066 |
| `DDoS` |  |  |  |  | 95,144 | 95,144 |
| `Botnet` |  |  |  |  | 736 | 736 |
| `Botnet - Attempted` |  |  |  |  | 4,067 | 4,067 |
| **Rows** | **371,624** | **322,078** | **496,641** | **362,076** | **547,557** | **2,099,976** |

## Terms and redistribution

Datasets are downloaded by each developer from UNB CIC (and the correction authors, if they host files). This repository never contains dataset rows. Test fixtures are synthetic. [VERIFY] the terms on each dataset page before publishing any derived statistics or samples.

## Citations

See `ml/config/datasets.yaml` for the full citation list. Cite the original dataset authors **and** the correction authors in the README and in any report.
