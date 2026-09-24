# Models

Model binaries are **not** committed. Trained artifacts are published as GitHub Release assets, each with:

- `model_manifest.json` (schema id/version/SHA-256, preprocessing manifest, dataset SHA-256s, seed, git commit, library versions, artifact SHA-256)
- `preprocessing_manifest.json` (final feature order and hash, dropped constant features, fitted parameters)
- a model card (intended use, data, metrics, limitations)

The application loads a model only after its SHA-256 matches the manifest, and only if the inference gate passes (ADR 0007).

No models exist yet (Phase 5).
