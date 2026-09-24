"""Header and feature-frame checks."""

from __future__ import annotations

import pandas as pd
import pytest

from cybersentinel_ml.contract.schema import FeatureSchema
from cybersentinel_ml.contract.validation import (
    all_passed,
    check_feature_frame,
    check_raw_header,
    resolve_raw_header,
)

from .conftest import make_frame


def _by_name(results):  # type: ignore[no-untyped-def]
    return {r.name: r for r in results}


def test_exact_header_passes(schema_a: FeatureSchema) -> None:
    assert all_passed(check_raw_header(schema_a.raw_columns, schema_a))


def test_missing_and_unexpected_columns_are_reported(schema_a: FeatureSchema) -> None:
    header = [c for c in schema_a.raw_columns if c != "Flow Duration"] + ["Surprise"]
    r = _by_name(check_raw_header(header, schema_a))
    assert not r["header_no_missing_columns"].passed
    assert "Flow Duration" in r["header_no_missing_columns"].detail
    assert not r["header_no_unexpected_columns"].passed
    assert "Surprise" in r["header_no_unexpected_columns"].detail


def test_reordered_header_fails_order_check(schema_a: FeatureSchema) -> None:
    header = list(schema_a.raw_columns)
    header[7], header[8] = header[8], header[7]
    r = _by_name(check_raw_header(header, schema_a))
    assert r["header_no_missing_columns"].passed
    assert not r["header_order"].passed
    assert "position 7" in r["header_order"].detail


def test_whitespace_padded_columns_get_a_hint(schema_a: FeatureSchema) -> None:
    header = [" " + c if c == "Protocol" else c for c in schema_a.raw_columns]
    r = _by_name(check_raw_header(header, schema_a))
    assert not r["header_no_missing_columns"].passed
    assert "whitespace" in r["header_no_missing_columns"].detail


def test_undeclared_duplicate_header_column_fails(schema_a: FeatureSchema) -> None:
    header = [*schema_a.raw_columns, "Flow ID"]
    r = _by_name(check_raw_header(header, schema_a))
    assert not r["header_no_duplicates"].passed
    assert "'Flow ID' appears 2 times" in r["header_no_duplicates"].detail


def test_declared_duplicate_label_passes_and_resolves_by_position(schema_b: FeatureSchema) -> None:
    # Draft Track B assumes the raw file repeats "Label" (ADR 0011). The raw header passes
    # only because the schema declares it, and the rename happens in a separate, explicit step.
    header = schema_b.expected_raw_header()
    assert header.count("Label") == 2
    r = _by_name(check_raw_header(header, schema_b))
    assert all_passed(list(r.values()))
    assert "declared" in r["header_no_duplicates"].detail
    assert resolve_raw_header(header, schema_b) == schema_b.raw_columns


def test_resolved_name_is_not_accepted_as_a_raw_column(schema_b: FeatureSchema) -> None:
    # The resolved name exists only inside the pipeline. A file that already carries it
    # (or a pandas-style "Label.1") is a different header and must fail, not be renamed.
    for second in ("Label (column 84)", "Label.1"):
        header = [*schema_b.raw_columns[:-1], second]
        r = _by_name(check_raw_header(header, schema_b))
        assert not r["header_no_unexpected_columns"].passed
        assert not r["header_no_duplicates"].passed  # 'Label' appears once, schema expects twice
        with pytest.raises(ValueError):
            resolve_raw_header(header, schema_b)


def test_feature_frame_happy_path(schema_a: FeatureSchema) -> None:
    order = schema_a.candidate_model_order()
    assert all_passed(check_feature_frame(make_frame(order), order))


def test_feature_frame_detects_missing_unexpected_order_and_dtype(schema_a: FeatureSchema) -> None:
    order = schema_a.candidate_model_order()
    frame = make_frame(order)

    r = _by_name(check_feature_frame(frame.drop(columns=[order[0]]), order))
    assert not r["features_no_missing"].passed

    r = _by_name(check_feature_frame(frame.assign(extra=1.0), order))
    assert not r["features_no_unexpected"].passed

    r = _by_name(check_feature_frame(frame[list(reversed(order))], order))
    assert not r["features_order"].passed

    bad = frame.copy()
    bad[order[3]] = "not a number"
    r = _by_name(check_feature_frame(bad, order))
    assert not r["features_numeric_dtypes"].passed

    as_bool = frame.copy()
    as_bool[order[4]] = True
    r = _by_name(check_feature_frame(as_bool, order))
    assert not r["features_numeric_dtypes"].passed


def test_integer_columns_count_as_numeric() -> None:
    frame = pd.DataFrame({"a": [1, 2], "b": [0.5, 1.5]})
    assert all_passed(check_feature_frame(frame, ["a", "b"]))
