"""Minimal script to replace substrings in the name column of balancing.csv.

Usage: py rename_replace.py "old_string" "new_string"
"""

import csv
import sys
from pathlib import Path

CSV_PATH = Path("../balancing.csv")

if len(sys.argv) != 3:
    print('Usage: py rename_replace.py "old_string" "new_string"')
    sys.exit(1)

old_str = sys.argv[1]
new_str = sys.argv[2]


def load_balancing(csv_path: Path):
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
    rows: list[list[str]] = []
    for line in text_lines[header_idx + 1 :]:
        for row in csv.reader([line]):
            rows.append(row)
    return first_line, header, rows, name_col


def write_balancing(
    csv_path: Path, first_line: str, header: list[str], rows: list[list[str]]
):
    tmp = csv_path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        f.write(first_line + "\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    tmp.replace(csv_path)


if not CSV_PATH.exists():
    raise SystemExit(f"Missing {CSV_PATH}")

first_line, header, rows, name_col = load_balancing(CSV_PATH)

# Replace in name column
for row in rows:
    if len(row) > name_col:
        old_name = row[name_col]
        new_name = old_name.replace(old_str, new_str)
        if new_name != old_name:
            print(f"{old_name} -> {new_name}")
        row[name_col] = new_name

write_balancing(CSV_PATH, first_line, header, rows)

print(f"Replaced '{old_str}' with '{new_str}' in name column.")
