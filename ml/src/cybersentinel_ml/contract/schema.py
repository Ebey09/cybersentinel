"""Feature schema: the single source of truth shared by training and inference.

A schema YAML describes, for ONE dataset track:
  * the exact raw CSV header the extractor produces (names and order)
  * which raw columns are model inputs, identifiers, labels, or excluded (and why)
  * per-feature documentation: dtype, unit, meaning, range, missing-value handling,
    scaling, encoding, and whether the feature can be produced from PCAP
  * the extractor (name, commit, timeouts) that the training data came from
  * the preprocessing version
  * the output vocabulary the track is allowed to use

Loading fails loudly if the file is internally inconsistent. See docs/ML_DATA_CONTRACT.md.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_SCHEMA_BYTES = 1_000_000  # a schema file is small; refuse anything absurd
SEMVER = r"^\d+\.\d+\.\d+$"
SNAKE = r"^[a-z][a-z0-9_]*$"


class SchemaStatus(StrEnum):
    DRAFT = "draft"
    VERIFIED = "verified"


class ParityStatus(StrEnum):
    NOT_DEMONSTRATED = "not_demonstrated"
    DEMONSTRATED = "demonstrated"
    FAILED = "failed"


class _Strict(BaseModel):
    """Unknown keys are errors, so a typo in YAML cannot be silently ignored."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Range(_Strict):
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def _ordered(self) -> Range:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"expected_range min {self.min} > max {self.max}")
        return self


class Scaling(_Strict):
    logistic_regression: str
    tree_models: str


class FeatureSpec(_Strict):
    name: str = Field(pattern=SNAKE)
    source_column: str
    dtype: Literal["float64", "int64"]
    unit: str | None
    group: str
    meaning: str = Field(min_length=10)
    expected_range: Range
    missing_values: str
    scaling: Scaling
    encoding: Literal["numeric", "one_hot_fixed_categories", "numeric_trees_only"]
    categories: list[int] | None = None
    unknown_category: str | None = None
    included: bool
    status: Literal["draft", "verified"]
    notes: str | None
    pcap_available: Literal["pinned_extractor_only", "unverified", "no"]
    source: str

    @model_validator(mode="after")
    def _encoding_needs_categories(self) -> FeatureSpec:
        if self.encoding == "one_hot_fixed_categories" and not self.categories:
            raise ValueError(f"feature {self.name}: one-hot encoding requires 'categories'")
        return self


class IdentifierSpec(_Strict):
    name: str = Field(pattern=SNAKE)
    source_column: str
    dtype: Literal["string", "int64"]
    used_for: list[str]
    model_input: Literal[False]
    reason: str = Field(min_length=10)


class LabelColumnSpec(_Strict):
    source_column: str
    name: str = Field(pattern=SNAKE)
    notes: str | None = None
    known_values_source: str | None = None


class ExtractorSpec(_Strict):
    name: str
    repository: str
    commit: str
    # pinned: the exact commit is known. to_verify: not checked yet. not_documented: checked, and the
    # dataset authors do not document it. Only 'pinned' allows parity or inference (ADR 0010).
    commit_status: Literal["pinned", "to_verify", "not_documented"]
    flow_timeout_us: int | None
    activity_timeout_us: int | None
    pcap_preprocessing: list[str]
    known_header_columns: int
    notes: str | None = None

    @model_validator(mode="after")
    def _pinned_needs_real_commit(self) -> ExtractorSpec:
        if self.commit_status == "pinned" and ("[VERIFY]" in self.commit or len(self.commit.strip()) < 7):
            raise ValueError("extractor commit_status 'pinned' needs a real commit, not a placeholder")
        return self

    @property
    def is_pinned(self) -> bool:
        return self.commit_status == "pinned"


class ParitySpec(_Strict):
    status: ParityStatus
    evidence: str | None
    required_for: list[str]
    test: str
    notes: str | None = None


class PositionalRename(_Strict):
    """A raw column whose name is ambiguous (for example a header that repeats 'Label').

    raw_columns holds the resolved name. The raw file must have raw_name at this position.
    The dataset adapter renames it explicitly, and only after the raw header check passed (ADR 0011).
    """

    position: int = Field(ge=0)
    raw_name: str
    resolved_name: str
    reason: str = Field(min_length=10)


class DerivedFeature(_Strict):
    name: str = Field(pattern=SNAKE)
    dtype: Literal["float64"]
    definition: str
    reason: str
    pcap_available: str


class PreprocessingSpec(_Strict):
    version: str = Field(pattern=SEMVER)
    inf_handling: str
    out_of_range_handling: str
    missing_handling: str
    derived_features: list[DerivedFeature]
    duplicate_handling: str
    constant_feature_handling: str
    scaling: Scaling
    categorical_encoding: str
    dtype_policy: str
    feature_order: str


class OutputVocabulary(_Strict):
    allowed_terms: list[str]
    forbidden_terms: list[str] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def _no_overlap(self) -> OutputVocabulary:
        allowed = " | ".join(self.allowed_terms).lower()
        clash = [t for t in self.forbidden_terms if t.lower() in allowed]
        if clash:
            raise ValueError(f"allowed_terms contain forbidden terms: {clash}")
        return self


class DatasetInfo(_Strict):
    name: str
    homepage: str
    release: str
    correction: str | None = None


class FeatureSchema(_Strict):
    schema_id: str
    schema_version: str = Field(pattern=SEMVER)
    status: SchemaStatus
    track: Literal["A", "B"]
    title: str
    dataset: DatasetInfo
    extractor: ExtractorSpec
    parity: ParitySpec
    raw_columns: list[str] = Field(min_length=1)
    positional_renames: list[PositionalRename] = Field(default_factory=list)
    identifier_columns: list[IdentifierSpec]
    label_columns: list[LabelColumnSpec] = Field(min_length=1)
    features: list[FeatureSpec] = Field(min_length=1)
    excluded_features: list[FeatureSpec]
    preprocessing: PreprocessingSpec
    output_vocabulary: OutputVocabulary

    @model_validator(mode="after")
    def _consistent(self) -> FeatureSchema:
        errors: list[str] = []

        dupes = sorted({c for c in self.raw_columns if self.raw_columns.count(c) > 1})
        if dupes:
            errors.append(f"raw_columns has duplicates: {dupes}")

        positions = [r.position for r in self.positional_renames]
        if len(set(positions)) != len(positions):
            errors.append("positional_renames has duplicate positions")
        for r in self.positional_renames:
            if r.position >= len(self.raw_columns):
                errors.append(f"positional rename at {r.position} is past the end of raw_columns")
            elif self.raw_columns[r.position] != r.resolved_name:
                errors.append(f"raw_columns[{r.position}] must be the resolved name {r.resolved_name!r}")
            if r.raw_name == r.resolved_name:
                errors.append(f"positional rename at {r.position} does not change the name")

        # Every raw column must be accounted for exactly once.
        roles: dict[str, list[str]] = {}
        for f in self.features:
            roles.setdefault(f.source_column, []).append("feature")
        for f in self.excluded_features:
            roles.setdefault(f.source_column, []).append("excluded")
        for i in self.identifier_columns:
            roles.setdefault(i.source_column, []).append("identifier")
        for lab in self.label_columns:
            roles.setdefault(lab.source_column, []).append("label")

        raw = set(self.raw_columns)
        unknown = sorted(set(roles) - raw)
        if unknown:
            errors.append(f"columns referenced but not in raw_columns: {unknown}")
        unassigned = sorted(raw - set(roles))
        if unassigned:
            errors.append(f"raw columns with no role (feature/excluded/identifier/label): {unassigned}")
        multi = sorted(c for c, r in roles.items() if len(r) > 1)
        if multi:
            errors.append(f"columns with more than one role: {multi}")

        if any(not f.included for f in self.features):
            errors.append("every entry in 'features' must have included: true")
        if any(f.included for f in self.excluded_features):
            errors.append("every entry in 'excluded_features' must have included: false")

        names = (
            [f.name for f in self.features]
            + [f.name for f in self.excluded_features]
            + [i.name for i in self.identifier_columns]
            + [lab.name for lab in self.label_columns]
            + [d.name for d in self.preprocessing.derived_features]
        )
        dup_names = sorted({n for n in names if names.count(n) > 1})
        if dup_names:
            errors.append(f"duplicate canonical names: {dup_names}")

        if self.status == SchemaStatus.VERIFIED:
            if any(f.status != "verified" for f in self.features):
                errors.append("a verified schema cannot contain draft features")
            if self.extractor.commit_status == "to_verify":
                errors.append(
                    "a verified schema needs a pinned extractor commit, or one confirmed as not documented"
                )
        if self.extractor.commit_status == "not_documented":
            # Without the exact extractor, PCAP parity cannot be shown (ADR 0006, ADR 0010).
            if self.parity.status == ParityStatus.DEMONSTRATED:
                errors.append("parity cannot be demonstrated when the extractor commit is not documented")
            if any(f.pcap_available == "pinned_extractor_only" for f in self.features):
                errors.append(
                    "features cannot be 'pinned_extractor_only' when the extractor is not documented"
                )

        if errors:
            raise ValueError("; ".join(errors))
        return self

    # ---- convenience -------------------------------------------------

    def expected_raw_header(self) -> list[str]:
        """The header exactly as the raw file must have it, before any declared rename."""
        header = list(self.raw_columns)
        for r in self.positional_renames:
            header[r.position] = r.raw_name
        return header

    def input_feature_names(self) -> list[str]:
        """Model input features in schema order, BEFORE fitted preprocessing
        (constant-column dropping) and derived features."""
        return [f.name for f in self.features]

    def candidate_model_order(self) -> list[str]:
        """Schema features followed by derived features, i.e. the order the
        preprocessing step starts from."""
        return self.input_feature_names() + [d.name for d in self.preprocessing.derived_features]

    def source_to_name(self) -> dict[str, str]:
        """Raw CSV column -> canonical name, for every column with a role."""
        mapping = {f.source_column: f.name for f in self.features + self.excluded_features}
        mapping.update({i.source_column: i.name for i in self.identifier_columns})
        mapping.update({lab.source_column: lab.name for lab in self.label_columns})
        return mapping

    def sha256(self) -> str:
        """Hash of the parsed content (comments and formatting do not matter)."""
        canonical = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_schema(path: str | Path) -> FeatureSchema:
    """Load and validate a schema YAML. Uses yaml.safe_load only."""
    p = Path(path)
    size = p.stat().st_size
    if size > MAX_SCHEMA_BYTES:
        raise ValueError(f"schema file too large ({size} bytes): {p}")
    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"schema file must contain a mapping: {p}")
    return FeatureSchema.model_validate(data)


def sha256_of_sequence(items: list[str]) -> str:
    """Stable hash of an ordered list of names (used for feature order)."""
    return hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()
