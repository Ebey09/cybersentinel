# Track A: Attack detection (corrected CIC-IDS2017)

> Generated from the schema YAML by `cybersentinel-ml schema-docs`. Do not edit by hand.

- Schema: `track_a.cicids2017_corrected` v0.3.0 (status: **draft**)
- Content SHA-256: `37e254a78641a823fa398384cca803439052d33a6c7b28f3fd035807fc558076`
- Dataset: CNS2022 Improved CIC-IDS2017 (Liu, Engelen et al.)
- Extractor: CICFlowMeter (Engelen et al. fork), commit `[VERIFY] Author tool identified, exact generation commit not published/documented. Do not infer it.` (commit status: **to_verify**)
- Flow timeout: 120000000 us, activity timeout: 5000000 us
- PCAP parity: **not_demonstrated**
- Preprocessing version: 0.1.0
- Raw columns: 91, model features: 80, excluded: 3, identifiers: 6

## Model input features (in order)

| # | name | source column | dtype | unit | range | missing values | scaling (LR) | encoding | PCAP | status | meaning |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `dst_port` | Dst Port | int64 |  | [0.0, 65535.0] | reject_row | excluded | numeric_trees_only | pinned_extractor_only | draft | Destination transport port. Kept for tree models only (a port number is not a linear quantity). Every experiment also runs a no-port ablation to detect port shortcut learning. |
| 2 | `protocol` | Protocol | int64 |  | [0.0, 255.0] | reject_row | none | one_hot_fixed_categories | pinned_extractor_only | draft | IANA IP protocol number (6 = TCP, 17 = UDP). [VERIFY] observed protocol values in the real CSV (CICFlowMeter may emit 0 for non-TCP/UDP). |
| 3 | `flow_duration` | Flow Duration | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Time between the first and last packet of the flow.  |
| 4 | `fwd_packets_total` | Total Fwd Packet | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of packets sent from initiator to responder.  |
| 5 | `bwd_packets_total` | Total Bwd packets | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of packets sent from responder to initiator.  |
| 6 | `fwd_payload_bytes_total` | Total Length of Fwd Packet | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Total payload bytes in the forward direction. Label coupling: Engelen's labelling marks a TCP attack-window flow as '<attack> - Attempted' exactly when this value is 0. With Attempted mapped to BENIGN, this feature partly encodes the labelling rule. Reported in the evaluation, see docs/adr/0004. |
| 7 | `bwd_payload_bytes_total` | Total Length of Bwd Packet | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Total payload bytes in the backward direction.  |
| 8 | `fwd_pkt_len_max` | Fwd Packet Length Max | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Largest forward packet payload length.  |
| 9 | `fwd_pkt_len_min` | Fwd Packet Length Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Smallest forward packet payload length.  |
| 10 | `fwd_pkt_len_mean` | Fwd Packet Length Mean | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean forward packet payload length.  |
| 11 | `fwd_pkt_len_std` | Fwd Packet Length Std | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of forward packet payload length.  |
| 12 | `bwd_pkt_len_max` | Bwd Packet Length Max | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Largest backward packet payload length.  |
| 13 | `bwd_pkt_len_min` | Bwd Packet Length Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Smallest backward packet payload length.  |
| 14 | `bwd_pkt_len_mean` | Bwd Packet Length Mean | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean backward packet payload length.  |
| 15 | `bwd_pkt_len_std` | Bwd Packet Length Std | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of backward packet payload length.  |
| 16 | `flow_bytes_per_s` | Flow Bytes/s | float64 | bytes per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Payload bytes per second over the whole flow. Undefined (Infinity/NaN) when duration is 0.  |
| 17 | `flow_packets_per_s` | Flow Packets/s | float64 | packets per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets per second over the whole flow. Undefined (Infinity/NaN) when duration is 0.  |
| 18 | `flow_iat_mean` | Flow IAT Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean inter-arrival time between packets in either direction.  |
| 19 | `flow_iat_std` | Flow IAT Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of inter-arrival time, both directions.  |
| 20 | `flow_iat_max` | Flow IAT Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Maximum inter-arrival time, both directions.  |
| 21 | `flow_iat_min` | Flow IAT Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Minimum inter-arrival time, both directions.  |
| 22 | `fwd_iat_total` | Fwd IAT Total | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Sum of inter-arrival times between forward packets.  |
| 23 | `fwd_iat_mean` | Fwd IAT Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean inter-arrival time between forward packets.  |
| 24 | `fwd_iat_std` | Fwd IAT Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of forward inter-arrival time.  |
| 25 | `fwd_iat_max` | Fwd IAT Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Maximum forward inter-arrival time.  |
| 26 | `fwd_iat_min` | Fwd IAT Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Minimum forward inter-arrival time.  |
| 27 | `bwd_iat_total` | Bwd IAT Total | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Sum of inter-arrival times between backward packets.  |
| 28 | `bwd_iat_mean` | Bwd IAT Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean inter-arrival time between backward packets.  |
| 29 | `bwd_iat_std` | Bwd IAT Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of backward inter-arrival time.  |
| 30 | `bwd_iat_max` | Bwd IAT Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Maximum backward inter-arrival time.  |
| 31 | `bwd_iat_min` | Bwd IAT Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Minimum backward inter-arrival time.  |
| 32 | `fwd_psh_flags` | Fwd PSH Flags | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of forward packets with the PSH flag set. Correctly incremented in the Engelen fork (bug fix listed in the fork README). |
| 33 | `bwd_psh_flags` | Bwd PSH Flags | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of backward packets with the PSH flag set. Correctly incremented in the Engelen fork (bug fix listed in the fork README). |
| 34 | `fwd_urg_flags` | Fwd URG Flags | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of forward packets with the URG flag set. Correctly incremented in the Engelen fork (bug fix listed in the fork README). |
| 35 | `bwd_urg_flags` | Bwd URG Flags | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of backward packets with the URG flag set. Correctly incremented in the Engelen fork (bug fix listed in the fork README). |
| 36 | `fwd_rst_flags` | Fwd RST Flags | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of forward packets with the RST flag set.  |
| 37 | `bwd_rst_flags` | Bwd RST Flags | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Number of backward packets with the RST flag set.  |
| 38 | `fwd_header_bytes_total` | Fwd Header Length | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Total bytes of transport/network headers in the forward direction.  |
| 39 | `bwd_header_bytes_total` | Bwd Header Length | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Total bytes of transport/network headers in the backward direction.  |
| 40 | `fwd_packets_per_s` | Fwd Packets/s | float64 | packets per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Forward packets per second.  |
| 41 | `bwd_packets_per_s` | Bwd Packets/s | float64 | packets per second | [0.0, inf] | inf_to_nan_then_train_median_plus_zero_duration_flag | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Backward packets per second.  |
| 42 | `pkt_len_min` | Packet Length Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Smallest packet payload length, both directions.  |
| 43 | `pkt_len_max` | Packet Length Max | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Largest packet payload length, both directions.  |
| 44 | `pkt_len_mean` | Packet Length Mean | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean packet payload length, both directions.  |
| 45 | `pkt_len_std` | Packet Length Std | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of packet payload length, both directions.  |
| 46 | `pkt_len_var` | Packet Length Variance | float64 | bytes squared | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Variance of packet payload length, both directions.  |
| 47 | `fin_flag_count` | FIN Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with FIN set. [VERIFY] whether CICFlowMeter stores a count or a 0/1 indicator.  |
| 48 | `syn_flag_count` | SYN Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with SYN set. [VERIFY] count vs 0/1 indicator.  |
| 49 | `rst_flag_count` | RST Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with RST set. [VERIFY] count vs 0/1 indicator.  |
| 50 | `psh_flag_count` | PSH Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with PSH set. [VERIFY] count vs 0/1 indicator.  |
| 51 | `ack_flag_count` | ACK Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with ACK set. [VERIFY] count vs 0/1 indicator.  |
| 52 | `urg_flag_count` | URG Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with URG set. [VERIFY] count vs 0/1 indicator.  |
| 53 | `cwr_flag_count` | CWR Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with CWR set. [VERIFY] count vs 0/1 indicator.  |
| 54 | `ece_flag_count` | ECE Flag Count | float64 | count | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Packets with ECE set. [VERIFY] count vs 0/1 indicator.  |
| 55 | `down_up_ratio` | Down/Up Ratio | float64 | ratio | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Ratio of backward to forward packets. [VERIFY] integer vs float division in the extractor.  |
| 56 | `avg_packet_size` | Average Packet Size | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average packet size over the flow.  |
| 57 | `fwd_segment_size_avg` | Fwd Segment Size Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average forward segment size.  |
| 58 | `bwd_segment_size_avg` | Bwd Segment Size Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average backward segment size.  |
| 59 | `fwd_bytes_per_bulk_avg` | Fwd Bytes/Bulk Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average bytes per bulk transfer, forward.  |
| 60 | `fwd_packets_per_bulk_avg` | Fwd Packet/Bulk Avg | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average packets per bulk transfer, forward.  |
| 61 | `fwd_bulk_rate_avg` | Fwd Bulk Rate Avg | float64 | bytes per second | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average bulk transfer rate, forward.  |
| 62 | `bwd_bytes_per_bulk_avg` | Bwd Bytes/Bulk Avg | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average bytes per bulk transfer, backward.  |
| 63 | `bwd_packets_per_bulk_avg` | Bwd Packet/Bulk Avg | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average packets per bulk transfer, backward.  |
| 64 | `bwd_bulk_rate_avg` | Bwd Bulk Rate Avg | float64 | bytes per second | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average bulk transfer rate, backward.  |
| 65 | `subflow_fwd_packets` | Subflow Fwd Packets | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average forward packets per subflow.  |
| 66 | `subflow_fwd_bytes` | Subflow Fwd Bytes | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average forward bytes per subflow.  |
| 67 | `subflow_bwd_packets` | Subflow Bwd Packets | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average backward packets per subflow.  |
| 68 | `subflow_bwd_bytes` | Subflow Bwd Bytes | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Average backward bytes per subflow.  |
| 69 | `fwd_init_win_bytes` | FWD Init Win Bytes | float64 | bytes | [-1.0, 65535.0] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | TCP window size in the first forward packet. [VERIFY] sentinel value (expected -1) when not TCP / not observed.  |
| 70 | `bwd_init_win_bytes` | Bwd Init Win Bytes | float64 | bytes | [-1.0, 65535.0] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | TCP window size in the first backward packet. [VERIFY] sentinel value (expected -1) when not TCP / not observed.  |
| 71 | `fwd_active_data_packets` | Fwd Act Data Pkts | float64 | packets | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Forward packets carrying at least 1 byte of payload.  |
| 72 | `fwd_seg_size_min` | Fwd Seg Size Min | float64 | bytes | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Minimum forward segment size. [VERIFY] exact definition in FlowFeature/BasicFlow source (header vs payload size).  |
| 73 | `active_mean` | Active Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean time the flow was active before becoming idle (activity timeout). Fork fix: no longer encodes an absolute timestamp (fork README). |
| 74 | `active_std` | Active Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of active periods. Fork fix: no longer encodes an absolute timestamp (fork README). |
| 75 | `active_max` | Active Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Longest active period. Fork fix: no longer encodes an absolute timestamp (fork README). |
| 76 | `active_min` | Active Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Shortest active period. Fork fix: no longer encodes an absolute timestamp (fork README). |
| 77 | `idle_mean` | Idle Mean | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Mean idle period between active periods. Fork fix: no longer encodes an absolute timestamp (fork README). |
| 78 | `idle_std` | Idle Std | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Standard deviation of idle periods. Fork fix: no longer encodes an absolute timestamp (fork README). |
| 79 | `idle_max` | Idle Max | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Longest idle period. Fork fix: no longer encodes an absolute timestamp (fork README). |
| 80 | `idle_min` | Idle Min | float64 | microseconds | [0.0, inf] | inf_to_nan_then_train_median | signed_log1p_then_standard | numeric | pinned_extractor_only | draft | Shortest idle period. Fork fix: no longer encodes an absolute timestamp (fork README). |

## Derived features (appended after schema features)

- `zero_duration_flag`: 1.0 if flow_duration == 0 else 0.0. Rate features are undefined for zero-duration flows. The flag keeps that information after imputation.

## Excluded features

| name | source column | reason |
|---|---|---|
| `icmp_code` | ICMP Code | Excluded until the non-ICMP sentinel value and encoding are confirmed in EDA. |
| `icmp_type` | ICMP Type | Excluded until the non-ICMP sentinel value and encoding are confirmed in EDA. |
| `total_tcp_flow_time` | Total TCP Flow Time | Excluded until V16 confirms its definition, unit and treatment. Present in the CNS2022 release. The later fork column Total Connection Flow Time is not in this release and is not assumed to be the same feature. |

## Identifier columns (never model inputs)

| name | source column | used for | reason |
|---|---|---|---|
| `flow_id` | Flow ID | display, alert_rules, related_flows | Identifier. Encodes IPs and ports, so it would leak lab topology into the model. |
| `src_ip` | Src IP | display, alert_rules, related_flows | Lab-specific. Attacker and victim IPs are fixed in the capture, so the model would learn addresses, not behaviour. Kept for display and alert rules only. |
| `src_port` | Src Port | display, alert_rules, related_flows | Ephemeral client port, mostly random noise, and a potential session identifier. |
| `dst_ip` | Dst IP | display, alert_rules, related_flows | Lab-specific, same reason as Src IP. Kept for display and alert rules only. |
| `timestamp` | Timestamp | display, alert_rules, related_flows | Labels were assigned by time window, so time is a direct label proxy. Kept for display, related-flow lookup and timelines only. |
| `row_id` | id | display, related_flows | Row number written by the CNS2022 labelling notebook (print_index), not a CICFlowMeter feature. It follows file order, which follows time, so it would act as a label proxy. |

## Label columns

- `Label` -> `label`. [VERIFY] V5: exact label strings in the CNS2022 release. Attempted flows keep their own label string and map to BENIGN in the experiments (ADR 0004); there is no separate Attempted class.
- `Attempted Category` -> `attempted_category`. Label-side metadata added by the CNS2022 labelling notebook (default -1, set per labelled attempt). Derived from the labelling itself, so it is never a model input and never a training target. Category definitions are on the CNS2022 Tools_Documentation page.

## Output vocabulary

- Allowed: benign, attack, attack category, suspected, confidence
