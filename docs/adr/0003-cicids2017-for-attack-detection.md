# ADR 0003: CIC-IDS2017 is the attack-detection dataset

- Status: Accepted
- Date: 2026-09-24

## Context

Track A needs labelled network flows covering several attack types, released publicly, with raw PCAPs available so the flow features can be reproduced. Candidates considered: CIC-IDS2017, CSE-CIC-IDS2018, UNSW-NB15, and older datasets (KDD Cup 99, NSL-KDD).

## Decision

Use CIC-IDS2017, in its corrected form (ADR 0004).

Reasons:

- Raw PCAPs are published, so flows can be regenerated with a pinned extractor. This makes PCAP parity (ADR 0006) possible at all.
- Flow features come from CICFlowMeter, which can be run on new PCAPs.
- Independent researchers have audited it and published corrections and code. That audit trail is valuable, and the audit itself is a strong interview topic.
- Covers several attack families: brute force (FTP/SSH), DoS/DDoS, web attacks, port scan, botnet, infiltration, Heartbleed.

## Consequences and limitations (stated in the README)

- It is a **lab dataset from 2017**. Good test scores show the model learned that lab's traffic. They do not show it will work on a real network.
- Several classes are tiny in the original release (Heartbleed, Infiltration, SQL injection). Counts in the corrected release must be computed, not assumed. [VERIFY]
- Attack traffic comes from known attacker hosts in known time windows. Labels were assigned from IPs and time, so IPs and timestamps are excluded from model inputs to avoid learning the labelling rule.
- The model can only claim attack types present in the dataset labels. It cannot detect "unknown attacks" and the UI does not say it can.

## Alternatives considered

- **CSE-CIC-IDS2018.** Larger (harder on a CPU laptop) with similar issues. Could be a later second Track A dataset using the same fork extractor.
- **UNSW-NB15.** Different feature extractor (Argus/Bro-based), so it would need its own schema and its own PCAP pipeline. Kept as a possible future adapter.
- **KDD Cup 99 / NSL-KDD.** Rejected: very old traffic, well-known flaws, no modern PCAP pipeline.

## References

- CIC-IDS2017 page: https://www.unb.ca/cic/datasets/ids-2017.html
- Engelen et al., WTMC 2021: https://github.com/GintsEngelen/WTMC2021-Code
