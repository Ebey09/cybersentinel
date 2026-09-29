"""Raw-data quality diagnostics for one CSV file (measurement only).

Streams the file with the csv module, so repeated header names (for example two
'Label' columns) are kept as they are instead of being renamed by a loader. The
header must match the schema exactly (ADR 0011) before any column is measured by
position. Nothing is dropped, imputed, de-duplicated or normalized: every number
describes the raw file. Interpreting the numbers is left to the reader.
"""

from __future__ import annotations

import csv
import hashlib
import math
import statistics
from array import array
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from cybersentinel_ml.contract.schema import FeatureSchema
from cybersentinel_ml.contract.validation import all_passed, check_raw_header

# Column groups by raw CICFlowMeter header name. Missing names are skipped, so the
# same report works for either track.
FLOW_ID = "Flow ID"
PROTOCOL = "Protocol"
INIT_WIN = ["FWD Init Win Bytes", "Bwd Init Win Bytes"]
PSH_URG = ["Fwd PSH Flags", "Bwd PSH Flags", "Fwd URG Flags", "Bwd URG Flags"]
FLAG_COUNTS = [
    "FIN Flag Count",
    "SYN Flag Count",
    "RST Flag Count",
    "PSH Flag Count",
    "ACK Flag Count",
    "URG Flag Count",
    "CWE Flag Count",
    "CWR Flag Count",
    "ECE Flag Count",
]
DOWN_UP = "Down/Up Ratio"
ACTIVE_IDLE_PREFIXES = ("Active ", "Idle ")

# Epoch time in microseconds for 2014-01-01 and 2021-01-01 (UTC). Values in this range
# look like absolute timestamps rather than durations (VERIFY V9).
EPOCH_US_2014 = 1_388_534_400_000_000
EPOCH_US_2021 = 1_609_459_200_000_000

_MAX_DISTINCT = 50  # cap on distinct values listed for one column
_MISSING_TOKENS = {"", "nan", "NaN", "NAN", "null", "NULL", "None"}


def _parse(value: str) -> float | None:
    """float for a finite or infinite number, NaN for a missing marker, None for non-numeric text."""
    s = value.strip()
    if s in _MISSING_TOKENS:
        return math.nan
    try:
        return float(s)
    except ValueError:
        return None


def _num(x: float) -> int | float:
    return int(x) if x.is_integer() else x


def _counter_json(c: Counter[Any], limit: int | None = _MAX_DISTINCT) -> dict[str, int]:
    items = sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0])))
    if limit is not None:
        items = items[:limit]
    return {str(k): n for k, n in items}


def _read(path: Path) -> tuple[list[str], Iterable[list[str]], Any]:
    fh = path.open("r", encoding="utf-8-sig", newline="")
    reader = csv.reader(fh)
    return next(reader), reader, fh


def analyze_csv(path: str | Path, schema: FeatureSchema) -> dict[str, Any]:
    """Measure one raw CSV that matches `schema`. Raises ValueError if the header does not match."""
    csv.field_size_limit(10 * 1024 * 1024)
    header, rows, fh = _read(Path(path))
    try:
        checks = check_raw_header(header, schema)
        if not all_passed(checks):
            failed = "; ".join(f"{c.name}: {c.detail}" for c in checks if not c.passed)
            raise ValueError(
                f"header does not match schema {schema.schema_id} v{schema.schema_version}: {failed}"
            )
        names = list(schema.raw_columns)  # resolved names, unique, same positions as the raw header
        idx = {n: i for i, n in enumerate(names)}
        numeric = [f.source_column for f in schema.features + schema.excluded_features]
        numeric += [c.source_column for c in schema.identifier_columns if c.dtype == "int64"]
        numeric = [c for c in names if c in set(numeric)]  # file order
        label_cols = [lab.source_column for lab in schema.label_columns]
        active_idle = [c for c in names if c.startswith(ACTIVE_IDLE_PREFIXES)]
        tracked = active_idle  # columns whose values are kept for medians

        n_rows = short_rows = long_rows = 0
        rows_with_missing = rows_with_inf = 0
        missing: Counter[str] = Counter()
        pos_inf: Counter[str] = Counter()
        neg_inf: Counter[str] = Counter()
        non_numeric: Counter[str] = Counter()
        labels = {c: Counter() for c in label_cols}
        row_hashes: Counter[bytes] = Counter()
        flow_ids: Counter[str] = Counter()
        protocol: Counter[str] = Counter()
        negatives = {c: Counter() for c in INIT_WIN if c in idx}
        values = {c: Counter() for c in PSH_URG + FLAG_COUNTS if c in idx}
        tracked_vals = {c: array("d") for c in tracked}
        down_up_integer = down_up_fraction = 0

        for row in rows:
            n_rows += 1
            if len(row) != len(names):
                if len(row) < len(names):
                    short_rows += 1
                else:
                    long_rows += 1
                row = (row + [""] * len(names))[: len(names)]
            row_hashes[
                hashlib.blake2b("\x1f".join(row).encode("utf-8", "surrogatepass"), digest_size=16).digest()
            ] += 1
            for c in label_cols:
                labels[c][row[idx[c]]] += 1
            if FLOW_ID in idx:
                flow_ids[row[idx[FLOW_ID]]] += 1
            if PROTOCOL in idx:
                protocol[row[idx[PROTOCOL]].strip()] += 1

            row_missing = row_inf = False
            for c in numeric:
                x = _parse(row[idx[c]])
                if x is None:
                    non_numeric[c] += 1
                    continue
                if math.isnan(x):
                    missing[c] += 1
                    row_missing = True
                    continue
                if math.isinf(x):
                    (pos_inf if x > 0 else neg_inf)[c] += 1
                    row_inf = True
                    continue
                if c in negatives and x < 0:
                    negatives[c][_num(x)] += 1
                if c in values:
                    values[c][_num(x)] += 1
                if c in tracked_vals:
                    tracked_vals[c].append(x)
                if c == DOWN_UP:
                    if x.is_integer():
                        down_up_integer += 1
                    else:
                        down_up_fraction += 1
            rows_with_missing += row_missing
            rows_with_inf += row_inf
    finally:
        fh.close()

    def pct(n: int) -> float:
        return round(100.0 * n / n_rows, 4) if n_rows else 0.0

    dup_groups = [n for n in row_hashes.values() if n > 1]
    fid_groups = [n for n in flow_ids.values() if n > 1]

    def summary(c: str) -> dict[str, Any]:
        v = tracked_vals[c]
        if not v:
            return {"finite_values": 0}
        ts_like = sum(1 for x in v if EPOCH_US_2014 <= x <= EPOCH_US_2021)
        return {
            "finite_values": len(v),
            "min": _num(min(v)),
            "median": _num(statistics.median(v)),
            "max": _num(max(v)),
            "values_ge_1e12": sum(1 for x in v if x >= 1e12),
            "values_in_epoch_us_2014_2020": ts_like,
        }

    def flag_summary(c: str) -> dict[str, Any]:
        cnt = values[c]
        keys = sorted(cnt)
        finite = sum(cnt.values())
        return {
            "finite_values": finite,
            "min": keys[0] if keys else None,
            "max": keys[-1] if keys else None,
            "distinct": len(keys),
            "zero_share_pct": round(100.0 * cnt.get(0, 0) / finite, 4) if finite else None,
            "values_subset_of_0_1": set(keys) <= {0, 1},
            "counts_by_value": {str(k): cnt[k] for k in keys[:_MAX_DISTINCT]},
        }

    return {
        "file": str(path),
        "schema": f"{schema.schema_id} v{schema.schema_version}",
        "shape": {
            "rows": n_rows,
            "raw_columns": len(header),
            "short_rows": short_rows,
            "long_rows": long_rows,
            "declared_duplicate_headers": [
                {"position": r.position, "raw_name": r.raw_name, "resolved_name": r.resolved_name}
                for r in schema.positional_renames
            ],
        },
        "labels": {
            c: {
                k: {"count": n, "pct": pct(n)} for k, n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))
            }
            for c, cnt in labels.items()
        },
        "missing": {
            "rows_with_any_missing": rows_with_missing,
            "per_column": _counter_json(missing, None),
        },
        "non_finite": {
            "rows_with_any_infinity": rows_with_inf,
            "positive_infinity": _counter_json(pos_inf, None),
            "negative_infinity": _counter_json(neg_inf, None),
        },
        "non_numeric_in_numeric_columns": _counter_json(non_numeric, None),
        "exact_duplicate_rows": {
            "extra_copies": sum(n - 1 for n in dup_groups),
            "rows_in_duplicate_groups": sum(dup_groups),
            "duplicate_groups": len(dup_groups),
        },
        "flow_id": (
            {
                "rows": n_rows,
                "unique": len(flow_ids),
                "ids_occurring_more_than_once": len(fid_groups),
                "rows_with_a_repeated_id": sum(fid_groups),
                "extra_occurrences": sum(n - 1 for n in fid_groups),
            }
            if FLOW_ID in idx
            else None
        ),
        "protocol": _counter_json(protocol, None) if PROTOCOL in idx else None,
        "init_win_negative": {
            c: {"count": sum(cnt.values()), "distinct_values": _counter_json(cnt)}
            for c, cnt in negatives.items()
        },
        "active_idle": {c: summary(c) for c in active_idle},
        "psh_urg": {c: flag_summary(c) for c in PSH_URG if c in values},
        "flag_counts": {c: flag_summary(c) for c in FLAG_COUNTS if c in values},
        "down_up_ratio": (
            {"integer_valued": down_up_integer, "non_integer": down_up_fraction} if DOWN_UP in idx else None
        ),
    }


def render_text(report: dict[str, Any]) -> str:
    """Plain-text rendering of `analyze_csv` output, in a stable order."""
    out: list[str] = []
    s = report["shape"]
    out.append(f"file:   {report['file']}")
    out.append(f"schema: {report['schema']}")
    out.append(
        f"rows: {s['rows']}  raw columns: {s['raw_columns']}  short rows: {s['short_rows']}  "
        f"long rows: {s['long_rows']}"
    )
    for r in s["declared_duplicate_headers"]:
        out.append(
            f"declared duplicate header: position {r['position']} raw {r['raw_name']!r} "
            f"resolved {r['resolved_name']!r}"
        )
    for col, vals in report["labels"].items():
        out.append(f"\n[labels] {col!r}")
        for k, v in vals.items():
            out.append(f"  {v['count']:>10}  {v['pct']:>8.4f}%  {k!r}")
    m = report["missing"]
    out.append(f"\n[missing] rows with any missing value: {m['rows_with_any_missing']}")
    for c, n in m["per_column"].items():
        out.append(f"  {n:>10}  {c!r}")
    nf = report["non_finite"]
    out.append(f"\n[non-finite] rows with any infinity: {nf['rows_with_any_infinity']}")
    for c, n in nf["positive_infinity"].items():
        out.append(f"  +inf {n:>10}  {c!r}")
    for c, n in nf["negative_infinity"].items():
        out.append(f"  -inf {n:>10}  {c!r}")
    out.append(
        f"\n[non-numeric text in numeric columns] {report['non_numeric_in_numeric_columns'] or 'none'}"
    )
    d = report["exact_duplicate_rows"]
    out.append(
        f"\n[exact duplicate rows] extra copies: {d['extra_copies']}  rows in duplicate groups: "
        f"{d['rows_in_duplicate_groups']}  groups: {d['duplicate_groups']}"
    )
    if report["flow_id"]:
        f = report["flow_id"]
        out.append(
            f"\n[Flow ID] rows: {f['rows']}  unique: {f['unique']}  ids occurring >1: "
            f"{f['ids_occurring_more_than_once']}  rows with a repeated id: {f['rows_with_a_repeated_id']}  "
            f"extra occurrences: {f['extra_occurrences']}"
        )
    if report["protocol"] is not None:
        out.append(f"\n[Protocol] {report['protocol']}")
    out.append("\n[init window, values below zero]")
    for c, v in report["init_win_negative"].items():
        out.append(f"  {c!r}: {v['count']}  distinct: {v['distinct_values']}")
    out.append("\n[Active/Idle] finite | min | median | max | >=1e12 | in epoch-us 2014-2020")
    for c, v in report["active_idle"].items():
        out.append(
            f"  {c!r}: {v.get('finite_values')} | {v.get('min')} | {v.get('median')} | {v.get('max')} | "
            f"{v.get('values_ge_1e12')} | {v.get('values_in_epoch_us_2014_2020')}"
        )
    for section in ("psh_urg", "flag_counts"):
        out.append(f"\n[{section}] min | max | distinct | zero % | subset of {{0,1}} | counts by value")
        for c, v in report[section].items():
            out.append(
                f"  {c!r}: {v['min']} | {v['max']} | {v['distinct']} | {v['zero_share_pct']} | "
                f"{v['values_subset_of_0_1']} | {v['counts_by_value']}"
            )
    if report["down_up_ratio"]:
        du = report["down_up_ratio"]
        out.append(
            f"\n[Down/Up Ratio] integer-valued: {du['integer_valued']}  non-integer: {du['non_integer']}"
        )
    return "\n".join(out) + "\n"
