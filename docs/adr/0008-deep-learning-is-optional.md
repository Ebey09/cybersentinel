# ADR 0008: Deep learning is an optional comparison, not a default component

- Status: Accepted
- Date: 2026-09-24

## Context

Flow features are tabular: about 60 to 90 numeric columns per row. On tabular data, tree ensembles usually match or beat deep networks and are cheaper to train and explain. This is reported, for example, by Grinsztajn, Oyallon and Varoquaux (NeurIPS 2022 Datasets and Benchmarks track). Development is CPU-only, with about 5 to 8 hours a week.

## Decision

- Phase 5 trains Logistic Regression, Random Forest and XGBoost on identical splits, seeds and preprocessing.
- A small PyTorch MLP is **optional** (Phase 6). It is trained only if Milestone A finishes with time to spare, on the same splits and preprocessing, and added to the comparison table.
- A deep model is deployed only if it beats the best tree model on the **validation** set on the primary metric (macro-F1 for multi-class, PR-AUC for binary) **and** stays within the latency budget. Otherwise the comparison is documented and the tree model stays.
- No sequence or packet-level deep models (CNN/LSTM on raw bytes). They need different data, much more compute, and a different parity story.

## Consequences

- Less time on model tuning, more on data quality, leakage checks and honest evaluation, which is where the credibility comes from.
- SHAP TreeExplainer gives fast, exact explanations for the deployed tree models. A deep model would need slower approximate explainers.

## References

- Grinsztajn, Oyallon, Varoquaux. Why do tree-based models still outperform deep learning on typical tabular data? NeurIPS 2022 Datasets and Benchmarks. [VERIFY] exact title and link before quoting in the README.
