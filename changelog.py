"""Compare two balancing CSVs and write a versioned changelog."""

import argparse
import sys
from pathlib import Path

from _change_report import compare_files, write_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a changelog from two balancing CSVs.")
    parser.add_argument("old", type=Path, help="Previous balancing CSV.")
    parser.add_argument("new", type=Path, help="Current balancing CSV.")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        version, total, changed, added, _ = compare_files(arguments.old, arguments.new)
        if not version:
            raise ValueError("New CSV metadata row has no version in its first cell.")
        output_path = Path("changelogs") / f"{version.replace('.', '-')}.md"
        write_report(
            output_path,
            f"{version} Balancing Changes",
            total,
            changed,
            added,
        )
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote report to {output_path.resolve()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
