"""Shared CSV comparison and Markdown report helpers."""

import csv
from pathlib import Path


STAT_DIRECTIONS = {
    "ergonomics": True,
    "weight": False,
    "horizontal_recoil": False,
    "vertical_recoil": False,
    "magazine_capacity": True,
    "barrel_deviation": False,
    "bullet_damage": True,
    "bullet_velocity": True,
    "buck_barrel_deviation": False,
    "fire_rate": True,
    "muzzle_loudness": False,
    "price": False,
}


def read_csv(path: Path) -> tuple[str, list[str], dict[str, dict[str, str]]]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Input must be a .csv file: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        try:
            metadata = next(reader)
            headers = next(reader)
        except StopIteration as error:
            raise ValueError(f"CSV must contain a metadata row and header row: {path}") from error

        named_headers = [header for header in headers if header]
        duplicates = sorted({header for header in named_headers if named_headers.count(header) > 1})
        if duplicates:
            raise ValueError(f"CSV has duplicate header(s): {', '.join(duplicates)}")
        if "name" not in headers:
            raise ValueError(f"CSV header row has no 'name' column: {path}")

        name_index = headers.index("name")
        rows: dict[str, dict[str, str]] = {}
        row_numbers: dict[str, int] = {}
        for row_number, values in enumerate(reader, start=3):
            if len(values) <= name_index or not values[name_index]:
                continue
            name = values[name_index]
            if name in rows:
                raise ValueError(
                    f"{path}: duplicate name {name!r} at rows "
                    f"{row_numbers[name]} and {row_number}."
                )
            row_numbers[name] = row_number
            rows[name] = {
                header: values[index] if index < len(values) else ""
                for index, header in enumerate(headers)
                if header
            }

    return metadata[0] if metadata else "", named_headers, rows


def format_header(header: str) -> str:
    return " ".join(word.capitalize() for word in header.split("_"))


def compare_rows(
    old_row: dict[str, str] | None,
    new_row: dict[str, str],
    columns: list[str],
) -> list[str]:
    changes = []
    for column in columns:
        new = new_row.get(column, "")
        if old_row is None:
            if new:
                changes.append(f"{format_header(column)}: `{new}`")
            continue

        old = old_row.get(column, "") or "0"
        new = new or "0"
        if old == new:
            continue
        try:
            color = (
                "green"
                if (float(new) > float(old)) == STAT_DIRECTIONS[column]
                else "red"
            )
            changes.append(
                f'{format_header(column)}: `{old}` -> <code class="{color}">{new}</code>'
            )
        except (TypeError, ValueError):
            changes.append(f"{format_header(column)}: `{old}` -> `{new}`")
    return changes


def entry(row: dict[str, str], changes: list[str] | None = None) -> str:
    pretty_name = row.get("pretty_name") or row["name"]
    if not changes:
        return f"### {pretty_name}\n"
    return f"### {pretty_name}\n\n" + " \\\n".join(changes) + "\n"


def compare_files(
    old_path: Path, new_path: Path
) -> tuple[str, int, list[str], list[str], list[str]]:
    _, old_headers, old_rows = read_csv(old_path)
    version, new_headers, new_rows = read_csv(new_path)
    changed_columns = [
        column
        for column in STAT_DIRECTIONS
        if column in old_headers and column in new_headers
    ]
    new_columns = [column for column in STAT_DIRECTIONS if column in new_headers]

    changed: list[str] = []
    added: list[str] = []
    for name, new_row in new_rows.items():
        if name in old_rows:
            changes = compare_rows(old_rows[name], new_row, changed_columns)
            if changes:
                changed.append(entry(new_row, changes))
        else:
            added.append(entry(new_row, compare_rows(None, new_row, new_columns)))

    removed = [entry(old_rows[name]) for name in old_rows if name not in new_rows]
    return version, len(new_rows), changed, added, removed


def write_report(
    output_path: Path,
    title: str,
    total: int,
    changed: list[str],
    added: list[str],
    removed: list[str] | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as output:
        output.write(f"# {title}\n\n")
        output.write(f"[Changed attachments](#changed-attachments): {len(changed)}\n\n")
        output.write(f"[New attachments](#new-attachments): {len(added)}\n\n")
        if removed is not None:
            output.write(f"[Removed attachments](#removed-attachments): {len(removed)}\n\n")
        output.write(f"Total attachments: {total}\n\n")
        output.write("## Changed Attachments\n\n")
        output.write("\n".join(changed))
        output.write("\n## New Attachments\n\n")
        output.write("\n".join(added))
        if removed is not None:
            output.write("\n## Removed Attachments\n\n")
            output.write("\n".join(removed))
