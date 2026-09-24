"""Manifest self-consistency."""

from __future__ import annotations

import pytest

from cybersentinel_ml.contract.manifest import PreprocessingManifest
from cybersentinel_ml.contract.schema import FeatureSchema, sha256_of_sequence

from .conftest import make_manifest


def test_feature_order_hash_must_match(schema_a: FeatureSchema) -> None:
    order = schema_a.candidate_model_order()
    with pytest.raises(ValueError, match="feature_order_sha256"):
        PreprocessingManifest(
            preprocessing_version="0.1.0",
            schema_id=schema_a.schema_id,
            schema_version=schema_a.schema_version,
            schema_sha256=schema_a.sha256(),
            feature_order=order,
            feature_order_sha256=sha256_of_sequence(list(reversed(order))),
        )


def test_feature_cannot_be_kept_and_dropped(schema_a: FeatureSchema) -> None:
    order = schema_a.candidate_model_order()
    with pytest.raises(ValueError, match="both kept and dropped"):
        PreprocessingManifest(
            preprocessing_version="0.1.0",
            schema_id=schema_a.schema_id,
            schema_version=schema_a.schema_version,
            schema_sha256=schema_a.sha256(),
            feature_order=order,
            feature_order_sha256=sha256_of_sequence(order),
            dropped_constant_features=[order[0]],
        )


def test_model_and_preprocessing_must_reference_same_schema(schema_a: FeatureSchema) -> None:
    with pytest.raises(ValueError, match="different schemas"):
        make_manifest(schema_a, schema_version="0.9.0")
