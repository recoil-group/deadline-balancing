"""Apply the rename list in renames.csv to the name column of CSV and Excel sheets."""

from __future__ import annotations

import argparse
import csv
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

HEADER_SEARCH_ROWS = 10
NAME_COLUMN = "name"
EXCEL_SUFFIXES = (".xlsx", ".xlsm")


@dataclass
class Rename:
    path: Path
    sheet: str
    row: int
    old: str
    new: str
    collision: bool = False


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply renames.csv to the name column of CSV and Excel sheets."
    )
    parser.add_argument("targets", type=Path, nargs="+", help="Sheets to update.")
    parser.add_argument(
        "--renames", type=Path, default=Path("renames.csv"), help="Rename list CSV."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    return parser.parse_args()


# Rename list


def read_renames(path: Path) -> dict[str, str]:
    """Read the rename list, collapsing chains such as A -> B and B -> C into A -> C."""
    if not path.is_file():
        raise FileNotFoundError(f"Rename list not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))
    if not rows or [value.strip() for value in rows[0][:2]] != ["old_name", "new_name"]:
        raise ValueError(f"{path}: header row must be 'old_name,new_name'.")

    direct: dict[str, str] = {}
    for number, row in enumerate(rows[1:], start=2):
        old, new = ([value.strip() for value in row] + ["", ""])[:2]
        if not old and not new:
            continue
        if not old or not new:
            raise ValueError(f"{path} row {number}: needs both an old and a new name.")
        if old == new:
            raise ValueError(f"{path} row {number}: {old!r} renames to itself.")
        if direct.get(old, new) != new:
            raise ValueError(
                f"{path} row {number}: {old!r} already renames to {direct[old]!r}."
            )
        direct[old] = new

    resolved: dict[str, str] = {}
    for old in direct:
        chain = [old]
        while chain[-1] in direct:
            chain.append(direct[chain[-1]])
            if chain[-1] in chain[:-1]:
                raise ValueError(f"{path}: rename chain loops: {' -> '.join(chain)}")
        resolved[old] = chain[-1]
    return resolved


# CSV sheets
#
# Only the renamed cells are rewritten, so untouched text keeps its exact
# quoting, line endings, and encoding.


def split_records(text: str) -> list[str]:
    """Split CSV text into records, keeping quoted line breaks inside a record."""
    records: list[str] = []
    current: list[str] = []
    quoted = False
    for line in text.splitlines(keepends=True):
        current.append(line)
        quoted ^= line.count('"') % 2 == 1
        if not quoted:
            records.append("".join(current))
            current = []
    if current:
        records.append("".join(current))
    return records


def field_spans(record: str) -> list[tuple[int, int, str]]:
    """Return (start, end, value) for every field in one CSV record."""
    body = record.rstrip("\r\n")
    spans: list[tuple[int, int, str]] = []
    index = 0
    while True:
        start = index
        if index < len(body) and body[index] == '"':
            index += 1
            value: list[str] = []
            while index < len(body):
                if body[index] == '"':
                    if body[index + 1 : index + 2] == '"':
                        value.append('"')
                        index += 2
                        continue
                    index += 1
                    break
                value.append(body[index])
                index += 1
            text = "".join(value)
        else:
            comma = body.find(",", index)
            index = len(body) if comma == -1 else comma
            text = body[start:index]
        spans.append((start, index, text))
        if index >= len(body):
            return spans
        index += 1


def encode_field(value: str) -> str:
    if any(character in value for character in ',"\r\n'):
        return '"' + value.replace('"', '""') + '"'
    return value


def rename_csv(path: Path, mapping: dict[str, str], write: bool) -> list[Rename]:
    raw = path.read_bytes()
    records = split_records(raw.decode("utf-8-sig"))

    header = next(
        (
            (number, [value for _, _, value in field_spans(record)].index(NAME_COLUMN))
            for number, record in enumerate(records[:HEADER_SEARCH_ROWS])
            if NAME_COLUMN in [value for _, _, value in field_spans(record)]
        ),
        None,
    )
    if header is None:
        return []
    header_row, name_index = header

    cells = [
        (number, spans[name_index])
        for number, record in enumerate(records[header_row + 1 :], start=header_row + 2)
        if len(spans := field_spans(record)) > name_index and spans[name_index][2]
    ]
    names = {value: number for number, (_, _, value) in cells}

    renames: list[Rename] = []
    for number, (start, end, old) in cells:
        new = mapping.get(old)
        if new is None:
            continue
        collision = names.get(new, number) != number
        renames.append(Rename(path, "", number, old, new, collision))
        if collision:
            continue
        record = records[number - 1]
        records[number - 1] = record[:start] + encode_field(new) + record[end:]

    if write and any(not rename.collision for rename in renames):
        text = ("﻿" if raw.startswith(b"\xef\xbb\xbf") else "") + "".join(records)
        path.write_bytes(text.encode("utf-8"))
    return renames


# Excel sheets
#
# Workbooks are edited as XML inside the package, so cached formula results,
# styling, and every untouched part survive the round trip. Cell text always
# lives in the shared string table; Excel does not write inline strings.


def unescape(value: str) -> str:
    for entity, character in (("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")):
        value = value.replace(entity, character)
    return value


def escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def shared_strings(xml: str) -> list[str]:
    return [
        "".join(unescape(text) for text in re.findall(r"<t[^>]*>(.*?)</t>", item, re.S))
        for item in re.findall(r"<si>(.*?)</si>", xml, re.S)
    ]


def worksheets(entries: dict[str, bytes]) -> list[tuple[str, str]]:
    """Return (sheet title, package path) in workbook order."""
    workbook = entries.get("xl/workbook.xml", b"").decode("utf-8")
    relationships = entries.get("xl/_rels/workbook.xml.rels", b"").decode("utf-8")
    targets = dict(
        re.findall(r'<Relationship[^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', relationships)
    )
    sheets = []
    for element in re.findall(r"<sheet\b[^>]*>", workbook):
        title = re.search(r'name="([^"]*)"', element)
        identifier = re.search(r'r:id="([^"]*)"', element)
        target = targets.get(identifier.group(1), "") if identifier else ""
        package = f"xl/{target.lstrip('/')}".replace("xl/xl/", "xl/")
        if package in entries:
            sheets.append((unescape(title.group(1)) if title else package, package))
    return sheets


def string_cells(xml: str, strings: list[str]) -> list[tuple[int, int, str, int, str]]:
    """Return (start, end, column, row, text) for every shared-string cell."""
    cells = []
    for match in re.finditer(r'<c\b[^>]*?(?:/>|>.*?</c>)', xml, re.S):
        cell = match.group(0)
        reference = re.search(r'\br="([A-Z]+)(\d+)"', cell)
        index = re.search(r"<v>(\d+)</v>", cell)
        if not reference or not index or 't="s"' not in cell:
            continue
        if int(index.group(1)) < len(strings):
            cells.append(
                (
                    match.start(),
                    match.end(),
                    reference.group(1),
                    int(reference.group(2)),
                    strings[int(index.group(1))],
                )
            )
    return cells


def rename_excel(path: Path, mapping: dict[str, str], write: bool) -> list[Rename]:
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        entries = {info.filename: archive.read(info.filename) for info in infos}

    strings_path = "xl/sharedStrings.xml"
    strings_xml = entries.get(strings_path, b"").decode("utf-8")
    strings = shared_strings(strings_xml)
    added: list[str] = []
    renames: list[Rename] = []

    for title, sheet_path in worksheets(entries):
        xml = entries[sheet_path].decode("utf-8")
        cells = string_cells(xml, strings)
        header = next(
            ((row, column) for _, _, column, row, text in cells if text.strip() == NAME_COLUMN),
            None,
        )
        if header is None or header[0] > HEADER_SEARCH_ROWS:
            continue
        header_row, name_column = header

        column_cells = [
            cell for cell in cells if cell[2] == name_column and cell[3] > header_row
        ]
        names = {text: row for _, _, _, row, text in column_cells}

        edits: list[tuple[int, int, str]] = []
        for start, end, _, row, old in column_cells:
            new = mapping.get(old)
            if new is None:
                continue
            collision = names.get(new, row) != row
            renames.append(Rename(path, title, row, old, new, collision))
            if collision:
                continue
            if new not in strings:
                strings.append(new)
                added.append(new)
            replacement = re.sub(r"<v>\d+</v>", f"<v>{strings.index(new)}</v>", xml[start:end])
            edits.append((start, end, replacement))

        for start, end, replacement in reversed(edits):
            xml = xml[:start] + replacement + xml[end:]
        entries[sheet_path] = xml.encode("utf-8")

    if not write or not any(not rename.collision for rename in renames):
        return renames

    if added:
        items = "".join(f"<si><t>{escape(value)}</t></si>" for value in added)
        strings_xml = strings_xml.replace("</sst>", items + "</sst>")
        entries[strings_path] = re.sub(
            r'uniqueCount="\d+"', f'uniqueCount="{len(strings)}"', strings_xml, count=1
        ).encode("utf-8")

    temporary = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w") as archive:
        for info in infos:
            archive.writestr(info, entries[info.filename])
    temporary.replace(path)
    return renames


def rename_sheet(path: Path, mapping: dict[str, str], write: bool) -> list[Rename]:
    if not path.is_file():
        raise FileNotFoundError(f"Sheet not found: {path}")
    if path.suffix.lower() in EXCEL_SUFFIXES:
        return rename_excel(path, mapping, write)
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Unsupported sheet type: {path}")
    return rename_csv(path, mapping, write)


def report(renames: list[Rename], mapping: dict[str, str], dry_run: bool) -> None:
    for path in dict.fromkeys(rename.path for rename in renames):
        print(f"\n{path}")
        for rename in (rename for rename in renames if rename.path == path):
            location = f"{rename.sheet}!" if rename.sheet else ""
            skipped = " skipped, that name already exists in this sheet"
            print(
                f"  {'! ' if rename.collision else ''}{location}row {rename.row}: "
                f"{rename.old} -> {rename.new}{skipped if rename.collision else ''}"
            )

    unused = sorted(set(mapping) - {rename.old for rename in renames})
    if unused:
        print("\nNot found in any sheet:")
        for name in unused:
            print(f"  {name}")

    applied = [rename for rename in renames if not rename.collision]
    files = len({rename.path for rename in applied})
    print(f"\n{'Would rename' if dry_run else 'Renamed'} {len(applied)} name(s) in {files} file(s).")


def main() -> int:
    arguments = parse_arguments()
    try:
        mapping = read_renames(arguments.renames)
        if not mapping:
            print("Rename list is empty.")
            return 0
        renames = [
            rename
            for path in arguments.targets
            for rename in rename_sheet(path, mapping, not arguments.dry_run)
        ]
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    report(renames, mapping, arguments.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
