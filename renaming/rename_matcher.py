"""Minimal interactive rename matcher for `balancing.csv`.

What it does:
    1. Reads new internal names from `new_item_names.txt` (one per line).
    2. Loads `balancing.csv`, finds the header row that contains the `name` column.
    3. For each new name, shows TOP_CANDIDATES best fuzzy matches from current names.
    4. You pick the index, or:
             - s : skip
             - c : custom search (substring / regex)
             - q : quit early
         Then it asks to confirm replacement (you can enter a custom replacement target).
    5. Writes the CSV in-place after each accepted rename (safe if interrupted).

Only the `name` column value is changed; nothing else is modified.
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Dict, Tuple, Optional


@dataclass
class RowRef:
    index: int  # index in rows list
    row: List[str]  # actual row list


def load_balancing(
    csv_path: Path,
) -> Tuple[str, List[str], List[List[str]], Dict[str, RowRef], int]:
    """Load balancing.csv returning (first_line, header_fields, rows, name_index).

    We keep both raw lines (for potential advanced preservation) and parsed rows.
    """
    text = csv_path.read_text(encoding="utf-8", errors="replace").splitlines(
        keepends=False
    )
    if not text:
        raise SystemExit("balancing.csv is empty")
    first_line = text[0]
    # Find header (line containing 'name' exactly as a field)
    header_idx = None
    header_fields: List[str] = []
    for i, line in enumerate(text[1:], start=1):  # skip first meta line
        # Use csv reader for this single line
        for row in csv.reader([line]):
            if "name" in row:
                header_idx = i
                header_fields = row
        if header_idx is not None:
            break
    if header_idx is None:
        raise SystemExit(
            "Could not locate header row containing 'name' in balancing.csv"
        )
    name_col = header_fields.index("name")

    # Parse all rows after header
    parsed_rows: List[List[str]] = []
    name_lookup: Dict[str, RowRef] = {}
    for i, line in enumerate(text[header_idx + 1 :], start=header_idx + 1):
        for row in csv.reader([line]):
            parsed_rows.append(row)
            if len(row) > name_col and row[name_col]:
                n = row[name_col]
                if n not in name_lookup:  # first occurrence wins
                    name_lookup[n] = RowRef(index=len(parsed_rows) - 1, row=row)

    return first_line, header_fields, parsed_rows, name_lookup, name_col


def load_new_names(path: Path) -> List[str]:
    return [
        ln.strip()
        for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if ln.strip()
    ]


TOKEN_SPLIT_RE = re.compile(r"[_\-/]+")


def tokenize(name: str) -> List[str]:
    return [t for t in TOKEN_SPLIT_RE.split(name.lower()) if t]


def similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    seq_ratio = SequenceMatcher(None, a, b).ratio()
    ta, tb = set(tokenize(a)), set(tokenize(b))
    if not ta or not tb:
        token_ratio = 0.0
    else:
        inter = len(ta & tb)
        token_ratio = 2 * inter / (len(ta) + len(tb))
    return (seq_ratio + token_ratio) / 2.0


def top_matches(
    new_name: str, existing: List[str], limit: int = 8
) -> List[Tuple[str, float]]:
    scores = [(ex, similarity(new_name, ex)) for ex in existing]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:limit]


def write_csv(
    csv_path: Path, first_line: str, header: List[str], rows: List[List[str]]
):
    tmp_path = csv_path.with_suffix(".tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as f:
        f.write(first_line + "\n")
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(header)
        for r in rows:
            writer.writerow(r)
    tmp_path.replace(csv_path)


TOP_CANDIDATES = 6
CSV_PATH = Path("balancing.csv")
NEW_NAMES_PATH = Path("new_item_names.txt")
CHANGE_LOG_PATH = Path("renamed_items.csv")  # appended list of old,new


def interactive():
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing {CSV_PATH}")
    if not NEW_NAMES_PATH.exists():
        raise SystemExit(f"Missing {NEW_NAMES_PATH}")

    first_line, header, rows, name_lookup, name_col = load_balancing(CSV_PATH)
    existing_names = list(name_lookup.keys())
    new_names = load_new_names(NEW_NAMES_PATH)

    # Prepare change log header if file missing
    if not CHANGE_LOG_PATH.exists():
        CHANGE_LOG_PATH.write_text("old_name,new_name\n", encoding="utf-8")

    for new_name in new_names:
        print(f"\n=== New name: {new_name}")
        matches = top_matches(new_name, existing_names, limit=TOP_CANDIDATES)
        for idx, (cand, score) in enumerate(matches, start=1):
            try:
                pretty_idx = header.index("pretty_name")
                pretty = (
                    name_lookup[cand].row[pretty_idx]
                    if pretty_idx < len(name_lookup[cand].row)
                    else ""
                )
            except ValueError:
                pretty = ""
            print(f"  {idx}. {cand:<55} score={score:.3f} {pretty}")
        print("  s. skip  |  c. custom search  |  q. quit")

        choice_name: Optional[str] = None
        while choice_name is None:
            sel = input("Select (number / s / c / q): ").strip().lower()
            if sel in {"s", "skip", ""}:
                print("[SKIPPED]")
                break
            if sel in {"q", "quit"}:
                print("[QUIT]")
                write_csv(CSV_PATH, first_line, header, rows)
                return
            if sel in {"c", "custom"}:
                pattern = input(" substring or regex: ").strip()
                if not pattern:
                    continue
                try:
                    rx = re.compile(pattern)
                    cands = [n for n in existing_names if rx.search(n)]
                except re.error:
                    cands = [n for n in existing_names if pattern in n]
                if not cands:
                    print("  (no matches)")
                    continue
                for i2, n2 in enumerate(cands, start=1):
                    print(f"    {i2}. {n2}")
                pick = input("  pick #: ").strip()
                if pick.isdigit():
                    i_sel = int(pick) - 1
                    if 0 <= i_sel < len(cands):
                        choice_name = cands[i_sel]
                        break
                continue
            if sel.isdigit():
                i_sel = int(sel) - 1
                if 0 <= i_sel < len(matches):
                    choice_name = matches[i_sel][0]
                    break
                print("  invalid index")
                continue
            print("  invalid selection")

        if not choice_name:
            continue
        if choice_name not in name_lookup:
            print("[MISSING after selection] skipping")
            continue

        override = input(
            f" Replace '{choice_name}' with '{new_name}'? (Y/n/custom): "
        ).strip()
        if override and override.lower() not in {"y", "yes"}:
            if override.lower() in {"n", "no"}:
                print("[SKIPPED]")
                continue
            target_new_name = override
        else:
            target_new_name = new_name

        if target_new_name in name_lookup and target_new_name != choice_name:
            print("[ALREADY EXISTS] skipping (duplicate target)")
            continue

        rr = name_lookup[choice_name]
        rr.row[name_col] = target_new_name
        del name_lookup[choice_name]
        name_lookup[target_new_name] = rr
        existing_names = list(name_lookup.keys())
        write_csv(CSV_PATH, first_line, header, rows)
        with CHANGE_LOG_PATH.open("a", encoding="utf-8") as logf:
            logf.write(f"{choice_name},{target_new_name}\n")
        print(f"[RENAMED] {choice_name} -> {target_new_name} (saved & logged)")

    print("\nDone. All new names processed (or skipped).")


if __name__ == "__main__":
    interactive()
