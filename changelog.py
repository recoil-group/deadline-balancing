import csv
import sys
from typing import Dict, List, Tuple

stat_directions = {
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
    "price": False,
}


def read_csv(file_path: str) -> Tuple[str, int, Dict[str, Dict[str, str]]]:
    data = {}
    with open(file_path, "r", newline="", encoding="utf-8-sig") as f:
        version = f.readline().split(",")[0]
        size = 0
        reader = csv.DictReader(f)
        for row in reader:
            if row["name"]:
                data[row["name"]] = row
                size += 1
    return version, size, data


def format_header(header: str) -> str:
    return " ".join(word.capitalize() for word in header.split("_"))


def compare_rows(
    row1: Dict[str, str], row2: Dict[str, str], compare_cols: List[str]
) -> List[str]:
    changes = []
    for key in compare_cols:
        if not row1:
            if row2.get(key):
                changes.append(f"{format_header(key)}: `{row2.get(key, '0')}`")
            continue

        old = row1.get(key, "0")
        new = row2.get(key, "0")

        if old == "":
            old = "0"
        if new == "":
            new = "0"

        if old != new:
            try:
                color = (
                    "green"
                    if (float(new) > float(old)) == stat_directions[key]
                    else "red"
                )
                changes.append(
                    f'{format_header(key)}: `{old}` -> <code class="{color}">{new}</code>'
                )
            except:
                changes.append(f"{format_header(key)}: `{old}` -> `{new}`")
    return changes


def main(file1: str, file2: str):
    _, _, data1 = read_csv(file1)
    version, size, data2 = read_csv(file2)

    compare_cols = list(next(iter(data1.values())).keys())[4:]

    new = []
    changes = []
    for name, row2 in data2.items():
        row_changes = []
        if name in data1:
            row_changes = compare_rows(data1[name], row2, compare_cols)
            if len(row_changes) > 0:
                pretty_name = row2.get("pretty_name") or row2["name"]
                changes.append(
                    f"### {pretty_name}\n\n" + " \\\n".join(row_changes) + "\n"
                )
        else:
            row_changes = compare_rows({}, row2, compare_cols)
            if len(row_changes) > 0:
                pretty_name = row2.get("pretty_name") or row2["name"]
                new.append(f"### {pretty_name}\n\n" + " \\\n".join(row_changes) + "\n")

    output_file = "changelogs/" + version.replace(".", "-") + ".md"
    with open(output_file, "w", encoding="utf-8-sig") as f:
        f.write(f"# {version} Balancing Changes\n\n")
        f.write(f"[Changed attachments](#changed-attachments): {len(changes)}\n\n")
        f.write(f"[New attachments](#new-attachments): {len(new)}\n\n")
        f.write(f"Total attachments: {size}\n\n")
        f.write(f"## Changed Attachments\n\n")
        f.write("\n".join(changes))
        f.write(f"\n## New Attachments\n\n")
        f.write("\n".join(new))

    print(f"Output written to {output_file}")


main(sys.argv[1], sys.argv[2])
