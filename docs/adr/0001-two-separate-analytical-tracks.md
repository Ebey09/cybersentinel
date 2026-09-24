# ADR 0001: Two separate analytical tracks

- Status: Accepted
- Date: 2026-09-24

## Context

The project uses two datasets that answer different questions:

- **CIC-IDS2017 (corrected)** labels flows as benign or as one of several attack types generated in a lab.
- **CIC-Darknet2020** labels flows as Tor, Non-Tor, VPN or Non-VPN, plus an application category. It has no attack labels.

A single "malicious vs benign" model trained on both would need a shared definition of "malicious". None exists across these datasets. Treating Tor/VPN as malicious would be a claim the data does not support. Merging the datasets would also mix two capture environments and two different extractor versions (see ADR 0005), so a model could learn "which dataset did this row come from" instead of anything about the traffic.

## Decision

The platform has two independent tracks. Each has its own schema, experiments, models, metrics and output vocabulary.

| | Track A: Attack detection | Track B: Darknet/VPN characterization |
|---|---|---|
| Dataset | Corrected CIC-IDS2017 | CIC-Darknet2020 |
| Question | Does this flow resemble an attack class in the dataset? | Does this flow resemble Tor or VPN traffic, and which application category? |
| Output words | benign, attack, attack family names from the dataset | Tor traffic detected, VPN traffic detected, Non-Tor/Non-VPN traffic, application category, policy/risk signal |
| Must never say | anything about attack types not in the dataset | malicious, attack, threat, malware, intrusion |

In the UI and in alerts the two outputs are shown side by side and never combined into one score. A Track B result can raise a LOW severity **policy** alert ("VPN traffic detected, check against acceptable-use policy"), never a threat alert.

## Consequences

- Two schemas, two sets of experiments, and two model families to maintain.
- Honest outputs. An interviewer asking "why is Tor malicious?" gets "it isn't, and the system never says it is".
- Each track's metrics only describe performance on its own dataset distribution.

## Alternatives considered

- **One combined binary model.** Rejected: no shared label semantics, and dataset-of-origin leakage.
- **Darknet2020 only.** Rejected: the project would stop being a threat-detection platform.
- **Stacked model (Track B output as a Track A feature).** Rejected for now: no labelled data shows Tor/VPN usage changes attack likelihood in CIC-IDS2017. Could only be revisited with a dataset that has both label types.

## References

- CIC-Darknet2020 page: https://www.unb.ca/cic/datasets/darknet2020.html
- CIC-IDS2017 page: https://www.unb.ca/cic/datasets/ids-2017.html
