"""Experiment configs: label maps, display vocabulary, splits."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cybersentinel_ml.contract.experiment import ExperimentConfig, load_experiment

EXPERIMENTS = sorted((Path(__file__).resolve().parents[1] / "config" / "experiments").glob("*.yaml"))


@pytest.mark.parametrize("path", EXPERIMENTS, ids=lambda p: p.name)
def test_experiment_loads_against_its_schema(path: Path, repo_root: Path) -> None:
    exp, schema, digest = load_experiment(path, repo_root)
    assert exp.track == schema.track
    assert len(digest) == 64
    assert exp.seed == 42


def test_track_a_attempted_flows_map_to_benign(repo_root: Path) -> None:
    exp, _, _ = load_experiment(repo_root / "ml/config/experiments/track_a_binary.yaml", repo_root)
    attempted = {k: v for k, v in exp.label_map.items() if k.endswith(" - Attempted")}
    assert attempted, "expected '- Attempted' labels in the Track A map"
    assert set(attempted.values()) == {"BENIGN"}
    assert "PortScan - Attempted" not in exp.label_map  # PortScan has no Attempted variant


def test_track_b_never_uses_harm_vocabulary(repo_root: Path) -> None:
    for path in EXPERIMENTS:
        exp, _schema, _ = load_experiment(path, repo_root)
        if exp.track != "B":
            continue
        for cls, text in exp.class_display.items():
            for term in ["malicious", "attack", "threat", "malware", "benign"]:
                assert term not in text.lower() and term not in cls.lower()


def test_track_b_primary_task_merges_regular_captures(repo_root: Path) -> None:
    exp, _, _ = load_experiment(repo_root / "ml/config/experiments/track_b_traffic_type.yaml", repo_root)
    assert exp.label_map["Non-Tor"] == exp.label_map["Non-VPN"] == "REGULAR"


def test_forbidden_display_text_is_rejected(repo_root: Path, tmp_path: Path) -> None:
    src = repo_root / "ml/config/experiments/track_b_traffic_type.yaml"
    data = yaml.safe_load(src.read_text())
    data["class_display"]["TOR"] = "Malicious Tor traffic"
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="forbidden term"):
        load_experiment(bad, repo_root)


def test_split_must_sum_to_one(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "ml/config/experiments/track_a_binary.yaml").read_text())
    data["split"]["test"] = 0.5
    with pytest.raises(ValueError, match=r"sum to 1\.0"):
        ExperimentConfig.model_validate(data)


def test_class_without_display_text_is_rejected(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "ml/config/experiments/track_a_binary.yaml").read_text())
    data["label_map"]["Bot"] = "NEW_CLASS"
    with pytest.raises(ValueError, match="without display text"):
        ExperimentConfig.model_validate(data)
