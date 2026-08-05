"""Normalize TRUE/FALSE cells in any CSV to lowercase booleans.

Usage:
    python fix_booleans.py calibers.csv
    python fix_booleans.py balancing.csv optics.csv --dry-run
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

BOOLEANS = {"true", "false"}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lowercase TRUE/FALSE cells in one or more CSVs."
    )
    parser.add_argument("csv", nargs="+", type=Path, help="CSV file(s) to update.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing.",
    )
    return parser.parse_args()


def lowercase_booleans(csv_path: Path, dry_run: bool = False) -> int:
    csv_path = csv_path.resolve()
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    if csv_path.suffix.lower() != ".csv":
        raise ValueError(f"Input must be a .csv file: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))

    changes = 0
    for row in rows:
        for index, value in enumerate(row):
            if value.casefold() in BOOLEANS and value != value.lower():
                row[index] = value.lower()
                changes += 1

    if changes and not dry_run:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as target:
            csv.writer(target).writerows(rows)
    return changes


def main() -> int:
    arguments = parse_arguments()
    status = 0
    for csv_path in arguments.csv:
        try:
            changes = lowercase_booleans(csv_path, arguments.dry_run)
        except Exception as error:
            print(f"Error: {error}", file=sys.stderr)
            status = 1
            continue

        verb = "Would lowercase" if arguments.dry_run else "Lowercased"
        print(f"{verb} {changes} boolean cell(s) in {csv_path.resolve()}.")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
