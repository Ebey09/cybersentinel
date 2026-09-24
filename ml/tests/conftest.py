"""Shared fixtures. Everything here is synthetic: no real dataset rows are used in tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cybersentinel_ml.contract.manifest import (
    ExtractorProvenance,
    InputProvenance,
    ModelManifest,
    PreprocessingManifest,
)
from cybersentinel_ml.contract.schema import FeatureSchema, load_schema, sha256_of_sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_A = REPO_ROOT / "ml" / "config" / "schemas" / "track_a_cicids2017.yaml"
SCHEMA_B = REPO_ROOT / "ml" / "config" / "schemas" / "track_b_darknet2020.yaml"
PINNED_COMMIT = "0123456789abcdef0123456789abcdef01234567"  # synthetic, tests only


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def schema_a() -> FeatureSchema:
    return load_schema(SCHEMA_A)


@pytest.fixture
def schema_b() -> FeatureSchema:
    return load_schema(SCHEMA_B)


def make_verified(schema: FeatureSchema, parity: str = "demonstrated") -> FeatureSchema:
    """Build a 'verified' copy through full validation (validators re-run)."""
    data = schema.model_dump(mode="json")
    data["status"] = "verified"
    data["extractor"]["commit"] = PINNED_COMMIT
    data["extractor"]["commit_status"] = "pinned"
    data["parity"]["status"] = parity
    for f in data["features"]:
        f["status"] = "verified"
    return FeatureSchema.model_validate(data)


@pytest.fixture
def verified_a(schema_a: FeatureSchema) -> FeatureSchema:
    return make_verified(schema_a)


def make_manifest(schema: FeatureSchema, **overrides: object) -> ModelManifest:
    order = schema.candidate_model_order()
    prep = PreprocessingManifest(
        preprocessing_version=schema.preprocessing.version,
        schema_id=schema.schema_id,
        schema_version=schema.schema_version,
        schema_sha256=schema.sha256(),
        feature_order=order,
        feature_order_sha256=sha256_of_sequence(order),
    )
    fields: dict[str, object] = {
        "model_id": "test-model",
        "model_version": "0.1.0",
        "track": schema.track,
        "task": "binary",
        "algorithm": "xgboost",
        "schema_id": schema.schema_id,
        "schema_version": schema.schema_version,
        "schema_sha256": schema.sha256(),
        "experiment_config_sha256": "0" * 64,
        "preprocessing": prep,
        "dataset_sha256": {"synthetic.csv": "0" * 64},
        "classes": ["BENIGN", "ATTACK"],
        "seed": 42,
        "git_commit": None,
        "library_versions": {},
        "artifact_sha256": "0" * 64,
    }
    fields.update(overrides)
    return ModelManifest(**fields)


def make_frame(order: list[str], rows: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame(rng.random((rows, len(order))), columns=order)


def provenance_for(
    schema: FeatureSchema, source_type: str = "pcap", verified: bool = True, **extractor_overrides: object
) -> InputProvenance:
    ex = {
        "name": schema.extractor.name,
        "repository": schema.extractor.repository,
        "commit": schema.extractor.commit,
        "flow_timeout_us": schema.extractor.flow_timeout_us,
        "activity_timeout_us": schema.extractor.activity_timeout_us,
    }
    ex.update(extractor_overrides)
    return InputProvenance(
        source_type=source_type,  # type: ignore[arg-type]
        extractor=ExtractorProvenance(**ex),  # type: ignore[arg-type]
        provenance_verified=verified,
    )
