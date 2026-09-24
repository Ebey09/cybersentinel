# ADR 0002: CIC-Darknet2020 is not treated as attack or malware data

- Status: Accepted
- Date: 2026-09-24

## Context

CIC-Darknet2020 has two label layers. The first is traffic type (Tor, Non-Tor, VPN, Non-VPN). The second is application category (Audio-Streaming, Browsing, Chat, Email, File Transfer, P2P, Video-Streaming, VOIP). The dataset page describes it as a way to detect and characterize VPN and Tor applications. It was built by combining the earlier ISCXTor2016 and ISCXVPN2016 captures.

Nothing in the labels says whether a flow is harmful. People use Tor and VPNs for privacy, work, and circumvention. A SOC may still care, because Tor or unapproved VPN use can break policy, but that is a **policy signal**, not evidence of an attack.

Three further problems were found while reviewing the dataset:

1. **Capture-session artifact.** Non-Tor traffic comes from the Tor capture sessions and Non-VPN traffic from the VPN capture sessions. Both are "regular" traffic. A model that separates Non-Tor from Non-VPN is probably learning the capture environment, not a property of the traffic.
2. **Heavy imbalance.** One paper reports Tor at 1,393 flows against Non-Tor at 93,357. The same paper gives a different total sample count in its text, so no counts are hardcoded in this repo. They are computed from the data. [VERIFY]
3. **IP-address shortcut in the literature.** At least one paper split source and destination IPs into octet features and reported better results with them. In a lab capture, IPs identify hosts and sessions, so this is a shortcut, not a generalizable signal. This project excludes IPs.

## Decision

- Track B never uses the words malicious, malware, attack, threat, intrusion, compromise or exploit. This is enforced by `output_vocabulary.forbidden_terms` in the schema and by tests over every Track B experiment's display text.
- The primary Track B task is **3 classes: TOR, VPN, REGULAR**, with Non-Tor and Non-VPN merged into REGULAR.
- The original 4-class task is kept as a **diagnostic experiment only**. If the model separates Non-Tor from Non-VPN easily, that is reported as evidence of a capture artifact.
- Application category is a separate task with its own display text ("Application category: Chat").
- IP addresses, ports used as identifiers, flow IDs and timestamps are excluded from model inputs.

## Consequences

- Track B results are useful for policy monitoring and for showing ML methodology. They are not presented as threat detection.
- The 3-class choice loses the Non-Tor vs Non-VPN distinction, which was never meaningful for a SOC.

## Open verification items

- [VERIFY] exact label strings and casing in the CSV (`cybersentinel-ml inspect-labels`).
- [VERIFY] class counts computed from the real file.
- [VERIFY] whether the second label column is literally named `Label` twice in the raw header.

## References

- CIC-Darknet2020 page: https://www.unb.ca/cic/datasets/darknet2020.html
- Darknet Traffic Classification and Adversarial Attacks (reports Table 3 counts and the IP-octet features): https://arxiv.org/pdf/2206.06371
