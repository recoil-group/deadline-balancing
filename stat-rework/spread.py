"""How much handling and stability vary inside each competing set, against how much ergonomics did.

    python stat-rework/spread.py                    # summary per family, writes review/spread.csv
    python stat-rework/spread.py --sheet OTHER.csv  # the same for another sheet in the new layout

For every competing set with at least three items that carry a value (rail families capped at 60
items, as in the domination check), the spread is max - min over its items. Per family, the median
over sets of handling spread / ergonomics spread is the number to watch: 1 means handling varies as
much as ergonomics did.
"""

import argparse
import csv
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from generate import generate, stats_table  # noqa: E402
from tree import num, read_sheet  # noqa: E402


def sheet_values(path):
    _, _, rows = read_sheet(path)
    return {d["name"]: {k: num(d.get(k)) for k in ("handling", "stability")} for d in rows if d.get("name")}


def spreads(ctx, vals):
    out = []
    for gid, g in ctx.groups.items():
        items = [n for n in g["items"] if n in ctx.items and n in vals and ctx.items[n]["family"] != "weapon"]
        if len(items) < 3 or (g["rail"] and len(items) > 60):
            continue
        e = [ctx.items[n]["ergonomics"] for n in items]
        h = [vals[n]["handling"] or 0.0 for n in items]
        s = [vals[n]["stability"] or 0.0 for n in items]
        es = max(e) - min(e)
        if es <= 0 and max(h) == min(h):
            continue
        fams = defaultdict(int)
        for n in items:
            fams[ctx.items[n]["family"]] += 1
        out.append({"set": gid, "family": max(fams, key=fams.get), "n": len(items), "ergo_spread": es,
                    "handling_spread": max(h) - min(h), "stability_spread": max(s) - min(s)})
    return out


def summary(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)
    lines = []
    for fam in sorted(by):
        rs = [r for r in by[fam] if r["ergo_spread"] > 0]
        if not rs:
            continue
        ratio = statistics.median(r["handling_spread"] / r["ergo_spread"] for r in rs)
        worst = max(rs, key=lambda r: r["handling_spread"] / r["ergo_spread"])
        lines.append((fam, len(rs), ratio, statistics.median(r["handling_spread"] for r in rs),
                      statistics.median(r["ergo_spread"] for r in rs), worst["set"], worst["handling_spread"] / worst["ergo_spread"]))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    ctx, out, _ = generate()
    vals = sheet_values(a.sheet) if a.sheet else stats_table(ctx, out)
    rows = spreads(ctx, vals)
    if not a.sheet:
        with open(os.path.join(HERE, "review", "spread.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(sorted(rows, key=lambda r: (r["family"], r["set"])))
    print(f"{'family':12s} {'sets':>4s} {'median h/ergo':>13s} {'median h':>8s} {'median ergo':>11s}  widest set (ratio)")
    for fam, n, ratio, mh, me, ws, wr in summary(rows):
        print(f"{fam:12s} {n:4d} {ratio:13.2f} {mh:8.1f} {me:11.1f}  {ws[:50]} ({wr:.1f})")


if __name__ == "__main__":
    main()
