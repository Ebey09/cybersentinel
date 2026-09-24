"""Provenance and artifact manifests.

These are data contracts only. Phase 5 (training) writes ModelManifest and
PreprocessingManifest next to every model artifact. The inference gate reads them.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cybersentinel_ml.contract.schema import SEMVER, sha256_of_sequence


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ExtractorProvenance(_Strict):
    """Which extractor produced a batch of flows, and with what settings."""

    name: str
    repository: str
    commit: str
    flow_timeout_us: int | None
    activity_timeout_us: int | None
    image_digest: str | None = None


class InputProvenance(_Strict):
    """Attached to every batch of flows that reaches inference.

    provenance_verified is True only when the flows were produced by the
    platform's own pinned extractor container (the worker sets it). A CSV
    uploaded by a user can only ever carry *asserted* provenance.
    """

    source_type: Literal["pcap", "csv"]
    extractor: ExtractorProvenance | None
    provenance_verified: bool


class PreprocessingManifest(_Strict):
    preprocessing_version: str = Field(pattern=SEMVER)
    schema_id: str
    schema_version: str = Field(pattern=SEMVER)
    schema_sha256: str = Field(min_length=64, max_length=64)
    feature_order: list[str] = Field(min_length=1)
    feature_order_sha256: str = Field(min_length=64, max_length=64)
    dropped_constant_features: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _order_hash_matches(self) -> PreprocessingManifest:
        if sha256_of_sequence(self.feature_order) != self.feature_order_sha256:
            raise ValueError("feature_order_sha256 does not match feature_order")
        overlap = set(self.feature_order) & set(self.dropped_constant_features)
        if overlap:
            raise ValueError(f"features both kept and dropped: {sorted(overlap)}")
        return self


class ModelManifest(_Strict):
    model_id: str
    model_version: str = Field(pattern=SEMVER)
    track: Literal["A", "B"]
    task: str
    algorithm: Literal["logistic_regression", "random_forest", "xgboost", "mlp"]
    schema_id: str
    schema_version: str = Field(pattern=SEMVER)
    schema_sha256: str = Field(min_length=64, max_length=64)
    experiment_config_sha256: str = Field(min_length=64, max_length=64)
    preprocessing: PreprocessingManifest
    dataset_sha256: dict[str, str]
    classes: list[str] = Field(min_length=2)
    seed: int
    git_commit: str | None
    library_versions: dict[str, str]
    artifact_sha256: str = Field(min_length=64, max_length=64)

    @model_validator(mode="after")
    def _schema_refs_agree(self) -> ModelManifest:
        p = self.preprocessing
        if (p.schema_id, p.schema_version, p.schema_sha256) != (
            self.schema_id,
            self.schema_version,
            self.schema_sha256,
        ):
            raise ValueError("model and preprocessing manifests reference different schemas")
        return self
