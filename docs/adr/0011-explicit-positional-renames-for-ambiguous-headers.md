# ADR 0011: Ambiguous raw column names are resolved by declared positional renames, never silently

- Status: Accepted
- Date: 2026-09-24
- Refines: ADR 0005

## Context

CIC-Darknet2020 has two label layers: traffic type and application category. The Phase 1 Track B schema listed the second label column as `Label.1`. That name was not taken from the file. It is what pandas produces when a CSV header repeats a name (`Label`, `Label`). So the schema treated a loader artifact as a raw column name.

That matters because the contract says the raw header must match the schema exactly and nothing is renamed silently (`ML_DATA_CONTRACT.md` section 3). If the real file repeats `Label`:

- `check-header` would report a duplicate and fail. That part is correct.
- But the schema offered no way to say "yes, this file repeats `Label`, and here is how we tell the two apart". The schema validator also forbids duplicate names in `raw_columns`, because every column needs exactly one role.
- Reading the file with pandas would "fix" it by renaming to `Label.1` behind our back, which is exactly the silent renaming the contract forbids.

The real header is not known yet (V4).

## Decision

1. `raw_columns` keeps one unique name per column. Roles, experiments and label columns refer to these names.
2. A schema may declare `positional_renames`. Each entry gives a `position`, the `raw_name` the file has there, the `resolved_name` used in `raw_columns`, and a `reason`. The validator checks that `raw_columns[position]` is the resolved name.
3. `check_raw_header` / `check-header` compare the file against `expected_raw_header()`: `raw_columns` with the declared raw names put back. A repeated name passes only if the schema declares exactly that repeat. Anything else still fails. It never renames anything, and the CLI prints the declared renames so they are visible.
4. The rename is a separate, explicit step: `resolve_raw_header()`. It refuses to run unless the header is exactly the expected raw header. Dataset adapters (Phase 4) call it after the header check passed.
5. Dataset readers must not rely on pandas' automatic `.1` suffixes. The adapter reads the header itself and applies the declared renames.
6. The draft Track B schema now assumes the file repeats `Label` at positions 83 and 84, and names the second one `Label (column 84)`. This is marked `[VERIFY] V4`. If the real file gives the second column its own name, that name goes into `raw_columns` and the rename is deleted.

## Consequences

- `check-header` tells the truth either way. A file with `Label` twice passes only because the schema says so. A file with a literal `Label.1`, or with the internal name `Label (column 84)`, fails.
- `inspect-labels --column Label` refuses a file that repeats `Label` and asks for `--column-index`. Use 83 for traffic type and 84 for application category (V6).
- The mechanism is generic. It can handle other datasets with repeated names. It does not add any renaming for whitespace or casing, which stays an adapter decision per the contract.

## Alternatives considered

- **Keep `Label.1` in the schema.** Rejected: it encodes a pandas artifact as if it were the file's header.
- **Allow duplicates in `raw_columns` and assign roles by position everywhere.** Rejected: a much larger change to the schema model and every consumer, for one column.
- **Let pandas rename and accept `Label.1`.** Rejected: silent renaming.

## Open verification items

- V4: the real Track B header, and whether it repeats `Label`.
- V6: the label strings in both columns.
