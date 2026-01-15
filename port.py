import sys
import csv
from datetime import datetime


def update_csv(changes, original, header_line=1):
    with open(changes, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        if header_line > 1:
            for i in range(header_line - 1):
                next(reader)
        c_headers = next(reader)
        c_name_idx = c_headers.index("name")
        data = {row[c_name_idx]: row for row in reader}

    with open(original, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        lines = list(reader)

    lines[0][1] = datetime.now().strftime("%a %b %d %H:%M:%S %Y")

    o_headers = lines[1]
    o_name_idx = o_headers.index("name")

    for i in range(2, len(lines)):
        if len(lines[i]) <= o_name_idx:
            continue
        name = lines[i][o_name_idx]
        if len(name) > 0 and name in data:
            changes_row = data[name]
            for j in range(0, len(c_headers)):
                if c_headers[j] in o_headers:
                    o_idx = o_headers.index(c_headers[j])
                    lines[i][o_idx] = changes_row[j]
            del data[name]

    for name in data:
        print(f"Warning: Name '{name}' from changes file not found in original file.")

    with open(original, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(lines)


update_csv(sys.argv[1], sys.argv[2], int(sys.argv[3]))
