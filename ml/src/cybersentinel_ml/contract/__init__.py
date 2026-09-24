"""The ML data contract: feature schemas, manifests, validation and the inference gate."""

from cybersentinel_ml.contract.gate import InferenceDecision, evaluate_inference_gate
from cybersentinel_ml.contract.manifest import (
    ExtractorProvenance,
    InputProvenance,
    ModelManifest,
    PreprocessingManifest,
)
from cybersentinel_ml.contract.schema import FeatureSchema, load_schema, sha256_of_sequence
from cybersentinel_ml.contract.validation import CheckResult, check_feature_frame, check_raw_header

__all__ = [
    "CheckResult",
    "ExtractorProvenance",
    "FeatureSchema",
    "InferenceDecision",
    "InputProvenance",
    "ModelManifest",
    "PreprocessingManifest",
    "check_feature_frame",
    "check_raw_header",
    "evaluate_inference_gate",
    "load_schema",
    "sha256_of_sequence",
]
