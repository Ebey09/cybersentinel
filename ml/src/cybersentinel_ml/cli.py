"""Command-line entry point: `cybersentinel-ml <command>`.

Phase 1 commands only check contracts. They never train or predict.

  validate-config   load every schema and experiment config and cross-check them
  check-header      compare a real CSV header with a schema (closes [VERIFY] items)
  inspect-labels    count label values in a CSV column (closes [VERIFY] items)
  schema-docs       render a schema as a Markdown reference table
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import yaml

from cybersentinel_ml.contract.experiment import load_experiment
from cybersentinel_ml.contract.schema import FeatureSchema, load_schema
from cybersentinel_ml.contract.validation import all_passed, check_raw_header

# Errors that mean 'this config file is broken' (pydantic's ValidationError is a ValueError).
_CONFIG_ERRORS = (ValueError, yaml.YAMLError, FileNotFoundError)

# Some CIC CSVs have very long lines; the default csv field limit is 128 KiB.
csv.field_size_limit(10 * 1024 * 1024)


def _find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "ml" / "config").is_dir():
            return p
    raise SystemExit("could not find the repository root (a folder containing ml/config)")


def cmd_validate_config(args: argparse.Namespace) -> int:
    root = _find_repo_root(Path(args.root).resolve())
    ok = True
    for path in sorted((root / "ml" / "config" / "schemas").glob("*.yaml")):
        try:
            s = load_schema(path)
            print(
                f"[ok]   schema {path.relative_to(root)}  id={s.schema_id} v{s.schema_version} "
                f"status={s.status.value} features={len(s.features)} excluded={len(s.excluded_features)} "
                f"sha256={s.sha256()[:12]}"
            )
        except _CONFIG_ERRORS as exc:  # report every broken file, then fail
            ok = False
            print(f"[FAIL] schema {path.relative_to(root)}: {exc}")
    for path in sorted((root / "ml" / "config" / "experiments").glob("*.yaml")):
        try:
            exp, _schema, digest = load_experiment(path, root)
            print(
                f"[ok]   experiment {path.relative_to(root)}  id={exp.experiment_id} "
                f"classes={exp.classes()} sha256={digest[:12]}"
            )
        except _CONFIG_ERRORS as exc:
            ok = False
            print(f"[FAIL] experiment {path.relative_to(root)}: {exc}")
    return 0 if ok else 1


def _read_header(path: Path) -> list[str]:
    # utf-8-sig strips a byte-order mark, which is an encoding artifact, not part of a column name.
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return next(csv.reader(fh))


def cmd_check_header(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    header = _read_header(Path(args.csv))
    print(f"schema: {schema.schema_id} v{schema.schema_version} ({len(schema.raw_columns)} columns expected)")
    print(f"csv:    {args.csv} ({len(header)} columns found)")
    results = check_raw_header(header, schema)
    for r in results:
        print(f"  [{'ok' if r.passed else 'FAIL'}] {r.name}: {r.detail}")
    passed = all_passed(results)
    print("RESULT: header matches schema" if passed else "RESULT: header does NOT match schema")
    return 0 if passed else 1


def cmd_inspect_labels(args: argparse.Namespace) -> int:
    path = Path(args.csv)
    counts: Counter[str] = Counter()
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        if args.column_index is not None:
            idx = args.column_index
            # A negative index would silently count from the end; an index past the header would crash later.
            if not 0 <= idx < len(header):
                print(
                    f"column index {idx} is out of range. Header has {len(header)} columns (valid: 0 to {len(header) - 1})"
                )
                return 1
        else:
            matches = [i for i, c in enumerate(header) if c == args.column]
            if not matches:
                print(f"column {args.column!r} not found. Header has: {header}")
                return 1
            if len(matches) > 1:
                print(f"column {args.column!r} appears {len(matches)} times at {matches}; use --column-index")
                return 1
            idx = matches[0]
        bad_rows = 0
        for row in reader:
            if idx >= len(row):
                bad_rows += 1
                continue
            counts[row[idx]] += 1
    total = sum(counts.values())
    print(f"{path}: column index {idx} ({header[idx]!r}), {total} rows, {len(counts)} distinct values")
    if bad_rows:
        print(f"WARNING: {bad_rows} rows were shorter than the header")
    for value, n in counts.most_common():
        print(f"  {n:>10}  {100 * n / total:6.2f}%  {value!r}")

    if args.experiment:
        root = _find_repo_root(Path(args.experiment).resolve().parent)
        exp, _schema, _ = load_experiment(args.experiment, root)
        unmapped = sorted(v for v in counts if v not in exp.label_map)
        unused = sorted(k for k in exp.label_map if k not in counts)
        print(f"experiment {exp.experiment_id}:")
        print(f"  labels in CSV but not in label_map: {unmapped or 'none'}")
        print(f"  labels in label_map but not in CSV: {unused or 'none'}")
        return 1 if unmapped else 0
    return 0


def _cell(v: object) -> str:
    return "" if v is None else str(v).replace("|", "\\|").replace("\n", " ")


def render_schema_markdown(schema: FeatureSchema, sha: str) -> str:
    out = [
        f"# {schema.title}",
        "",
        "> Generated from the schema YAML by `cybersentinel-ml schema-docs`. Do not edit by hand.",
        "",
        f"- Schema: `{schema.schema_id}` v{schema.schema_version} (status: **{schema.status.value}**)",
        f"- Content SHA-256: `{sha}`",
        f"- Dataset: {schema.dataset.name}",
        f"- Extractor: {schema.extractor.name}, commit `{schema.extractor.commit}`",
        f"- Flow timeout: {schema.extractor.flow_timeout_us} us, activity timeout: "
        f"{schema.extractor.activity_timeout_us} us",
        f"- PCAP parity: **{schema.parity.status.value}**",
        f"- Preprocessing version: {schema.preprocessing.version}",
        f"- Raw columns: {len(schema.raw_columns)}, model features: {len(schema.features)}, "
        f"excluded: {len(schema.excluded_features)}, identifiers: {len(schema.identifier_columns)}",
        "",
        "## Model input features (in order)",
        "",
        "| # | name | source column | dtype | unit | range | missing values | scaling (LR) | encoding | PCAP | status | meaning |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, f in enumerate(schema.features, 1):
        rng = f"[{_cell(f.expected_range.min)}, {_cell(f.expected_range.max) or 'inf'}]"
        out.append(
            f"| {i} | `{f.name}` | {_cell(f.source_column)} | {f.dtype} | {_cell(f.unit)} | {rng} | "
            f"{_cell(f.missing_values)} | {_cell(f.scaling.logistic_regression)} | {f.encoding} | "
            f"{f.pcap_available} | {f.status} | {_cell(f.meaning)} {_cell(f.notes)} |"
        )
    out += ["", "## Derived features (appended after schema features)", ""]
    for d in schema.preprocessing.derived_features:
        out.append(f"- `{d.name}`: {d.definition}. {d.reason}")
    out += ["", "## Excluded features", "", "| name | source column | reason |", "|---|---|---|"]
    for f in schema.excluded_features:
        out.append(f"| `{f.name}` | {_cell(f.source_column)} | {_cell(f.notes)} |")
    out += [
        "",
        "## Identifier columns (never model inputs)",
        "",
        "| name | source column | used for | reason |",
        "|---|---|---|---|",
    ]
    for c in schema.identifier_columns:
        out.append(f"| `{c.name}` | {_cell(c.source_column)} | {', '.join(c.used_for)} | {_cell(c.reason)} |")
    out += ["", "## Label columns", ""]
    for lab in schema.label_columns:
        out.append(f"- `{lab.source_column}` -> `{lab.name}`. {_cell(lab.notes)}")
    out += ["", "## Output vocabulary", "", f"- Allowed: {', '.join(schema.output_vocabulary.allowed_terms)}"]
    if schema.output_vocabulary.forbidden_terms:
        out.append(f"- Forbidden: {', '.join(schema.output_vocabulary.forbidden_terms)}")
    return "\n".join(out) + "\n"


def cmd_schema_docs(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    text = render_schema_markdown(schema, schema.sha256())
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cybersentinel-ml", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate-config", help="validate all schemas and experiment configs")
    v.add_argument("--root", default=".", help="any folder inside the repository")
    v.set_defaults(func=cmd_validate_config)

    h = sub.add_parser("check-header", help="compare a CSV header with a schema")
    h.add_argument("--schema", required=True)
    h.add_argument("--csv", required=True)
    h.set_defaults(func=cmd_check_header)

    lab = sub.add_parser("inspect-labels", help="count values of a label column")
    lab.add_argument("--csv", required=True)
    g = lab.add_mutually_exclusive_group(required=True)
    g.add_argument("--column")
    g.add_argument("--column-index", type=int)
    lab.add_argument("--experiment", help="also report labels missing from this experiment's label_map")
    lab.set_defaults(func=cmd_inspect_labels)

    d = sub.add_parser("schema-docs", help="render a schema as Markdown")
    d.add_argument("--schema", required=True)
    d.add_argument("--out")
    d.set_defaults(func=cmd_schema_docs)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
