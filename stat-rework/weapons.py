"""Weapon base values: handling, reload_speed and stability on each weapon row.

Scheme (see RULES.md, "Weapon base values"):

    base = anchor + identity offset - median part contribution of the weapon's reference builds

    anchor     handling and reload_speed: today's median ergonomics of the weapon's reference builds
               (official gun-game setups and Studio presets; the stock build if it has none), so a
               typical build feels as it does today. stability: 50, today's feel. Contract v4 makes
               the ADS and reload ranges universal; for weapons whose place range differed, the
               anchor is converted so the typical build keeps today's ADS time and reload speed.
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


# Contract v4: one range for every weapon. A weapon whose place range differed has its anchor
# converted so its typical build keeps today's ADS time and reload playback speed exactly.
UNIVERSAL = {"ads": [0, 100, 0.8, 0.25], "reload": [0, 100, 0.9, 1.3]}


def _map(x, lo, hi, a, b, clamp=True):
    t = (x - lo) / (hi - lo)
    if clamp:
        t = min(1.0, max(0.0, t))
    return a + (b - a) * t


def convert(points, place, universal):
    """Old points on the weapon's place range -> points giving the same value on the universal range."""
    value = _map(points, *place)
    lo, hi, a, b = universal
    return lo + (value - a) / (b - a) * (hi - lo)


def reference_builds(tree, weapon):
    refs = []
    for s in tree.setups:
        if s["weapon"] == weapon:
            refs.append([n for _, n in tree.resolve(weapon, s["map"])])
    for _, pm in sorted(tree.weapons[weapon]["presets"].items()):
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
        converted = []
        ranges = t.weapons[name].get("place_ranges", {})
        for key, s in (("ads", "handling"), ("reload", "reload_speed")):
            place = ranges.get(key)
            if place and [float(x) for x in place] != [float(x) for x in UNIVERSAL[key]]:
                anchor[s] = convert(old_typ, place, UNIVERSAL[key])
                converted.append(f"{s} anchor {anchor[s]:.1f} (place {key} range {place[2]}-{place[3]} over {place[0]}-{place[1]} converted to the universal range)")
        for s, k in (("handling", "offset_h"), ("reload_speed", "offset_r"), ("stability", "offset_s")):
            a = float(r["anchor_" + s]) if r.get("anchor_" + s, "") != "" else anchor[s]
            row[s] = rules.round_half(a + float(r.get(k) or 0) - parts[s])
        row["anchor"] = f"typical old ergo {old_typ:.1f} over {len(refs)} reference builds" + ("; " + "; ".join(converted) if converted else "")
        row["note"] = r.get("note", "")
        rows.append(row)
    with open(BASES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "handling", "reload_speed", "stability", "anchor", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {BASES}")
    for row in rows:
        print(f"  {row['name']:16s} h{row['handling']!s:>6} r{row['reload_speed']!s:>6} s{row['stability']!s:>6}  {row['anchor']}")
