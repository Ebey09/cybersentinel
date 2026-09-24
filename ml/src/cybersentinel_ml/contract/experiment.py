"""Experiment configuration: task, label mapping, split, seed, models.

The label map is part of the contract because it decides what a model is
allowed to claim. Every raw label must map to a class explicitly, and every
class must have display text that respects the track's output vocabulary.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from cybersentinel_ml.contract.schema import FeatureSchema, load_schema


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SplitSpec(_Strict):
    method: Literal["stratified_random"]
    train: float = Field(gt=0, lt=1)
    validation: float = Field(gt=0, lt=1)
    test: float = Field(gt=0, lt=1)
    dedup_before_split: bool

    @model_validator(mode="after")
    def _sums_to_one(self) -> SplitSpec:
        total = self.train + self.validation + self.test
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"split fractions must sum to 1.0, got {total}")
        return self


class ModelSpec(_Strict):
    algorithm: Literal["logistic_regression", "random_forest", "xgboost", "mlp"]
    params: dict[str, object] = Field(default_factory=dict)


class CalibrationSpec(_Strict):
    method: Literal["none", "isotonic", "sigmoid"]
    fit_on: Literal["validation"]


class ThresholdSpec(_Strict):
    policy: Literal["argmax", "target_fpr"]
    target_fpr: float | None = Field(default=None, gt=0, lt=1)
    fit_on: Literal["validation"]


class ExperimentConfig(_Strict):
    experiment_id: str = Field(pattern=r"^[a-z0-9_]+$")
    track: Literal["A", "B"]
    schema_path: str
    task: str = Field(pattern=r"^[a-z0-9_]+$")
    seed: int
    label_column: str
    label_map: dict[str, str] = Field(min_length=2)
    class_display: dict[str, str]
    unknown_label_policy: Literal["fail"]
    min_class_count: int | None = Field(default=None, ge=1)
    include_dst_port: bool
    split: SplitSpec
    models: list[ModelSpec] = Field(min_length=1)
    calibration: CalibrationSpec
    threshold: ThresholdSpec
    ablations: list[Literal["no_dst_port", "shuffled_labels", "single_feature_auc"]]
    notes: str | None = None

    @model_validator(mode="after")
    def _labels_complete(self) -> ExperimentConfig:
        classes = set(self.label_map.values())
        missing = sorted(classes - set(self.class_display))
        extra = sorted(set(self.class_display) - classes)
        if missing:
            raise ValueError(f"classes without display text: {missing}")
        if extra:
            raise ValueError(f"display text for classes that no label maps to: {extra}")
        if len(classes) < 2:
            raise ValueError("a task needs at least two classes")
        if self.threshold.policy == "target_fpr" and self.threshold.target_fpr is None:
            raise ValueError("threshold policy target_fpr needs target_fpr")
        return self

    def classes(self) -> list[str]:
        """Class names in a stable order (first appearance in label_map)."""
        return list(dict.fromkeys(self.label_map.values()))


def load_experiment(path: str | Path, repo_root: str | Path) -> tuple[ExperimentConfig, FeatureSchema, str]:
    """Load an experiment, its schema, and the SHA-256 of the experiment file.

    Cross-checks the experiment against the schema:
      * same track
      * label_column is a declared label column
      * display text uses no forbidden vocabulary for the track
    """
    p = Path(path)
    raw = p.read_bytes()
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"experiment file must contain a mapping: {p}")
    exp = ExperimentConfig.model_validate(data)
    schema = load_schema(Path(repo_root) / exp.schema_path)

    problems: list[str] = []
    if exp.track != schema.track:
        problems.append(f"experiment track {exp.track} != schema track {schema.track}")
    label_sources = {lab.source_column for lab in schema.label_columns}
    if exp.label_column not in label_sources:
        problems.append(f"label_column {exp.label_column!r} is not a label column in the schema")
    for cls, text in exp.class_display.items():
        for term in schema.output_vocabulary.forbidden_terms:
            if term.lower() in text.lower() or term.lower() in cls.lower():
                problems.append(f"class {cls!r} / display {text!r} uses forbidden term {term!r}")
    if problems:
        raise ValueError("; ".join(problems))
    return exp, schema, hashlib.sha256(raw).hexdigest()
