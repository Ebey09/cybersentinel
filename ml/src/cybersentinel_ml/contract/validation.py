"""Structural checks on raw CSV headers and model-ready feature frames.

Every check returns CheckResult objects instead of raising, so callers can show
ALL problems at once (an analyst or developer should not fix one issue, rerun,
and discover the next).
"""

from __future__ import annotations

from collections import Counter
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
    """Compare a CSV header with the schema's expected raw header: exact names, exact order.

    No normalisation is applied here on purpose. If a dataset needs renaming or
    whitespace stripping, the dataset adapter must do it explicitly, so the
    difference is visible in code review instead of hidden in a loader.
    A repeated name passes only if the schema declares it in positional_renames (ADR 0011).
    """
    expected = schema.expected_raw_header()
    actual = list(columns)
    results: list[CheckResult] = []

    want, got = Counter(expected), Counter(actual)
    # A name repeated in the file, or repeated a different number of times than declared.
    bad_counts = sorted(c for c, n in got.items() if n != want.get(c, 1) and (n > 1 or c in want))
    declared = sorted(c for c, n in want.items() if n > 1)
    ok_detail = "no duplicate column names"
    if declared:
        ok_detail = f"no undeclared duplicates (declared, resolved by position: {_fmt(declared)})"
    results.append(
        CheckResult(
            "header_no_duplicates",
            not bad_counts,
            ok_detail
            if not bad_counts
            else "duplicate columns: "
            + ", ".join(f"{c!r} appears {got[c]} times, schema expects {want.get(c, 0)}" for c in bad_counts),
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

    if not missing and not unexpected and not bad_counts:
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


def resolve_raw_header(columns: Sequence[str], schema: FeatureSchema) -> list[str]:
    """Apply the schema's declared positional renames and return the resolved header.

    Refuses unless the header is exactly the expected raw header, so a column is never
    renamed on a guess. Dataset adapters call this after check_raw_header passed.
    """
    if list(columns) != schema.expected_raw_header():
        raise ValueError("header does not match the schema's expected raw header; run check_raw_header")
    return list(schema.raw_columns)


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
