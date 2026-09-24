# Track B: Darknet/VPN traffic characterization (CIC-Darknet2020)

> Generated from the schema YAML by `cybersentinel-ml schema-docs`. Do not edit by hand.

- Schema: `track_b.cicdarknet2020` v0.2.0 (status: **draft**)
- Content SHA-256: `d38afd3e0cad53d069314a1d5c455366f900b3e06820e2ce87b3cbb497dba5ce`
- Dataset: CIC-Darknet2020
- Extractor: CICFlowMeter (upstream, ahlashkari), commit `[VERIFY] unknown. The version CIC used in 2020 is not documented in the sources checked.` (commit status: **to_verify**)
- Flow timeout: None us, activity timeout: None us
- PCAP parity: **not_demonstrated**
- Preprocessing version: 0.1.0
- Raw columns: 85, model features: 66, excluded: 12, identifiers: 5

## Model input features (in order)

| # | name | source column | dtype | unit | range | missing values | scaling (LR) | encoding | PCAP | status | meaning |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `dst_port` | Dst Port | int64 |  | [0.0, 65535.0] | reject_row | excluded | numeric_trees_only | unverified | draft | Destination transport port. Kept for tree models only (a port number is not a linear quantity). Every experiment also runs a no-port ablation to detect port shortcut learning. |
| 2 | `protocol` | Protocol | int64 |  | [0.0, 255.0] | reject_row | none | one_hot_fixed_categories | unverified | draft | IANA IP protocol number (6 = TCP, 17 = UDP). [VERIFY] observed protocol values in the real CSV (CICFlowMeter may emit 0 for non-TCP/UDP). |
| 3 | `flow_duration` | Flow Duration | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Time between the first and last packet of the flow.  |
| 4 | `fwd_packets_total` | Total Fwd Packet | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Number of packets sent from initiator to responder.  |
| 5 | `bwd_packets_total` | Total Bwd packets | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Number of packets sent from responder to initiator.  |
| 6 | `fwd_payload_bytes_total` | Total Length of Fwd Packet | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Total payload bytes in the forward direction.  |
| 7 | `bwd_payload_bytes_total` | Total Length of Bwd Packet | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Total payload bytes in the backward direction.  |
| 8 | `fwd_pkt_len_max` | Fwd Packet Length Max | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Largest forward packet payload length.  |
| 9 | `fwd_pkt_len_min` | Fwd Packet Length Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Smallest forward packet payload length.  |
| 10 | `fwd_pkt_len_mean` | Fwd Packet Length Mean | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Mean forward packet payload length.  |
| 11 | `fwd_pkt_len_std` | Fwd Packet Length Std | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Standard deviation of forward packet payload length.  |
| 12 | `bwd_pkt_len_max` | Bwd Packet Length Max | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Largest backward packet payload length.  |
| 13 | `bwd_pkt_len_min` | Bwd Packet Length Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Smallest backward packet payload length.  |
| 14 | `bwd_pkt_len_mean` | Bwd Packet Length Mean | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Mean backward packet payload length.  |
| 15 | `bwd_pkt_len_std` | Bwd Packet Length Std | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Standard deviation of backward packet payload length.  |
| 16 | `flow_bytes_per_s` | Flow Bytes/s | float64 | bytes per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | unverified | draft | Payload bytes per second over the whole flow. Undefined (Infinity/NaN) when duration is 0.  |
| 17 | `flow_packets_per_s` | Flow Packets/s | float64 | packets per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | unverified | draft | Packets per second over the whole flow. Undefined (Infinity/NaN) when duration is 0.  |
| 18 | `flow_iat_mean` | Flow IAT Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Mean inter-arrival time between packets in either direction.  |
| 19 | `flow_iat_std` | Flow IAT Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Standard deviation of inter-arrival time, both directions.  |
| 20 | `flow_iat_max` | Flow IAT Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Maximum inter-arrival time, both directions.  |
| 21 | `flow_iat_min` | Flow IAT Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Minimum inter-arrival time, both directions.  |
| 22 | `fwd_iat_total` | Fwd IAT Total | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Sum of inter-arrival times between forward packets.  |
| 23 | `fwd_iat_mean` | Fwd IAT Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Mean inter-arrival time between forward packets.  |
| 24 | `fwd_iat_std` | Fwd IAT Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Standard deviation of forward inter-arrival time.  |
| 25 | `fwd_iat_max` | Fwd IAT Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Maximum forward inter-arrival time.  |
| 26 | `fwd_iat_min` | Fwd IAT Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Minimum forward inter-arrival time.  |
| 27 | `bwd_iat_total` | Bwd IAT Total | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Sum of inter-arrival times between backward packets.  |
| 28 | `bwd_iat_mean` | Bwd IAT Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Mean inter-arrival time between backward packets.  |
| 29 | `bwd_iat_std` | Bwd IAT Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Standard deviation of backward inter-arrival time.  |
| 30 | `bwd_iat_max` | Bwd IAT Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Maximum backward inter-arrival time.  |
| 31 | `bwd_iat_min` | Bwd IAT Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Minimum backward inter-arrival time.  |
| 32 | `fwd_header_bytes_total` | Fwd Header Length | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Total bytes of transport/network headers in the forward direction.  |
| 33 | `bwd_header_bytes_total` | Bwd Header Length | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Total bytes of transport/network headers in the backward direction.  |
| 34 | `fwd_packets_per_s` | Fwd Packets/s | float64 | packets per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | unverified | draft | Forward packets per second.  |
| 35 | `bwd_packets_per_s` | Bwd Packets/s | float64 | packets per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | unverified | draft | Backward packets per second.  |
| 36 | `pkt_len_min` | Packet Length Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Smallest packet payload length, both directions.  |
| 37 | `pkt_len_max` | Packet Length Max | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Largest packet payload length, both directions.  |
| 38 | `pkt_len_mean` | Packet Length Mean | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Mean packet payload length, both directions.  |
| 39 | `pkt_len_std` | Packet Length Std | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Standard deviation of packet payload length, both directions.  |
| 40 | `pkt_len_var` | Packet Length Variance | float64 | bytes squared | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Variance of packet payload length, both directions.  |
| 41 | `fin_flag_count` | FIN Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with FIN set. [VERIFY] whether CICFlowMeter stores a count or a 0/1 indicator.  |
| 42 | `syn_flag_count` | SYN Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with SYN set. [VERIFY] count vs 0/1 indicator.  |
| 43 | `rst_flag_count` | RST Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with RST set. [VERIFY] count vs 0/1 indicator.  |
| 44 | `psh_flag_count` | PSH Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with PSH set. [VERIFY] count vs 0/1 indicator.  |
| 45 | `ack_flag_count` | ACK Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with ACK set. [VERIFY] count vs 0/1 indicator.  |
| 46 | `urg_flag_count` | URG Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with URG set. [VERIFY] count vs 0/1 indicator.  |
| 47 | `cwr_flag_count` | CWR Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with CWR set. [VERIFY] count vs 0/1 indicator.  |
| 48 | `ece_flag_count` | ECE Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Packets with ECE set. [VERIFY] count vs 0/1 indicator.  |
| 49 | `down_up_ratio` | Down/Up Ratio | float64 | ratio | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Ratio of backward to forward packets. [VERIFY] integer vs float division in the extractor.  |
| 50 | `avg_packet_size` | Average Packet Size | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average packet size over the flow.  |
| 51 | `fwd_segment_size_avg` | Fwd Segment Size Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average forward segment size.  |
| 52 | `bwd_segment_size_avg` | Bwd Segment Size Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average backward segment size.  |
| 53 | `fwd_bytes_per_bulk_avg` | Fwd Bytes/Bulk Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average bytes per bulk transfer, forward.  |
| 54 | `fwd_packets_per_bulk_avg` | Fwd Packet/Bulk Avg | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average packets per bulk transfer, forward.  |
| 55 | `fwd_bulk_rate_avg` | Fwd Bulk Rate Avg | float64 | bytes per second | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average bulk transfer rate, forward.  |
| 56 | `bwd_bytes_per_bulk_avg` | Bwd Bytes/Bulk Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average bytes per bulk transfer, backward.  |
| 57 | `bwd_packets_per_bulk_avg` | Bwd Packet/Bulk Avg | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average packets per bulk transfer, backward.  |
| 58 | `bwd_bulk_rate_avg` | Bwd Bulk Rate Avg | float64 | bytes per second | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average bulk transfer rate, backward.  |
| 59 | `subflow_fwd_packets` | Subflow Fwd Packets | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average forward packets per subflow.  |
| 60 | `subflow_fwd_bytes` | Subflow Fwd Bytes | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average forward bytes per subflow.  |
| 61 | `subflow_bwd_packets` | Subflow Bwd Packets | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average backward packets per subflow.  |
| 62 | `subflow_bwd_bytes` | Subflow Bwd Bytes | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Average backward bytes per subflow.  |
| 63 | `fwd_init_win_bytes` | FWD Init Win Bytes | float64 | bytes | [-1.0, 65535.0] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | TCP window size in the first forward packet. [VERIFY] sentinel value (expected -1) when not TCP / not observed.  |
| 64 | `bwd_init_win_bytes` | Bwd Init Win Bytes | float64 | bytes | [-1.0, 65535.0] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | TCP window size in the first backward packet. [VERIFY] sentinel value (expected -1) when not TCP / not observed.  |
| 65 | `fwd_active_data_packets` | Fwd Act Data Pkts | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Forward packets carrying at least 1 byte of payload.  |
| 66 | `fwd_seg_size_min` | Fwd Seg Size Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | unverified | draft | Minimum forward segment size. [VERIFY] exact definition in FlowFeature/BasicFlow source (header vs payload size).  |

## Derived features (appended after schema features)

- `zero_duration_flag`: 1.0 if flow_duration == 0 else 0.0. Rate features are undefined for zero-duration flows. The flag keeps that information after imputation.

## Excluded features

| name | source column | reason |
|---|---|---|
| `fwd_psh_flags` | Fwd PSH Flags | Excluded: upstream CICFlowMeter did not increment these correctly (bug fixed in the Engelen fork). Values are unreliable. [VERIFY] with EDA (expect near-constant values). |
| `bwd_psh_flags` | Bwd PSH Flags | Excluded: upstream CICFlowMeter did not increment these correctly (bug fixed in the Engelen fork). Values are unreliable. [VERIFY] with EDA (expect near-constant values). |
| `fwd_urg_flags` | Fwd URG Flags | Excluded: upstream CICFlowMeter did not increment these correctly (bug fixed in the Engelen fork). Values are unreliable. [VERIFY] with EDA (expect near-constant values). |
| `bwd_urg_flags` | Bwd URG Flags | Excluded: upstream CICFlowMeter did not increment these correctly (bug fixed in the Engelen fork). Values are unreliable. [VERIFY] with EDA (expect near-constant values). |
| `active_mean` | Active Mean | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |
| `active_std` | Active Std | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |
| `active_max` | Active Max | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |
| `active_min` | Active Min | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |
| `idle_mean` | Idle Mean | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |
| `idle_std` | Idle Std | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |
| `idle_max` | Idle Max | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |
| `idle_min` | Idle Min | Excluded: upstream CICFlowMeter encoded an absolute timestamp in Active/Idle features (bug documented by Engelen et al.). If CIC-Darknet2020 was generated with an affected version, these features leak capture time. Re-enable only if the EDA diagnostic shows no timestamp-like values. [VERIFY] |

## Identifier columns (never model inputs)

| name | source column | used for | reason |
|---|---|---|---|
| `flow_id` | Flow ID | display, alert_rules, related_flows | Identifier. Encodes IPs and ports, so it would leak lab topology into the model. |
| `src_ip` | Src IP | display, alert_rules, related_flows | Lab-specific. Attacker and victim IPs are fixed in the capture, so the model would learn addresses, not behaviour. Kept for display and alert rules only. |
| `src_port` | Src Port | display, alert_rules, related_flows | Ephemeral client port, mostly random noise, and a potential session identifier. |
| `dst_ip` | Dst IP | display, alert_rules, related_flows | Lab-specific, same reason as Src IP. Kept for display and alert rules only. |
| `timestamp` | Timestamp | display, alert_rules, related_flows | Labels were assigned by time window, so time is a direct label proxy. Kept for display, related-flow lookup and timelines only. |

## Positional renames (declared, applied by the dataset adapter)

- Position 84: raw `Label` -> `Label (column 84)`. [VERIFY] V4. Draft assumption: the raw CSV names both label columns 'Label' (traffic type, then application category). 'Label.1' is what pandas would call the second one, not a name taken from the file. If the real header gives the second column its own name, use that name in raw_columns and delete this rename.

## Label columns

- `Label` -> `traffic_type`. [VERIFY] exact strings. Literature reports Tor, Non-Tor, VPN, Non-VPN.
- `Label (column 84)` -> `application_category`. [VERIFY] V4: raw column name (see positional_renames). V6: exact strings and casing. Eight categories are reported: audio streaming, browsing, chat, email, file transfer, P2P, video streaming, VoIP. The raw spelling is not confirmed (for example 'File Transfer' vs 'File-Transfer').

## Output vocabulary

- Allowed: Tor traffic detected, VPN traffic detected, Non-Tor traffic, Non-VPN traffic, anonymized traffic, application category, policy/risk signal, confidence
- Forbidden: malicious, malware, attack, threat, intrusion, compromise, exploit
