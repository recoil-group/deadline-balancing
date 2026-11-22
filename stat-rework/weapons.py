"""Weapon base values: handling, reload_time and stability on each weapon row.

Scheme (see RULES.md, "Weapon base values"):

    handling, stability:  base = anchor + identity offset - median part contribution
    reload_time:          1 + base = (1 + identity offset) / median over reference builds of
                                     (today's playback x (1 + part sum))

    anchor     handling: today's median ergonomics of the weapon's reference builds (official
               gun-game setups and Studio presets; the stock build if it has none), so a typical
               build aims as it does today. Contract v4 makes the ADS range universal; a weapon
               whose place range differed has its anchor converted to keep today's ADS time.
               stability: 50, today's feel.
    reload     contract v5: the weapon row is the base factor on the native animation length,
               duration = length x (1 + weapon row) x clamp(1 + sum of parts, 0.6, 1.6).
               Today's playback is the place's reload range at the same median old ergonomics,
               so a typical build reloads exactly as long as today (identity offsets aside).
    offset     weapon identity, from weapon_identity.csv (one note per weapon); offset_rt is a
               fraction of reload time.
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

import rounding  # noqa: E402

IDENTITY = os.path.join(HERE, "weapon_identity.csv")
BASES = os.path.join(HERE, "weapon_bases.csv")


# Contract v4: one ADS range for every weapon. A weapon whose place range differed has its anchor
# converted so its typical build keeps today's ADS time exactly. The reload default is the range
# count_stats uses when a weapon has no marker of its own.
UNIVERSAL = {"ads": [0, 100, 0.8, 0.25]}
DEFAULT_RELOAD = [0, 100, 0.9, 1.3]
STATS = ("handling", "reload_time", "stability")


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
            for s in STATS:
                row[s] = r.get("fixed_" + s, "")
            row["note"] = r.get("note", "")
            row["anchor"] = ""
            rows.append(row)
            continue
        refs = reference_builds(t, name)
        zero = {k: dict(v) for k, v in st.items()}
        zero[name] = {k: 0.0 for k in zero[name]}
        parts = {s: statistics.median(t.sum_stats(name, b, zero, [s])[s] for b in refs) for s in STATS}
        old_typ = statistics.median(t.sum_stats(name, b, old, ["ergonomics"])["ergonomics"] for b in refs)
        ranges = t.weapons[name].get("place_ranges", {})
        anchor = {"handling": old_typ, "stability": 50.0}
        notes = [f"typical old ergo {old_typ:.1f} over {len(refs)} reference builds"]
        place = ranges.get("ads")
        if place and [float(x) for x in place] != [float(x) for x in UNIVERSAL["ads"]]:
            anchor["handling"] = convert(old_typ, place, UNIVERSAL["ads"])
            notes.append(f"handling anchor {anchor['handling']:.1f} (place ads range {place[2]}-{place[3]} over {place[0]}-{place[1]} converted to the universal range)")
        for s, k in (("handling", "offset_h"), ("stability", "offset_s")):
            a = float(r["anchor_" + s]) if r.get("anchor_" + s, "") != "" else anchor[s]
            row[s] = rounding.round_int(a + float(r.get(k) or 0) - parts[s])  # round 8: whole points
        # reload: per reference build, today's playback times the new parts' time factor; the base
        # factor makes the median of these exactly today's duration (identity offset aside)
        reload_range = ranges.get("reload") or DEFAULT_RELOAD
        per_build = []
        for bld in refs:
            playback_b = _map(t.sum_stats(name, bld, old, ["ergonomics"])["ergonomics"], *reload_range)
            rt_b = t.sum_stats(name, bld, zero, ["reload_time"])["reload_time"]
            per_build.append(playback_b * min(1.6, max(0.6, 1 + rt_b)))
        factor = (1 + float(r.get("offset_rt") or 0)) / statistics.median(per_build)
        row["reload_time"] = round(factor - 1, 3) + 0.0
        playback = _map(old_typ, *reload_range)
        notes.append(f"today's reload playback {playback:.3f}x at the typical old ergo (place range {reload_range[2]}-{reload_range[3]} over "
                     f"{reload_range[0]}-{reload_range[1]}), median part reload_time {parts['reload_time']:+.3f}")
        row["anchor"] = "; ".join(notes)
        row["note"] = r.get("note", "")
        rows.append(row)
    with open(BASES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", *STATS, "anchor", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {BASES}")
    for row in rows:
        print(f"  {row['name']:16s} h{row['handling']!s:>6} rt{row['reload_time']!s:>7} s{row['stability']!s:>6}  {row['anchor']}")
