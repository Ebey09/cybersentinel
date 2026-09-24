"""Header and feature-frame checks."""

from __future__ import annotations

import pandas as pd

from cybersentinel_ml.contract.schema import FeatureSchema
from cybersentinel_ml.contract.validation import all_passed, check_feature_frame, check_raw_header

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


def test_duplicate_header_columns_fail(schema_b: FeatureSchema) -> None:
    # CIC-Darknet2020 may ship two columns literally named "Label". The schema expects
    # "Label" and "Label.1", so a raw duplicate must be caught, not silently accepted.
    header = [c if c != "Label.1" else "Label" for c in schema_b.raw_columns]
    r = _by_name(check_raw_header(header, schema_b))
    assert not r["header_no_duplicates"].passed
    assert not r["header_no_missing_columns"].passed


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
