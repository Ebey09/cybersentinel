# ADR 0009: Build and validate the ML pipeline before the web application

- Status: Accepted
- Date: 2026-09-24

## Context

The largest technical risk is the data and model pipeline: dataset access, header and label surprises, memory limits on a laptop, leakage, and results that look too good. Authentication, dashboards and reports are well understood and low risk. Time is limited (about 5 to 8 hours a week).

## Decision

Build order: Phase 1 (contract) -> Phase 4 (ingestion and preprocessing) -> Phase 5 (baselines and evaluation) -> Phase 7 (XAI) -> then backend, database and auth, alerts, frontend, reports, hardening. Phase numbers are kept from the original plan for reference.

No authentication, frontend, dashboard or report code is written until the ML pipeline produces reproducible, leakage-checked results for Track A.

## Consequences

- By the end of Milestone A there is a complete, reproducible ML and XAI piece, even if the web app slips.
- Some backend decisions (API shapes for predictions and explanations) are informed by real model outputs instead of guesses.
