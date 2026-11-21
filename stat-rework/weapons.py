"""Weapon base values: handling, reload_speed and stability on each weapon row.

Scheme (see RULES.md, "Weapon base values"):

    base = anchor + identity offset - median part contribution of the weapon's reference builds

    anchor     handling and reload_speed: today's median ergonomics of the weapon's reference builds
               (official gun-game setups and Studio presets; the stock build if it has none), so a
               typical build feels as it does today. stability: 50, today's feel.
    offset     weapon identity, from weapon_identity.csv (one note per weapon).
    parts      the median over reference builds of what the re-statted parts add.

`python generate.py --calibrate` rewrites weapon_bases.csv from weapon_identity.csv and the current
part rules. Run it after part rules change, then regenerate. Weapons with no Studio data (Glock 20)
and non-firearm rows keep their identity row values directly.
"""

import csv
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

IDENTITY = os.path.join(HERE, "weapon_identity.csv")
BASES = os.path.join(HERE, "weapon_bases.csv")


def reference_builds(tree, weapon):
    refs = []
    for s in tree.setups:
        if s["weapon"] == weapon:
            refs.append([n for _, n in tree.resolve(weapon, s["map"])])
    for pm in tree.weapons[weapon]["presets"].values():
        b = [n for _, n in tree.resolve(weapon, pm)]
        if b not in refs:
            refs.append(b)
    return refs or [[n for _, n in tree.stock_build(weapon)]]


def calibrate():
    from generate import Context, generate, stats_table
    from simulate import old_ergo_table
    import rules

    ident = {r["name"]: r for r in csv.DictReader(open(IDENTITY, encoding="utf-8-sig"))}
    ctx, out, _ = generate()
    st = stats_table(ctx, out)
    old = old_ergo_table()
    t = ctx.tree
    rows = []
    for name, r in ident.items():
        row = {"name": name}
        if name not in t.weapons:
            for s in ("handling", "reload_speed", "stability"):
                row[s] = r.get("fixed_" + s, "")
            row["note"] = r.get("note", "")
            row["anchor"] = ""
            rows.append(row)
            continue
        refs = reference_builds(t, name)
        zero = {k: dict(v) for k, v in st.items()}
        zero[name] = {k: 0.0 for k in zero[name]}
        parts = {s: statistics.median(t.sum_stats(name, b, zero, [s])[s] for b in refs) for s in ("handling", "reload_speed", "stability")}
        old_typ = statistics.median(t.sum_stats(name, b, old, ["ergonomics"])["ergonomics"] for b in refs)
        anchor = {"handling": old_typ, "reload_speed": old_typ, "stability": 50.0}
        for s, k in (("handling", "offset_h"), ("reload_speed", "offset_r"), ("stability", "offset_s")):
            a = float(r["anchor_" + s]) if r.get("anchor_" + s, "") != "" else anchor[s]
            row[s] = rules.round_half(a + float(r.get(k) or 0) - parts[s])
        row["anchor"] = f"typical old ergo {old_typ:.1f} over {len(refs)} reference builds"
        row["note"] = r.get("note", "")
        rows.append(row)
    with open(BASES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "handling", "reload_speed", "stability", "anchor", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {BASES}")
    for row in rows:
        print(f"  {row['name']:16s} h{row['handling']!s:>6} r{row['reload_speed']!s:>6} s{row['stability']!s:>6}  {row['anchor']}")
