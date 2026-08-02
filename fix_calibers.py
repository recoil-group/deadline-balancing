"""Normalize TRUE/FALSE cells in a caliber CSV to lowercase booleans.

Usage:
    python lowercase_caliber_booleans.py
    python lowercase_caliber_booleans.py path/to/calibers.csv
"""

import csv
import sys
from pathlib import Path


def lowercase_booleans(csv_path: Path) -> int:
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


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("calibers.csv")
    changes = lowercase_booleans(csv_path)
    print(f"Lowercased {changes} boolean cell(s) in {csv_path}.")


if __name__ == "__main__":
    main()
