"""Port selected columns from a CSV or Excel change sheet into a target CSV."""

import argparse
import csv
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from xlsx_to_csv import convert, print_formula_summary


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Port a CSV or Excel change sheet into a target CSV."
    )
    parser.add_argument("changes", type=Path, help="Change sheet (.csv, .xlsx, or .xlsm).")
    parser.add_argument("target", type=Path, help="Target CSV to update.")
    parser.add_argument(
        "header_row", type=int, help="1-based row containing change-sheet headers."
    )
    return parser.parse_args()


def read_changes(path: Path, header_row: int) -> tuple[list[str], dict[str, dict[str, str]]]:
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
                raise ValueError(
                    f"{path}: duplicate name {name!r} at rows "
                    f"{row_numbers[name]} and {row_number}."
                )
            row_numbers[name] = row_number
            rows[name] = {
                header: row[index] if index < len(row) else ""
                for index, header in enumerate(headers)
                if header
            }

    return named_headers, rows


def update_csv(changes: Path, target: Path, header_row: int = 1) -> tuple[int, int]:
    changes = changes.resolve()
    target = target.resolve()
    if not changes.is_file():
        raise FileNotFoundError(f"Change sheet not found: {changes}")
    if not target.is_file():
        raise FileNotFoundError(f"Target CSV not found: {target}")
    if target.suffix.lower() != ".csv":
        raise ValueError("Target must be a .csv file.")

    change_headers, change_rows = read_changes(changes, header_row)
    with target.open("r", encoding="utf-8-sig", newline="") as source:
        lines = list(csv.reader(source))

    if len(lines) < 2:
        raise ValueError("Target CSV must contain a metadata row followed by a header row.")
    target_headers = lines[1]
    if target_headers.count("name") != 1:
        detail = "no" if "name" not in target_headers else "duplicate"
        raise ValueError(f"Target header row has {detail} 'name' column.")

    named_target_headers = [header for header in target_headers if header]
    duplicates = sorted(
        {header for header in named_target_headers if named_target_headers.count(header) > 1}
    )
    if duplicates:
        raise ValueError(f"Target CSV has duplicate header(s): {', '.join(duplicates)}")

    target_columns = {header: index for index, header in enumerate(target_headers) if header}
    missing_columns = sorted(set(change_headers) - set(target_columns))
    if missing_columns:
        print(
            f"Warning: source column(s) not present in target: {', '.join(missing_columns)}",
            file=sys.stderr,
        )

    name_index = target_headers.index("name")
    target_names: dict[str, int] = {}
    matched_names: set[str] = set()
    updated_cells = 0
    for row_number, row in enumerate(lines[2:], start=3):
        if len(row) <= name_index or not row[name_index]:
            continue
        name = row[name_index]
        if name in target_names:
            raise ValueError(
                f"{target}: duplicate name {name!r} at rows "
                f"{target_names[name]} and {row_number}."
            )
        target_names[name] = row_number
        if name not in change_rows:
            continue

        matched_names.add(name)
        if len(row) < len(target_headers):
            row.extend([""] * (len(target_headers) - len(row)))
        for column, value in change_rows[name].items():
            target_index = target_columns.get(column)
            if target_index is None or column == "name":
                continue
            if row[target_index] != value:
                row[target_index] = value
                updated_cells += 1

    missing_names = sorted(set(change_rows) - matched_names)
    for name in missing_names:
        print(f"Warning: source name {name!r} was not found in target.", file=sys.stderr)

    if len(lines[0]) < 2:
        lines[0].extend([""] * (2 - len(lines[0])))
    lines[0][1] = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    with target.open("w", encoding="utf-8-sig", newline="") as output:
        csv.writer(output).writerows(lines)

    return len(matched_names), updated_cells


def run(arguments: argparse.Namespace) -> tuple[int, int]:
    changes = arguments.changes.resolve()
    suffix = changes.suffix.lower()
    if suffix == ".csv":
        return update_csv(changes, arguments.target, arguments.header_row)
    if suffix not in {".xlsx", ".xlsm"}:
        raise ValueError("Change sheet must be a .csv, .xlsx, or .xlsm file.")

    with tempfile.TemporaryDirectory(prefix="deadline-port-") as temporary_directory:
        temporary_csv = Path(temporary_directory) / "changes.csv"
        summary = convert(changes, temporary_csv)
        print_formula_summary(summary)
        return update_csv(temporary_csv, arguments.target, arguments.header_row)


def main() -> int:
    arguments = parse_arguments()
    try:
        matched_rows, updated_cells = run(arguments)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(
        f"Updated {updated_cells} cell(s) across {matched_rows} matched row(s) "
        f"in {arguments.target.resolve()}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
