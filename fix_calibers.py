"""Normalize TRUE/FALSE cells in a caliber CSV to lowercase booleans."""

import argparse
import csv
import sys
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lowercase TRUE/FALSE cells in a caliber CSV."
    )
    parser.add_argument(
        "csv", nargs="?", type=Path, default=Path("calibers.csv"), help="CSV to update."
    )
    return parser.parse_args()


def lowercase_booleans(csv_path: Path) -> int:
    csv_path = csv_path.resolve()
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    if csv_path.suffix.lower() != ".csv":
        raise ValueError("Input must be a .csv file.")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))

    changes = 0
    for row in rows:
        for index, value in enumerate(row):
            if value.casefold() in {"true", "false"} and value != value.lower():
                row[index] = value.lower()
                changes += 1

    if changes:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as target:
            csv.writer(target).writerows(rows)
    return changes


def main() -> int:
    arguments = parse_arguments()
    try:
        changes = lowercase_booleans(arguments.csv)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Lowercased {changes} boolean cell(s) in {arguments.csv.resolve()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
