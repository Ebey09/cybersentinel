"""Structural checks on raw CSV headers and model-ready feature frames.

Every check returns CheckResult objects instead of raising, so callers can show
ALL problems at once (an analyst or developer should not fix one issue, rerun,
and discover the next).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd

from cybersentinel_ml.contract.schema import FeatureSchema

_MAX_LISTED = 10


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def _fmt(items: Sequence[str]) -> str:
    items = list(items)
    shown = ", ".join(repr(i) for i in items[:_MAX_LISTED])
    extra = f" (+{len(items) - _MAX_LISTED} more)" if len(items) > _MAX_LISTED else ""
    return shown + extra


def all_passed(results: Sequence[CheckResult]) -> bool:
    return all(r.passed for r in results)


def check_raw_header(columns: Sequence[str], schema: FeatureSchema) -> list[CheckResult]:
    """Compare a CSV header with schema.raw_columns: exact names, exact order.

    No normalisation is applied here on purpose. If a dataset needs renaming or
    whitespace stripping, the dataset adapter must do it explicitly, so the
    difference is visible in code review instead of hidden in a loader.
    """
    expected = list(schema.raw_columns)
    actual = list(columns)
    results: list[CheckResult] = []

    dupes = sorted({c for c in actual if actual.count(c) > 1})
    results.append(
        CheckResult(
            "header_no_duplicates",
            not dupes,
            "no duplicate column names" if not dupes else f"duplicate columns: {_fmt(dupes)}",
        )
    )

    missing = [c for c in expected if c not in actual]
    unexpected = [c for c in actual if c not in expected]

    hint = ""
    if missing and unexpected:
        stripped = {c.strip(): c for c in unexpected}
        ws_only = [m for m in missing if m in stripped]
        if ws_only:
            hint = f" Note: {len(ws_only)} missing column(s) exist with extra surrounding whitespace."

    results.append(
        CheckResult(
            "header_no_missing_columns",
            not missing,
            "all expected columns present" if not missing else f"missing: {_fmt(missing)}.{hint}",
        )
    )
    results.append(
        CheckResult(
            "header_no_unexpected_columns",
            not unexpected,
            "no unexpected columns" if not unexpected else f"unexpected: {_fmt(unexpected)}",
        )
    )

    if not missing and not unexpected and not dupes:
        first_diff = next((i for i, (a, e) in enumerate(zip(actual, expected, strict=True)) if a != e), None)
        results.append(
            CheckResult(
                "header_order",
                first_diff is None,
                "column order matches"
                if first_diff is None
                else f"order differs at position {first_diff}: got {actual[first_diff]!r}, "
                f"expected {expected[first_diff]!r}",
            )
        )
    else:
        results.append(CheckResult("header_order", False, "not checked because column sets differ"))
    return results


def check_feature_frame(frame: pd.DataFrame, expected_order: Sequence[str]) -> list[CheckResult]:
    """Check a model-ready frame: names, order and numeric dtypes."""
    expected = list(expected_order)
    actual = [str(c) for c in frame.columns]
    results: list[CheckResult] = []

    missing = [c for c in expected if c not in actual]
    unexpected = [c for c in actual if c not in expected]
    results.append(
        CheckResult(
            "features_no_missing",
            not missing,
            "all model features present" if not missing else f"missing features: {_fmt(missing)}",
        )
    )
    results.append(
        CheckResult(
            "features_no_unexpected",
            not unexpected,
            "no unexpected features" if not unexpected else f"unexpected features: {_fmt(unexpected)}",
        )
    )

    if not missing and not unexpected:
        ok = actual == expected
        results.append(
            CheckResult(
                "features_order",
                ok,
                "feature order matches the model"
                if ok
                else "feature order differs from the order the model was trained with",
            )
        )
    else:
        results.append(CheckResult("features_order", False, "not checked because feature sets differ"))

    bad_types = [
        c
        for c in actual
        if c in expected
        and (not pd.api.types.is_numeric_dtype(frame[c]) or pd.api.types.is_bool_dtype(frame[c]))
    ]
    results.append(
        CheckResult(
            "features_numeric_dtypes",
            not bad_types,
            "all features numeric" if not bad_types else f"non-numeric features: {_fmt(bad_types)}",
        )
    )
    return results
