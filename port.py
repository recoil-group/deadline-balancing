"""Preview and port selected columns from a change sheet into a target CSV."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from itertools import groupby
from pathlib import Path

from xlsx_to_csv import ConversionSummary, convert


@dataclass(frozen=True)
class CellChange:
    source_row: int
    target_row: int
    name: str
    column: str
    old: str
    new: str

    @property
    def blank_overwrite(self) -> bool:
        return bool(self.old and not self.new)


@dataclass
class PortPlan:
    lines: list[list[str]]
    matched_rows: int = 0
    changes: list[CellChange] = field(default_factory=list)
    unmatched_names: list[tuple[int, str]] = field(default_factory=list)
    unknown_columns: list[tuple[int, str]] = field(default_factory=list)
    names_with_whitespace: list[tuple[int, str]] = field(default_factory=list)
    headers_with_whitespace: list[tuple[int, str]] = field(default_factory=list)
    formula_without_cache: list[tuple[int, str, str]] = field(default_factory=list)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Port a CSV or Excel change sheet into a target CSV."
    )
    parser.add_argument("changes", type=Path, help="Change sheet (.csv, .xlsx, or .xlsm).")
    parser.add_argument("target", type=Path, help="Target CSV to update.")
    parser.add_argument("header_row", type=int, help="1-based row containing change-sheet headers.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Preview format.")
    return parser.parse_args()


def read_changes(path: Path, header_row: int) -> tuple[list[str], dict[str, dict[str, str]], dict[str, int]]:
    if header_row < 1:
        raise ValueError("Change-sheet header row must be at least 1.")
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        try:
            for _ in range(header_row - 1):
                next(reader)
            headers = next(reader)
        except StopIteration as error:
            raise ValueError(f"Change sheet has no header row {header_row}: {path}") from error
        named_headers = [header for header in headers if header]
        duplicates = sorted({header for header in named_headers if named_headers.count(header) > 1})
        if duplicates:
            raise ValueError(f"Change sheet has duplicate header(s): {', '.join(duplicates)}")
        if "name" not in headers:
            raise ValueError(f"Change-sheet header row {header_row} has no 'name' column.")
        name_index = headers.index("name")
        rows: dict[str, dict[str, str]] = {}
        row_numbers: dict[str, int] = {}
        for row_number, row in enumerate(reader, start=header_row + 1):
            if len(row) <= name_index or not row[name_index]:
                continue
            name = row[name_index]
            if name in rows:
                raise ValueError(f"{path}: duplicate name {name!r} at rows {row_numbers[name]} and {row_number}.")
            row_numbers[name] = row_number
            rows[name] = {header: row[index] if index < len(row) else "" for index, header in enumerate(headers) if header}
    return headers, rows, row_numbers


def build_plan(changes: Path, target: Path, header_row: int, summary: ConversionSummary | None = None) -> PortPlan:
    if not changes.is_file():
        raise FileNotFoundError(f"Change sheet not found: {changes}")
    if not target.is_file():
        raise FileNotFoundError(f"Target CSV not found: {target}")
    if target.suffix.lower() != ".csv":
        raise ValueError("Target must be a .csv file.")
    change_headers, change_rows, source_rows = read_changes(changes, header_row)
    with target.open("r", encoding="utf-8-sig", newline="") as source:
        lines = list(csv.reader(source))
    if len(lines) < 2:
        raise ValueError("Target CSV must contain a metadata row followed by a header row.")
    target_headers = lines[1]
    if target_headers.count("name") != 1:
        detail = "no" if "name" not in target_headers else "duplicate"
        raise ValueError(f"Target header row has {detail} 'name' column.")
    named_target_headers = [header for header in target_headers if header]
    duplicates = sorted({header for header in named_target_headers if named_target_headers.count(header) > 1})
    if duplicates:
        raise ValueError(f"Target CSV has duplicate header(s): {', '.join(duplicates)}")
    target_columns = {header: index for index, header in enumerate(target_headers) if header}
    plan = PortPlan(
        lines=lines,
        unknown_columns=[
            (index, header)
            for index, header in enumerate(change_headers, start=1)
            if header and header != "name" and header not in target_columns
        ],
        names_with_whitespace=sorted(
            (row, name)
            for name, row in source_rows.items()
            if name != name.strip()
        ),
        headers_with_whitespace=[
            (index, header)
            for index, header in enumerate(change_headers, start=1)
            if header and header != header.strip()
        ],
    )
    name_index = target_headers.index("name")
    target_names: dict[str, int] = {}
    matched_names: set[str] = set()
    for row_number, row in enumerate(lines[2:], start=3):
        if len(row) <= name_index or not row[name_index]:
            continue
        name = row[name_index]
        if name in target_names:
            raise ValueError(f"{target}: duplicate name {name!r} at rows {target_names[name]} and {row_number}.")
        target_names[name] = row_number
        source_row = change_rows.get(name)
        if source_row is None:
            continue
        matched_names.add(name)
        plan.matched_rows += 1
        if len(row) < len(target_headers):
            row.extend([""] * (len(target_headers) - len(row)))
        for column, new_value in source_row.items():
            target_index = target_columns.get(column)
            if target_index is None or column == "name":
                continue
            old_value = row[target_index]
            if old_value == new_value:
                continue
            change = CellChange(
                source_rows[name],
                row_number,
                name,
                column,
                old_value,
                new_value,
            )
            plan.changes.append(change)
            # ConversionSummary uses 1-based worksheet coordinates; CSV column is zero-based.
            if summary and (source_rows[name], change_headers.index(column) + 1) in summary.missing_formula_cells:
                plan.formula_without_cache.append((source_rows[name], name, column))
    plan.unmatched_names = sorted(
        (source_rows[name], name) for name in set(change_rows) - matched_names
    )
    return plan


def change_data(change: CellChange) -> dict[str, object]:
    return {
        "source_row": change.source_row,
        "target_row": change.target_row,
        "name": change.name,
        "column": change.column,
        "old": change.old,
        "new": change.new,
        "blank_overwrite": change.blank_overwrite,
    }


def warning_data(plan: PortPlan) -> list[dict[str, object]]:
    warnings: list[dict[str, object]] = []
    for row, name in plan.unmatched_names:
        warnings.append({"kind": "source_name_not_in_target", "source_row": row, "name": name})
    for column, header in plan.unknown_columns:
        warnings.append({"kind": "unknown_source_column", "column": column, "header": header})
    for change in plan.changes:
        if change.blank_overwrite:
            warnings.append({"kind": "blank_overwrite", **change_data(change)})
        if change.column == "pretty_name":
            warnings.append({"kind": "pretty_name_change", **change_data(change)})
    for row, name in plan.names_with_whitespace:
        warnings.append({"kind": "name_whitespace", "source_row": row, "name": name})
    for column, header in plan.headers_with_whitespace:
        warnings.append({"kind": "header_whitespace", "column": column, "header": header})
    return warnings


def plan_data(plan: PortPlan) -> dict[str, object]:
    return {
        "matched_rows": plan.matched_rows,
        "effective_changes": len(plan.changes),
        "changes": [change_data(change) for change in plan.changes],
        "warnings": warning_data(plan),
        "formula_without_cache": [dict(row=row, name=name, column=column) for row, name, column in plan.formula_without_cache],
    }


def print_plan(plan: PortPlan, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(plan_data(plan), indent=2))
        return
    blank_overwrites = sum(change.blank_overwrite for change in plan.changes)
    pretty_name_changes = sum(
        change.column == "pretty_name" for change in plan.changes
    )
    print(f"Matched rows: {plan.matched_rows}; changed cells: {len(plan.changes)}")
    if any(
        (
            blank_overwrites,
            pretty_name_changes,
            plan.unmatched_names,
            plan.unknown_columns,
            plan.names_with_whitespace,
            plan.headers_with_whitespace,
        )
    ):
        print("\nWarnings:")
        if pretty_name_changes:
            print(f"  {pretty_name_changes} pretty_name change(s)")
        if blank_overwrites:
            print(f"  {blank_overwrites} blank overwrite(s)")
        if plan.unmatched_names:
            details = "; ".join(
                f"row {row} {name!r}" for row, name in plan.unmatched_names
            )
            print(f"  Source names not in target ({len(plan.unmatched_names)}): {details}")
        if plan.unknown_columns:
            details = ", ".join(header for _, header in plan.unknown_columns)
            print(f"  Ignored columns ({len(plan.unknown_columns)}): {details}")
        if plan.names_with_whitespace:
            details = "; ".join(
                f"row {row} {name!r}" for row, name in plan.names_with_whitespace
            )
            print(
                "  Names with surrounding whitespace "
                f"({len(plan.names_with_whitespace)}): {details}"
            )
        if plan.headers_with_whitespace:
            details = "; ".join(
                f"column {column} {header!r}"
                for column, header in plan.headers_with_whitespace
            )
            print(
                "  Headers with surrounding whitespace "
                f"({len(plan.headers_with_whitespace)}): {details}"
            )
    if plan.changes:
        print("\nChanges:")
        key = lambda change: (change.source_row, change.target_row, change.name)
        ordered_changes = sorted(plan.changes, key=key)
        for (source_row, _, name), changes in groupby(ordered_changes, key=key):
            print(f"\n{name} (source row {source_row})")
            for change in changes:
                marker = "!" if change.blank_overwrite or change.column == "pretty_name" else " "
                old = "blank" if not change.old else repr(change.old)
                new = "blank" if not change.new else repr(change.new)
                print(f"  {marker} {change.column}: {old} -> {new}")
    if plan.formula_without_cache:
        print("\nErrors:")
        for row, name, column in plan.formula_without_cache:
            print(f"  Imported formula has no cached result: row {row} {name}.{column}")


def write_plan(target: Path, plan: PortPlan) -> None:
    if not plan.changes:
        return
    for change in plan.changes:
        plan.lines[change.target_row - 1][plan.lines[1].index(change.column)] = change.new
    if len(plan.lines[0]) < 2:
        plan.lines[0].extend([""] * (2 - len(plan.lines[0])))
    plan.lines[0][1] = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", delete=False, dir=target.parent, prefix=f".{target.name}.", suffix=".tmp") as output:
            temporary_name = output.name
            csv.writer(output).writerows(plan.lines)
        os.replace(temporary_name, target)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def run(arguments: argparse.Namespace) -> PortPlan:
    changes = arguments.changes.resolve()
    target = arguments.target.resolve()
    suffix = changes.suffix.lower()
    if suffix == ".csv":
        return build_plan(changes, target, arguments.header_row)
    if suffix not in {".xlsx", ".xlsm"}:
        raise ValueError("Change sheet must be a .csv, .xlsx, or .xlsm file.")
    with tempfile.TemporaryDirectory(prefix="deadline-port-") as directory:
        temporary_csv = Path(directory) / "changes.csv"
        summary = convert(changes, temporary_csv)
        return build_plan(temporary_csv, target, arguments.header_row, summary)


def main() -> int:
    arguments = parse_arguments()
    try:
        plan = run(arguments)
        print_plan(plan, arguments.format)
        if plan.formula_without_cache:
            print(
                "Error: imported formula cells without cached results cannot be ported.",
                file=sys.stderr,
            )
            return 1
        if not arguments.dry_run:
            write_plan(arguments.target.resolve(), plan)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    if arguments.format == "text" and not arguments.dry_run:
        print(f"\nUpdated {arguments.target.resolve()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
