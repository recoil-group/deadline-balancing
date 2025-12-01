"""Automated one-pass renamer for `balancing.csv`.

Behavior:
  * Reads list of target (new) internal names from `new_item_names.txt`.
  * Loads `balancing.csv`, detecting the header row containing the `name` column.
  * For each new name (in file order):
       - If the new name already exists in the CSV (already renamed), skip.
       - Build candidate OLD names excluding every name that appears in the new
         names list (to avoid selecting another target that was already renamed).
       - Compute similarity against remaining candidates; pick the highest.
       - Rename that OLD name to the NEW name (update only the `name` column).
       - Record (old_name,new_name,score) in a change log CSV.
  * Writes the updated CSV at the end (single write) plus a change log file
    `rename_changes_auto.csv` (overwritten each run).

Similarity metric:
  Average of difflib.SequenceMatcher ratio and token overlap (Dice coefficient) on
  lowercase tokens split by _ - / .

No prompts. No backups. Deterministic single pass.

Edge cases handled:
  * If there are no candidate old names left, the new name is skipped.
  * If the top candidate is identical to the new name (shouldn't happen due to
    checks), it is skipped.

You can safely re-run; already-renamed targets are skipped.
"""

from __future__ import annotations

import csv
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Dict, Tuple

CSV_PATH = Path("../balancing.csv")
NEW_NAMES_PATH = Path("new_item_names4.txt")
CHANGE_LOG_PATH = Path("rename_changes_auto4.csv")

TOKEN_SPLIT_RE = re.compile(r"[_\-/]+")

# Blacklist: substrings that should exclude candidates from matching
BLACKLIST_SUBSTRINGS: List[str] = ["aft", "kf_416"]


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


def load_new_names(path: Path) -> List[str]:
    return [
        ln.strip()
        for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if ln.strip()
    ]


def is_blacklisted(name: str) -> bool:
    """Check if name contains any blacklisted substrings (case-insensitive)."""
    name_lower = name.lower()
    return any(substring.lower() in name_lower for substring in BLACKLIST_SUBSTRINGS)


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
    rows: List[List[str]] = []
    for line in text_lines[header_idx + 1 :]:
        for row in csv.reader([line]):
            rows.append(row)
    return first_line, header, rows, name_col


def write_balancing(
    csv_path: Path, first_line: str, header: List[str], rows: List[List[str]]
):
    tmp = csv_path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        f.write(first_line + "\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    tmp.replace(csv_path)


def auto_rename():
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing {CSV_PATH}")
    if not NEW_NAMES_PATH.exists():
        raise SystemExit(f"Missing {NEW_NAMES_PATH}")

    first_line, header, rows, name_col = load_balancing(CSV_PATH)

    # Build index from current names to row reference
    name_to_row: Dict[str, List[str]] = {}
    for r in rows:
        if len(r) > name_col and r[name_col]:
            name_to_row.setdefault(r[name_col], r)

    target_new_names = load_new_names(NEW_NAMES_PATH)
    target_set = set(target_new_names)

    # Priority prefix mapping: new_prefix -> old_prefix (OLD to be replaced by NEW)
    # Starter list per user: aft mk17 -> fn scar h ; aft mk16 -> fn scar l
    # Normalized to id style (underscores) observed in CSV/new names.
    priority_prefix_pairs: List[Tuple[str, str]] = [
        ("aft_mk_17_", "fn_scar_h_"),
        ("aft_mk_16_", "fn_scar_l_"),
    ]

    changes: List[Tuple[str, str, float]] = []  # (old,new,score)

    for new_name in target_new_names:
        # Skip if already present
        if new_name in name_to_row:
            print(f"[SKIP already present] {new_name}")
            continue

        # Skip if blacklisted
        if is_blacklisted(new_name):
            print(f"[SKIP blacklisted] {new_name}")
            continue

        # Priority prefix direct match handling
        applied_priority = False
        for new_prefix, old_prefix in priority_prefix_pairs:
            if new_name.startswith(new_prefix):
                # Construct expected old candidate by swapping prefix
                old_candidate = old_prefix + new_name[len(new_prefix) :]
                if old_candidate in name_to_row and old_candidate not in target_set:
                    row = name_to_row.pop(old_candidate)
                    row[name_col] = new_name
                    name_to_row[new_name] = row
                    changes.append((old_candidate, new_name, 1.0))
                    print(f"[PRIORITY] {old_candidate} -> {new_name}")
                    applied_priority = True
                break  # only first matching new_prefix considered
        if applied_priority:
            continue

        # Candidate old names exclude any that are in target list (avoid chaining)
        candidates = [n for n in name_to_row.keys() if n not in target_set]
        if not candidates:
            print(f"[NO CANDIDATES] {new_name} (skipped)")
            continue

        # Filter out blacklisted candidates
        candidates = [n for n in candidates if not is_blacklisted(n)]
        if not candidates:
            print(f"[NO CANDIDATES after blacklist] {new_name} (skipped)")
            continue

        # Score all candidates
        best_old = None
        best_score = -1.0
        for old in candidates:
            sc = similarity(new_name, old)
            if sc > best_score:
                best_score = sc
                best_old = old

        if best_old is None:
            print(f"[NO MATCH] {new_name}")
            continue

        if best_old == new_name:
            print(f"[REDUNDANT] {new_name}")
            continue

        # Perform rename in-place
        row = name_to_row.pop(best_old)
        row[name_col] = new_name
        name_to_row[new_name] = row
        changes.append((best_old, new_name, best_score))
        print(f"[RENAMED] {best_old} -> {new_name} score={best_score:.3f}")

    # Write modified CSV
    write_balancing(CSV_PATH, first_line, header, rows)

    # Write change log CSV
    with CHANGE_LOG_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["old_name", "new_name", "score"])
        w.writerows(changes)

    print(f"\n[SUMMARY] {len(changes)} renames written to {CHANGE_LOG_PATH}")


if __name__ == "__main__":
    auto_rename()
