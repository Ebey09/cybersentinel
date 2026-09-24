# Dataset Matrix

What each dataset is for, what a model trained on it may say, and what it must never say.
Machine-readable details live in `ml/config/datasets.yaml` and the schemas in `ml/config/schemas/`.

Items marked **[VERIFY]** are not confirmed yet. See [VERIFY.md](VERIFY.md) for how to check each one.

## Summary matrix

| | **Track A: Attack detection** | **Track B: Darknet/VPN characterization** |
|---|---|---|
| **Dataset** | CIC-IDS2017, corrected by Engelen et al. (WTMC 2021; CNS 2022 variant possible) [VERIFY which release] | CIC-Darknet2020 |
| **Purpose** | Detect and classify flows that resemble the attack classes in the corrected dataset | Characterize flows as Tor, VPN or regular traffic, and by application category |
| **Raw labels** | `BENIGN`, `FTP-Patator`, `SSH-Patator`, `DoS GoldenEye`, `DoS Hulk`, `DoS Slowhttptest`, `DoS slowloris`, `Heartbleed`, `Web Attack - Brute Force`, `Web Attack - XSS`, `Web Attack - Sql Injection`, `Infiltration`, `Bot`, `PortScan`, `DDoS`, plus `<attack> - Attempted` for every attack except PortScan (strings from the WTMC 2021 scripts) | `Label`: Tor, Non-Tor, VPN, Non-VPN. `Label.1`: Audio-Streaming, Browsing, Chat, Email, File Transfer, P2P, Video-Streaming, VOIP (strings from the literature) [VERIFY exact strings and casing] |
| **Model tasks** | Binary (BENIGN vs ATTACK); multi-class by attack family | 3-class traffic type (TOR, VPN, REGULAR); 8-class application category; 4-class diagnostic (never deployed) |
| **Features** | 85 CICFlowMeter flow features from the Engelen fork (94-column header minus 5 identifiers, 1 label, 3 excluded) [VERIFY against real header] | 66 CICFlowMeter flow features from upstream (84-column header plus a second label column, minus 5 identifiers, 2 labels, 12 excluded) [VERIFY against real header] |
| **Excluded from model** | Flow ID, IPs, source port, timestamp (identifiers or label proxies); ICMP Code/Type and Total Connection Flow Time (definitions unconfirmed) | Same identifiers; Active/Idle x8 (possible timestamp leakage from an upstream bug); Fwd/Bwd PSH and URG flags x4 (upstream bug) |
| **Extraction method** | CICFlowMeter, Engelen fork, pinned commit [VERIFY], flow timeout 120 s, activity timeout 5 s | CICFlowMeter, upstream, version used by CIC in 2020 unknown [VERIFY], timeouts unknown |
| **PCAP inference** | Allowed only after the parity test passes (ADR 0006). Blocked for now | Blocked. Extractor version unknown, so parity cannot be shown. CSV only |
| **Intended model** | Best of LR / RF / XGBoost on validation; calibrated probabilities; threshold set for a target false-positive rate | Best of LR / RF / XGBoost on validation; calibrated probabilities |
| **Allowed claims** | "This flow resembles `<attack family>` traffic as represented in CIC-IDS2017, with calibrated confidence p." "Top features that pushed the model toward this class were ..." | "Tor traffic detected." "VPN traffic detected." "Non-Tor / Non-VPN traffic." "Application category: Chat." "Policy/risk signal." |
| **Must NOT claim** | Detection of attack types not in the dataset ("zero-day", "APT", "ransomware"); that a flow **is** an attack (only that it resembles one); that lab performance transfers to real networks; that SHAP shows attacker intent or causality | That Tor/VPN traffic is malicious, an attack, a threat, malware or an intrusion; anything about user intent; that Non-Tor vs Non-VPN is a real traffic distinction; performance on PCAPs |
| **Main known limitations** | 2017 lab traffic; tiny rare classes; label assigned by IP and time window; Attempted label is a function of one feature (ADR 0004) | Strong class imbalance (Tor is a small class); Non-Tor and Non-VPN come from different capture sessions; unknown extractor version and possible upstream bugs |

## Why the two tracks are never combined

See [ADR 0001](adr/0001-two-separate-analytical-tracks.md). In short: no shared definition of "malicious", two different extractor versions with different flow definitions ([ADR 0005](adr/0005-separate-feature-schema-per-track.md)), and a real risk of the model learning "which dataset is this row from".

## Class distribution

**Not recorded here yet, on purpose.** Counts are computed from the downloaded files by `cybersentinel-ml inspect-labels` (now) and by the Phase 4 data report (later), and then copied here with the file SHA-256 they came from. Numbers quoted from papers do not agree with each other (one Darknet2020 paper gives two different totals), so none are hardcoded.

| Dataset file | SHA-256 | Class counts | Source of counts |
|---|---|---|---|
| (after download) | | | `inspect-labels` output |

## Terms and redistribution

Datasets are downloaded by each developer from UNB CIC (and the correction authors, if they host files). This repository never contains dataset rows. Test fixtures are synthetic. [VERIFY] the terms on each dataset page before publishing any derived statistics or samples.

## Citations

See `ml/config/datasets.yaml` for the full citation list. Cite the original dataset authors **and** the correction authors in the README and in any report.
