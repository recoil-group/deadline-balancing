"""Check for new names that don't exist in balancing.csv.

Behavior:
  * Reads list of target (new) internal names from `new_item_names4.txt`.
  * Loads `balancing.csv`, detecting the header row containing the `name` column.
  * Outputs any new names that are not present in the CSV.

No modifications are made.
"""

from __future__ import annotations

import csv
from pathlib import Path

CSV_PATH = Path("../balancing.csv")
NEW_NAMES_PATH = Path("new_item_names4.txt")


def load_new_names(path: Path) -> list[str]:
    return [
        ln.strip()
        for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if ln.strip()
    ]


def load_balancing_names(csv_path: Path) -> set[str]:
    text_lines = csv_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not text_lines:
        raise SystemExit("balancing.csv empty")
    first_line = text_lines[0]
    header_idx = None
    header = []
    for i, line in enumerate(text_lines[1:], start=1):
        for row in csv.reader([line]):
            if "name" in row:
                header_idx = i
                header = row
        if header_idx is not None:
            break
    if header_idx is None:
        raise SystemExit("Could not locate header row with 'name'")
    name_col = header.index("name")
    names = set()
    for line in text_lines[header_idx + 1 :]:
        for row in csv.reader([line]):
            if len(row) > name_col and row[name_col]:
                names.add(row[name_col])
    return names


def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing {CSV_PATH}")
    if not NEW_NAMES_PATH.exists():
        raise SystemExit(f"Missing {NEW_NAMES_PATH}")

    target_new_names = load_new_names(NEW_NAMES_PATH)
    existing_names = load_balancing_names(CSV_PATH)

    missing_names = [name for name in target_new_names if name not in existing_names]

    if missing_names:
        print("New names not found in balancing.csv:")
        for name in missing_names:
            print(f"{name}")
    else:
        print("All new names are present in balancing.csv")


if __name__ == "__main__":
    main()
