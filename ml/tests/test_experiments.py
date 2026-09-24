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


# The 27 distinct Label values observed in the five CNS2022 Improved CIC-IDS2017 CSVs (V5), exact spelling.
OBSERVED_TRACK_A_LABELS = [
    "BENIGN",
    "FTP-Patator",
    "FTP-Patator - Attempted",
    "SSH-Patator",
    "SSH-Patator - Attempted",
    "DoS Hulk",
    "DoS Hulk - Attempted",
    "DoS GoldenEye",
    "DoS GoldenEye - Attempted",
    "DoS Slowloris",
    "DoS Slowloris - Attempted",
    "DoS Slowhttptest",
    "DoS Slowhttptest - Attempted",
    "Heartbleed",
    "Web Attack - Brute Force",
    "Web Attack - Brute Force - Attempted",
    "Web Attack - XSS",
    "Web Attack - XSS - Attempted",
    "Web Attack - SQL Injection",
    "Web Attack - SQL Injection - Attempted",
    "Infiltration",
    "Infiltration - Attempted",
    "Infiltration - Portscan",
    "Portscan",
    "DDoS",
    "Botnet",
    "Botnet - Attempted",
]
TRACK_A_EXPERIMENTS = ["track_a_binary", "track_a_multiclass_family"]


def _track_a(name: str, repo_root: Path) -> ExperimentConfig:
    exp, _, _ = load_experiment(repo_root / f"ml/config/experiments/{name}.yaml", repo_root)
    return exp


def test_observed_track_a_labels_are_distinct() -> None:
    assert len(OBSERVED_TRACK_A_LABELS) == len(set(OBSERVED_TRACK_A_LABELS)) == 27


@pytest.mark.parametrize("name", TRACK_A_EXPERIMENTS)
def test_every_observed_track_a_label_has_an_exact_mapping(name: str, repo_root: Path) -> None:
    exp = _track_a(name, repo_root)
    missing = [label for label in OBSERVED_TRACK_A_LABELS if label not in exp.label_map]
    assert not missing
    assert exp.unknown_label_policy == "fail"


def test_track_a_binary_and_family_have_identical_label_keys(repo_root: Path) -> None:
    # Both tasks must accept exactly the same raw labels. Key order is not compared: it only sets
    # each experiment's own class display order and has no meaning across experiments.
    binary = _track_a("track_a_binary", repo_root).label_map
    family = _track_a("track_a_multiclass_family", repo_root).label_map
    assert set(binary) == set(family)


@pytest.mark.parametrize("name", TRACK_A_EXPERIMENTS)
def test_track_a_attempted_flows_map_to_benign_and_never_form_a_class(name: str, repo_root: Path) -> None:
    exp = _track_a(name, repo_root)
    attempted = [label for label in OBSERVED_TRACK_A_LABELS if label.endswith(" - Attempted")]
    assert len(attempted) == 11
    assert {exp.label_map[label] for label in attempted} == {"BENIGN"}
    assert not any("ATTEMPT" in cls.upper() for cls in exp.classes())
    assert "Portscan - Attempted" not in exp.label_map  # CNS2022 has no Attempted variant for Portscan


def test_track_a_specific_mappings(repo_root: Path) -> None:
    binary = _track_a("track_a_binary", repo_root).label_map
    family = _track_a("track_a_multiclass_family", repo_root).label_map
    expected = {
        "Infiltration - Portscan": ("ATTACK", "PORTSCAN"),
        "Portscan": ("ATTACK", "PORTSCAN"),
        "Botnet": ("ATTACK", "BOTNET"),
        "Infiltration": ("ATTACK", "INFILTRATION"),
        "DDoS": ("ATTACK", "DDOS"),
        "BENIGN": ("BENIGN", "BENIGN"),
    }
    for label, (b, f) in expected.items():
        assert (binary[label], family[label]) == (b, f), label


def test_track_a_maps_have_no_obsolete_wtmc_spellings(repo_root: Path) -> None:
    obsolete = {"DoS slowloris", "Web Attack - Sql Injection", "Bot", "PortScan", "Heartbleed - Attempted"}
    for name in TRACK_A_EXPERIMENTS:
        assert not obsolete & set(_track_a(name, repo_root).label_map), name


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
