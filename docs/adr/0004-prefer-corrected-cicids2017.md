# ADR 0004: Use the corrected CIC-IDS2017 and map "Attempted" flows to BENIGN

- Status: Accepted (release choice pending [VERIFY])
- Date: 2026-09-24

## Context

Engelen, Rimmer and Joosen (WTMC 2021) audited CIC-IDS2017 and found problems in both the labels and the flow extractor. Their fork of CICFlowMeter lists these fixes in its README:

1. A TCP flow is no longer terminated after a single FIN packet. It ends after FINs are exchanged in both directions.
2. RST packets are no longer ignored. An RST also terminates the flow.
3. Active and Idle time features no longer encode an absolute timestamp.
4. Fwd/Bwd PSH and URG flag counts are now incremented correctly.

They then relabelled the regenerated flows with a script. From that script (verified in `labelling_CSV_flows.py`): if a flow falls in an attack window, is TCP, and carries **0 forward payload bytes** (`Total Length of Fwd Packet == 0`), it is labelled `<attack> - Attempted` instead of `<attack>`. PortScan has no Attempted variant. In their experiments, all Attempted flows were mapped to BENIGN (`MakeDataNumpyFriendly.py`).

A follow-up paper (Liu, Engelen et al., CNS 2022) applied a similar process to CIC-IDS2017 and CSE-CIC-IDS2018. Its pipeline also runs pcapfix and reordercap on the PCAPs before extraction. Lanvin et al. (CRiSIS 2022) independently report errors in CIC-IDS2017 and show they change detection results.

## Decision

- Use the corrected dataset, not the original CSVs.
- **Attempted policy: map to BENIGN**, matching Engelen et al., so results are comparable with theirs. Reasoning: an Attempted flow has no attack payload, so its features do not look like the attack. Calling it an attack would be label noise. Dropping these flows would remove realistic "hard negatives" and inflate precision.
- Failed attempts still matter to a SOC. They are covered by the **rule-based alert engine** (for example, bursts of short connection attempts), not by the classifier.

## Consequences

- **Label-feature coupling:** the Attempted rule is a threshold on `fwd_payload_bytes_total`. Mapping Attempted to BENIGN means part of the label is a direct function of one feature. The evaluation reports this, and SHAP results for that feature are interpreted with it in mind.
- The corrected release has to be identified precisely, because WTMC 2021 and CNS 2022 differ in process and possibly in columns.

## Open verification items

- [VERIFY] Which release is used: WTMC 2021 or CNS 2022, and whether pre-built CSVs are downloadable (the authors' site was not reachable when this ADR was written).
- [VERIFY] The real CSV header matches `raw_columns` in the Track A schema (the schema currently uses the fork's current 94-column header).
- Label strings in the chosen release match those in `track_a_*.yaml`. Resolved for the CNS2022 release (ADR 0012): the maps now use the 27 observed CNS2022 labels, see VERIFY V5.
- If regenerating from PCAP: the labelling script shifts timestamps by `TIME_DIFFERENCE` (the timezone of the machine that ran CICFlowMeter vs New Brunswick). Getting this wrong silently mislabels every attack window.

## References

- Engelen, Rimmer, Joosen. Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study. IEEE SPW 2021. Code: https://github.com/GintsEngelen/WTMC2021-Code
- Fixed extractor: https://github.com/GintsEngelen/CICFlowMeter
- Liu, Engelen, Lynar, Essam, Joosen. Error Prevalence in NIDS datasets. IEEE CNS 2022. Code: https://github.com/GintsEngelen/CNS2022_Code
- Lanvin et al. Errors in the CICIDS2017 Dataset and the Significant Differences in Detection Performances It Makes. CRiSIS 2022: https://dl.acm.org/doi/10.1007/978-3-031-31108-6_2
