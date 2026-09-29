"""Raw-data diagnostics on a synthetic CSV with the Track B raw header (no real dataset rows)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from cybersentinel_ml.cli import main
from cybersentinel_ml.contract.schema import FeatureSchema
from cybersentinel_ml.data_quality import analyze_csv, render_text


def _row(schema: FeatureSchema, values: dict[str, str] | None = None) -> list[str]:
    """One raw row in resolved-column order, with exact column names as keys."""
    base = dict.fromkeys(schema.raw_columns, "0")
    base.update({"Flow ID": "a-b-1-2-6", "Src IP": "10.0.0.1", "Dst IP": "10.0.0.2", "Timestamp": "t0"})
    base.update({"Label": "Tor", "Label (column 84)": "Chat", "Protocol": "6"})
    for name, v in (values or {}).items():
        assert name in base, name
        base[name] = v
    return [base[c] for c in schema.raw_columns]


def _write(path: Path, schema: FeatureSchema, rows: list[list[str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(schema.expected_raw_header())  # raw header: 'Label' twice
        w.writerows(rows)
    return path


@pytest.fixture
def report(schema_b: FeatureSchema, tmp_path: Path) -> dict:  # type: ignore[type-arg]
    r1 = _row(schema_b, {"Flow Bytes/s": "", "Flow Packets/s": "Infinity"})
    r3 = _row(
        schema_b,
        {
            "Src Port": "999",
            "Flow Bytes/s": "-Infinity",
            "FWD Init Win Bytes": "-1",
            "Down/Up Ratio": "0.5",
            "Active Mean": "1500000000000000",
            "Fwd PSH Flags": "1",
            "FIN Flag Count": "3",
            "Protocol": "17",
            "Label": "NonVPN",
            "Label (column 84)": "AUDIO-STREAMING",
        },
    )
    r4 = _row(
        schema_b, {"Flow ID": "other", "Down/Up Ratio": "2", "Bwd Init Win Bytes": "-1", "Label": "Non-Tor"}
    )
    csv_path = _write(tmp_path / "synthetic.csv", schema_b, [r1, list(r1), r3, r4])
    return analyze_csv(csv_path, schema_b)


def test_shape_and_duplicate_header(report: dict) -> None:  # type: ignore[type-arg]
    assert report["shape"]["rows"] == 4
    assert report["shape"]["raw_columns"] == 85
    assert report["shape"]["declared_duplicate_headers"] == [
        {"position": 84, "raw_name": "Label", "resolved_name": "Label (column 84)"}
    ]


def test_labels_keep_exact_spelling(report: dict) -> None:  # type: ignore[type-arg]
    traffic = report["labels"]["Label"]
    assert traffic["Tor"] == {"count": 2, "pct": 50.0}
    assert set(traffic) == {"Tor", "NonVPN", "Non-Tor"}
    assert set(report["labels"]["Label (column 84)"]) == {"Chat", "AUDIO-STREAMING"}


def test_missing_and_non_finite(report: dict) -> None:  # type: ignore[type-arg]
    assert report["missing"] == {"rows_with_any_missing": 2, "per_column": {"Flow Bytes/s": 2}}
    nf = report["non_finite"]
    assert nf["rows_with_any_infinity"] == 3
    assert nf["positive_infinity"] == {"Flow Packets/s": 2}
    assert nf["negative_infinity"] == {"Flow Bytes/s": 1}


def test_duplicates_and_flow_ids_are_counted_not_removed(report: dict) -> None:  # type: ignore[type-arg]
    assert report["exact_duplicate_rows"] == {
        "extra_copies": 1,
        "rows_in_duplicate_groups": 2,
        "duplicate_groups": 1,
    }
    assert report["flow_id"] == {
        "rows": 4,
        "unique": 2,
        "ids_occurring_more_than_once": 1,
        "rows_with_a_repeated_id": 3,
        "extra_occurrences": 2,
    }


def test_protocol_init_win_and_down_up(report: dict) -> None:  # type: ignore[type-arg]
    assert report["protocol"] == {"6": 3, "17": 1}
    assert report["init_win_negative"]["FWD Init Win Bytes"] == {"count": 1, "distinct_values": {"-1": 1}}
    assert report["init_win_negative"]["Bwd Init Win Bytes"]["count"] == 1
    assert report["down_up_ratio"] == {"integer_valued": 3, "non_integer": 1}


def test_active_idle_and_flag_columns(report: dict) -> None:  # type: ignore[type-arg]
    active = report["active_idle"]["Active Mean"]
    assert active["max"] == 1500000000000000
    assert active["values_in_epoch_us_2014_2020"] == 1
    assert active["median"] == 0
    psh = report["psh_urg"]["Fwd PSH Flags"]
    assert psh["counts_by_value"] == {"0": 3, "1": 1}
    assert psh["zero_share_pct"] == 75.0
    assert psh["values_subset_of_0_1"] is True
    fin = report["flag_counts"]["FIN Flag Count"]
    assert (fin["max"], fin["values_subset_of_0_1"]) == (3, False)
    assert "CWE Flag Count" in report["flag_counts"]


def test_render_text_is_stable(report: dict) -> None:  # type: ignore[type-arg]
    text = render_text(report)
    assert text == render_text(report)
    assert "[exact duplicate rows] extra copies: 1" in text


def test_cli_writes_json_and_refuses_a_mismatched_header(
    schema_b: FeatureSchema, tmp_path: Path, repo_root: Path, capsys
) -> None:  # type: ignore[no-untyped-def]
    src = _write(tmp_path / "b.csv", schema_b, [_row(schema_b)])
    out = tmp_path / "report.json"
    schema_b_path = str(repo_root / "ml/config/schemas/track_b_darknet2020.yaml")
    assert main(["data-quality", "--schema", schema_b_path, "--csv", str(src), "--json", str(out)]) == 0
    assert json.loads(out.read_text())["shape"]["rows"] == 1
    schema_a_path = str(repo_root / "ml/config/schemas/track_a_cicids2017.yaml")
    assert main(["data-quality", "--schema", schema_a_path, "--csv", str(src)]) == 1
    assert "refused" in capsys.readouterr().out
