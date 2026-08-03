"""Compare two balancing CSVs and write a focused Markdown diff."""

import argparse
import sys
from pathlib import Path

from _change_report import compare_files, write_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Markdown diff from two balancing CSVs.")
    parser.add_argument("old", type=Path, help="Previous CSV.")
    parser.add_argument("new", type=Path, help="Current CSV.")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        _, total, changed, added, removed = compare_files(arguments.old, arguments.new)
        output_path = Path("diffs") / f"{arguments.new.stem}.md"
        write_report(
            output_path,
            f"{arguments.new.name} Balancing Changes",
            total,
            changed,
            added,
            removed,
        )
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote report to {output_path.resolve()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
