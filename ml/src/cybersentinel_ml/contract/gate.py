"""Inference gate: decides whether ML predictions may be produced for a batch.

Fail closed. If any contract check fails, the gate returns allowed=False with
human-readable reasons, and the caller must show those reasons instead of a
prediction. Traffic statistics and rule-based alerts do not depend on the model
and stay available either way.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict

from cybersentinel_ml.contract.manifest import InputProvenance, ModelManifest
from cybersentinel_ml.contract.schema import FeatureSchema, ParityStatus, SchemaStatus
from cybersentinel_ml.contract.validation import CheckResult, check_feature_frame

WITHHELD_FALLBACK = (
    "Traffic statistics and rule-based alerts are still available for this data. "
    "Only the ML prediction is withheld."
)


class InferenceDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    allowed: bool
    track: str
    checks: list[dict[str, object]]
    reasons: list[str]
    warnings: list[str]

    def explanation(self) -> str:
        if self.allowed:
            base = f"ML inference allowed for Track {self.track}."
            return base + ("" if not self.warnings else " Warnings: " + " ".join(self.warnings))
        return (
            f"ML prediction withheld for Track {self.track}. Reasons: "
            + " ".join(self.reasons)
            + " "
            + WITHHELD_FALLBACK
        )


def _extractor_matches(schema: FeatureSchema, prov: InputProvenance) -> CheckResult:
    ex = prov.extractor
    if ex is None:
        return CheckResult("extractor_known", False, "the extractor that produced these flows is unknown")
    want = schema.extractor
    diffs = []
    for field in ("name", "repository", "commit", "flow_timeout_us", "activity_timeout_us"):
        if getattr(ex, field) != getattr(want, field):
            diffs.append(
                f"extractor {field} is {getattr(ex, field)!r}, training data used {getattr(want, field)!r}"
            )
    return CheckResult(
        "extractor_matches_training",
        not diffs,
        "extractor matches the one used for the training data" if not diffs else "; ".join(diffs),
    )


def evaluate_inference_gate(
    schema: FeatureSchema,
    manifest: ModelManifest,
    provenance: InputProvenance,
    features: pd.DataFrame,
) -> InferenceDecision:
    checks: list[CheckResult] = []
    warnings: list[str] = []

    checks.append(
        CheckResult(
            "schema_verified",
            schema.status == SchemaStatus.VERIFIED,
            "feature schema is verified"
            if schema.status == SchemaStatus.VERIFIED
            else "the feature schema is still a draft and has not been verified against the real dataset",
        )
    )
    checks.append(
        CheckResult(
            "manifest_track",
            manifest.track == schema.track,
            f"model belongs to Track {manifest.track}, schema is Track {schema.track}",
        )
    )
    same_schema = (manifest.schema_id, manifest.schema_version, manifest.schema_sha256) == (
        schema.schema_id,
        schema.schema_version,
        schema.sha256(),
    )
    checks.append(
        CheckResult(
            "manifest_schema_match",
            same_schema,
            "model was trained with this exact schema"
            if same_schema
            else "the model was trained with a different schema id, version or content",
        )
    )
    same_prep = manifest.preprocessing.preprocessing_version == schema.preprocessing.version
    checks.append(
        CheckResult(
            "preprocessing_version_match",
            same_prep,
            "preprocessing version matches"
            if same_prep
            else f"model expects preprocessing {manifest.preprocessing.preprocessing_version}, "
            f"schema defines {schema.preprocessing.version}",
        )
    )

    checks.append(_extractor_matches(schema, provenance))
    checks.append(
        CheckResult(
            "extractor_pinned",
            schema.extractor.is_pinned,
            "extractor commit is pinned"
            if schema.extractor.is_pinned
            else "the training extractor commit is not pinned, so parity cannot be checked",
        )
    )

    if provenance.source_type == "pcap":
        checks.append(
            CheckResult(
                "pcap_parity_demonstrated",
                schema.parity.status == ParityStatus.DEMONSTRATED,
                "PCAP-to-feature parity has been demonstrated"
                if schema.parity.status == ParityStatus.DEMONSTRATED
                else f"PCAP-to-feature parity is '{schema.parity.status.value}' for this track, "
                "so features extracted from PCAP cannot be trusted to match the training data",
            )
        )
        checks.append(
            CheckResult(
                "pcap_provenance_verified",
                provenance.provenance_verified,
                "flows were produced by the platform's pinned extractor"
                if provenance.provenance_verified
                else "flows were not produced by the platform's pinned extractor",
            )
        )
    elif not provenance.provenance_verified:
        warnings.append(
            "Extractor provenance for this CSV was asserted by the uploader, not verified by the platform."
        )

    checks.extend(check_feature_frame(features, manifest.preprocessing.feature_order))

    failed = [c for c in checks if not c.passed]
    return InferenceDecision(
        allowed=not failed,
        track=schema.track,
        checks=[{"name": c.name, "passed": c.passed, "detail": c.detail} for c in checks],
        reasons=[f"{c.detail[0].upper()}{c.detail[1:]}." for c in failed],
        warnings=warnings,
    )
