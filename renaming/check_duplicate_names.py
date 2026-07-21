import argparse
import csv
from collections import defaultdict
from pathlib import Path


def find_duplicate_names(csv_path: Path) -> dict[str, list[tuple[int, str]]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))

    try:
        header_index = next(
            index for index, row in enumerate(rows) if "name" in row
        )
    except StopIteration as error:
        raise ValueError(f"No 'name' column found in {csv_path}") from error

    headers = rows[header_index]
    name_index = headers.index("name")
    pretty_name_index = (
        headers.index("pretty_name") if "pretty_name" in headers else None
    )

    occurrences: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row_index, row in enumerate(rows[header_index + 1 :], header_index + 2):
        if len(row) <= name_index or not row[name_index]:
            continue
        pretty_name = (
            row[pretty_name_index]
            if pretty_name_index is not None and len(row) > pretty_name_index
            else ""
        )
        occurrences[row[name_index]].append((row_index, pretty_name))

    return {
        name: locations
        for name, locations in occurrences.items()
        if len(locations) > 1
    }


def main() -> None:
    default_csv = Path(__file__).resolve().parent.parent / "balancing.csv"
    parser = argparse.ArgumentParser(
        description="Find duplicate values in a balancing CSV's name column."
    )
    parser.add_argument("csv", nargs="?", type=Path, default=default_csv)
    args = parser.parse_args()

    duplicates = find_duplicate_names(args.csv)
    if not duplicates:
        print("No duplicate attachment names found.")
        return

    print(f"Found {len(duplicates)} duplicate attachment name(s):")
    for name, locations in sorted(duplicates.items()):
        rows = ", ".join(str(row) for row, _ in locations)
        pretty_names = sorted({pretty_name for _, pretty_name in locations if pretty_name})
        pretty_suffix = (
            f" | pretty_name: {', '.join(pretty_names)}" if pretty_names else ""
        )
        print(f"- {name} | rows: {rows}{pretty_suffix}")


if __name__ == "__main__":
    main()
