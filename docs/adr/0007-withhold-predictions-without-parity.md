# ADR 0007: Withhold ML predictions when the contract cannot be demonstrated

- Status: Accepted
- Date: 2026-09-24

## Context

When the data contract (ADR 0006) cannot be demonstrated for a batch of flows, there are three options: predict anyway with a warning, predict with lowered confidence, or refuse. Analysts learn to ignore warnings, and there is no principled way to "lower" a confidence score for an input distribution the model never saw.

## Decision

**Fail closed.** The inference gate (`cybersentinel_ml.contract.gate.evaluate_inference_gate`) returns `allowed=False` if any check fails, and then:

- No prediction, confidence or SHAP explanation is produced or stored for that batch and track.
- The UI and API show the gate's reasons in plain language, for example: *"ML prediction withheld for Track A. Reasons: PCAP-to-feature parity is 'not_demonstrated' for this track, so features extracted from PCAP cannot be trusted to match the training data. Traffic statistics and rule-based alerts are still available for this data."*
- Traffic statistics and rule-based alerts, which do not depend on the model, still run.
- The decision and its checks are logged, and later written to the audit log.

Checks that block inference: schema not verified, model trained on a different schema (id, version or content hash), preprocessing version mismatch, unknown or different extractor (name, repository, commit, timeouts), extractor commit not pinned, PCAP parity not demonstrated, PCAP flows not produced by the platform's own extractor, missing or unexpected features, wrong feature order, non-numeric features.

One case produces a **warning, not a block**: a CSV upload whose header matches but whose extractor provenance is only asserted by the uploader. Predictions are shown with "provenance asserted, not verified".

## Consequences

- Early in the project, almost nothing is allowed through. That is correct. Both schemas are drafts, so even the gate's own tests show inference blocked on the committed schemas.
- Each new data path has to earn inference by passing the contract, which is visible in code and tests.
- A good interview story: the system refuses to guess and says why.

## Alternatives considered

- **Predict with a warning banner.** Rejected: warnings get ignored, and the prediction still ends up in reports and alerts.
- **Out-of-distribution score only.** Kept as an *additional* per-flow warning inside an allowed batch (planned), not a replacement for the gate.
