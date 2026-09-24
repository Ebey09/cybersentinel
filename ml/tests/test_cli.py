"""CLI smoke tests on synthetic CSV files."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from cybersentinel_ml.cli import main
from cybersentinel_ml.contract.schema import FeatureSchema


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def test_validate_config_passes_on_repo(repo_root: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["validate-config", "--root", str(repo_root)]) == 0
    out = capsys.readouterr().out
    assert "track_a.cicids2017_corrected" in out and "[FAIL]" not in out


def test_check_header_ok_and_fail(schema_a: FeatureSchema, tmp_path: Path, repo_root: Path) -> None:
    schema_path = str(repo_root / "ml/config/schemas/track_a_cicids2017.yaml")
    good = tmp_path / "good.csv"
    _write_csv(good, schema_a.raw_columns, [])
    assert main(["check-header", "--schema", schema_path, "--csv", str(good)]) == 0

    bad = tmp_path / "bad.csv"
    _write_csv(bad, schema_a.raw_columns[:-3], [])
    assert main(["check-header", "--schema", schema_path, "--csv", str(bad)]) == 1


def test_check_header_accepts_declared_duplicate_without_renaming(
    schema_b: FeatureSchema, tmp_path: Path, repo_root: Path, capsys
) -> None:  # type: ignore[no-untyped-def]
    schema_path = str(repo_root / "ml/config/schemas/track_b_darknet2020.yaml")
    raw = tmp_path / "raw.csv"
    _write_csv(raw, schema_b.expected_raw_header(), [])  # 'Label' twice, as declared
    assert main(["check-header", "--schema", schema_path, "--csv", str(raw)]) == 0
    assert "declared rename (applied by the adapter, not here)" in capsys.readouterr().out


def test_inspect_labels_reports_unmapped(tmp_path: Path, repo_root: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    f = tmp_path / "labels.csv"
    _write_csv(f, ["x", "Label"], [["1", "Tor"], ["2", "VPN"], ["3", "NonVPN"], ["4", "Tor"]])
    exp = str(repo_root / "ml/config/experiments/track_b_traffic_type.yaml")
    code = main(["inspect-labels", "--csv", str(f), "--column", "Label", "--experiment", exp])
    out = capsys.readouterr().out
    assert code == 1
    assert "'NonVPN'" in out  # a spelling not in the label map is surfaced, not guessed


def test_inspect_labels_refuses_ambiguous_duplicate_column(tmp_path: Path) -> None:
    f = tmp_path / "dup.csv"
    _write_csv(f, ["Label", "Label"], [["Tor", "Chat"]])
    assert main(["inspect-labels", "--csv", str(f), "--column", "Label"]) == 1
    assert main(["inspect-labels", "--csv", str(f), "--column-index", "1"]) == 0


@pytest.mark.parametrize("index", ["-1", "2", "99"])
def test_inspect_labels_rejects_out_of_range_column_index(tmp_path: Path, capsys, index: str) -> None:  # type: ignore[no-untyped-def]
    f = tmp_path / "labels.csv"
    _write_csv(f, ["x", "Label"], [["1", "Tor"]])
    assert main(["inspect-labels", "--csv", str(f), "--column-index", index]) == 1
    assert "out of range" in capsys.readouterr().out


def test_schema_docs_renders(repo_root: Path, tmp_path: Path) -> None:
    out = tmp_path / "a.md"
    schema_path = str(repo_root / "ml/config/schemas/track_a_cicids2017.yaml")
    assert main(["schema-docs", "--schema", schema_path, "--out", str(out)]) == 0
    text = out.read_text()
    assert "flow_duration" in text and "Excluded features" in text
