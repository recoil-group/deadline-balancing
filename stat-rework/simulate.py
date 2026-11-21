"""Build simulation and validation for the reworked sheet.

    python stat-rework/simulate.py                # full report -> review/simulation_report.md
    python stat-rework/simulate.py --weapon M4A1  # one weapon, printed
    python stat-rework/simulate.py --sheet path   # evaluate a written sheet instead of generating

Builds per weapon:
    stock       the weapon's `defaults` build in Studio
    reference   official gun-game setups and the weapon's Studio presets
    archetypes  optimiser builds for handling, reload, stability, recoil and all-round play
    pure max    each of handling, reload_speed, stability maximised alone (clamping check)

The optimiser is a dynamic programme over the attachment tree. It ignores incompatibility rules
and lets each rail mount hold one item, adding the single best foregrip afterwards; the stats of
every build it returns are then evaluated exactly with the game's stacking rules. Its builds are
therefore always legal in stat terms but may occasionally be physically impossible, and it may
miss the true optimum by a little.
"""

import argparse
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import rules  # noqa: E402
from generate import Context, generate, stats_table  # noqa: E402
from families import family  # noqa: E402
from tree import NEW_STATS, read_sheet, sheet_stats  # noqa: E402

KEYS = NEW_STATS + ["weight", "horizontal_recoil", "vertical_recoil", "magazine_capacity", "bullet_velocity", "barrel_deviation"]

ARCHETYPES = {
    "handling": {"handling": 1.0, "reload_speed": 0.2, "stability": 0.2, "avg_recoil": -0.5, "weight": -2.0},
    "reload": {"handling": 0.2, "reload_speed": 1.0, "stability": 0.2, "avg_recoil": -0.5, "weight": -2.0},
    "stability": {"handling": 0.2, "reload_speed": 0.2, "stability": 1.0, "avg_recoil": -0.5, "weight": -2.0},
    "recoil": {"handling": 0.1, "reload_speed": 0.1, "stability": 0.1, "avg_recoil": -2.0, "weight": -1.0},
    "all_round": {"handling": rules.W_H, "reload_speed": rules.W_R, "stability": rules.W_S, "avg_recoil": -0.5, "weight": -3.0},
}
PURE = {s: {s: 1.0} for s in NEW_STATS}
PURE_MIN = {s + "_min": {s: -1.0} for s in NEW_STATS}


def item_score(st, name, obj, weight_only=False):
    s = st.get(name, {})
    v = obj.get("weight", 0.0) * s.get("weight", 0.0)
    if weight_only:
        return v
    for k in NEW_STATS:
        v += obj.get(k, 0.0) * s.get(k, 0.0)
    v += obj.get("avg_recoil", 0.0) * (s.get("horizontal_recoil", 0.0) + s.get("vertical_recoil", 0.0)) / 2
    return v


class Optimizer:
    def __init__(self, tree, st, weapon, obj):
        self.t, self.st, self.w, self.obj = tree, st, weapon, obj
        self.memo = {}
        self.busy = set()

    RAIL_FAMILIES = {"foregrip", "handguard"}

    def best(self, entries, nomuzzle=False, in_rail=False):
        key = (id(entries), nomuzzle, in_rail)
        if key in self.memo:
            return self.memo[key]
        if key in self.busy:
            return (0.0, [], [])
        self.busy.add(key)
        total, names, rails = 0.0, [], []
        for e in entries:
            if not e.get("class"):
                continue
            cands = self.t.candidates(e, self.w)
            is_rail = self.t.is_rail(e)
            if is_rail:
                if in_rail:
                    continue
                cands = [c for c in cands if family({"_class": self.t.att[c]["class"]}, self.t.att[c]) in self.RAIL_FAMILIES]
            required = bool(e.get("default")) and not is_rail
            opts = [] if required and cands else [(0.0, [], [])]
            for c in cands:
                a = self.t.att[c]
                if is_rail and "grip" in a["attach_type"]:
                    continue
                child = a["map"]
                sub_rail = in_rail or is_rail
                if a["is_muzzle_device"]:
                    if nomuzzle:
                        sc, nm, rl = self.best(child, True, sub_rail)
                        opts.append((item_score(self.st, c, self.obj, True) + sc, [c] + nm, rl))
                    else:
                        s1, n1, r1 = self.best(child, True, sub_rail)
                        s2, n2, r2 = self.best(child, False, sub_rail)
                        o1 = item_score(self.st, c, self.obj) + s1
                        o2 = item_score(self.st, c, self.obj, True) + s2
                        opts.append((o1, [c] + n1, r1) if o1 >= o2 else (o2, [c] + n2, r2))
                else:
                    sc, nm, rl = self.best(child, nomuzzle, sub_rail)
                    opts.append((item_score(self.st, c, self.obj) + sc, [c] + nm, rl))
            if not opts:
                continue
            sc, nm, rl = max(opts, key=lambda o: o[0])
            total += sc
            names += nm
            rails += rl + ([e] if is_rail else [])
        self.busy.discard(key)
        self.memo[key] = (total, names, rails)
        return self.memo[key]

    def run(self):
        _, names, rails = self.best(self.t.weapons[self.w]["map"])
        grips = set()
        for e in rails:
            for c in self.t.candidates(e, self.w):
                if "grip" in self.t.att[c]["attach_type"]:
                    grips.add(c)
        if grips:
            g = max(sorted(grips), key=lambda c: item_score(self.st, c, self.obj))
            if item_score(self.st, g, self.obj) > 0:
                names = names + [g]
        return names


def evaluate(tree, st, weapon, names):
    tot = tree.sum_stats(weapon, names, st, KEYS)
    tot["avg_recoil"] = (tot["horizontal_recoil"] + tot["vertical_recoil"]) / 2
    return tot


def weapon_builds(tree, st, weapon):
    builds = {"stock": [n for _, n in tree.stock_build(weapon)]}
    refs = {}
    for s in tree.setups:
        if s["weapon"] == weapon:
            refs["setup:" + s["name"]] = [n for _, n in tree.resolve(weapon, s["map"])]
    for pn, pm in tree.weapons[weapon]["presets"].items():
        names = [n for _, n in tree.resolve(weapon, pm)]
        if names not in refs.values():
            refs["preset:" + pn] = names
    opt = {}
    for k, obj in list(ARCHETYPES.items()) + list(PURE.items()) + list(PURE_MIN.items()):
        opt[k] = Optimizer(tree, st, weapon, obj).run()
    return builds, refs, opt


def dominance(ctx, st):
    """Within each competing set (non-rail slots and rail families), list strict dominations.

    Hidden capacity (Studio `mag_space` / `mag_space_add` flags on shotgun tubes) counts as a stat.
    Only like-for-like items are compared: both must host the same child slot classes, since an
    adapter that enables a different stock is not a worse version of a plain end plate.
    """
    found = []
    better_high = NEW_STATS + ["magazine_capacity", "bullet_velocity", "bullet_damage", "fire_rate"]
    better_low = ["weight", "horizontal_recoil", "vertical_recoil", "barrel_deviation", "muzzle_loudness"]
    for gid, g in ctx.groups.items():
        items = [n for n in g["items"] if n in st]
        if len(items) < 2:
            continue
        if g["rail"] and len(items) > 60:
            continue  # very broad rail families (all picatinny optics/mounts); compared by family review instead
        vec = {}
        kids = {n: tuple(sorted({m["class"] for m in ctx.tree.att.get(n, {}).get("map", []) if m.get("class")})) for n in items}
        for n in items:
            s = st[n]
            gfv = ctx.tree.att.get(n, {}).get("global_flag_values", {})
            hidden_capacity = gfv.get("mag_space", 0) + gfv.get("mag_space_add", 0)  # tube extensions
            vec[n] = [s.get(k, 0.0) for k in better_high] + [-s.get(k, 0.0) for k in better_low] + [hidden_capacity]
        for a in items:
            for b in items:
                if a == b or kids[a] != kids[b]:
                    continue  # items hosting different sub-assemblies are not like for like
                va, vb = vec[a], vec[b]
                if all(x >= y for x, y in zip(va, vb)) and any(x > y for x, y in zip(va, vb)):
                    pa, pb = st[a].get("price", 0.0), st[b].get("price", 0.0)
                    # a pure-cosmetic tie (all stats equal) is not a domination
                    found.append({"set": gid, "dominant": a, "dominated": b, "dominant_cheaper_or_equal": pa <= pb,
                                  "price_dominant": pa, "price_dominated": pb})
    return found


def write_dominations(ctx, st, hard, old_hard, write):
    """review/dominations.csv: every remaining strict domination, with a category."""
    import csv
    keys = NEW_STATS + ["horizontal_recoil", "vertical_recoil", "magazine_capacity", "bullet_velocity",
                        "bullet_damage", "barrel_deviation", "muzzle_loudness", "fire_rate"]
    in_old = {(d["dominant"], d["dominated"]) for d in old_hard}
    rows, seen = [], set()
    for d in hard:
        a, b = d["dominant"], d["dominated"]
        if (a, b) in seen:
            continue
        seen.add((a, b))
        diff = [k for k in keys if abs(st[a].get(k, 0) - st[b].get(k, 0)) > 1e-9]
        fam = ctx.items[b]["family"]
        if fam == "ammo":
            cat = "ammunition: rounds differ in calibers.csv (penetration, damage curve), not visible here"
        elif not diff:
            cat = "variant: identical stats, heavier (length or visual variant)"
        else:
            cat = "stat difference"
        rows.append({"family": fam, "set": d["set"], "dominant": a, "dominated": b, "category": cat,
                     "also_dominated_in_old_sheet": (a, b) in in_old, "differs_in": "+".join(diff),
                     "price_dominant": d["price_dominant"], "price_dominated": d["price_dominated"]})
    rows.sort(key=lambda r: (r["category"], r["family"], r["dominated"]))
    if write and rows:
        with open(os.path.join(HERE, "review", "dominations.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return rows


def fmt_build(tot):
    return (f"h{tot['handling']:6.1f} r{tot['reload_speed']:6.1f} s{tot['stability']:6.1f} "
            f"w{tot['weight']:5.2f} rec{tot['horizontal_recoil']:5.0f}/{tot['vertical_recoil']:<4.0f}")


def old_ergo_table():
    meta, header, rows = read_sheet(os.path.join(HERE, "data", "source_balancing.csv"))
    return sheet_stats(rows)


def report(weapons=None, write=True):
    ctx, out, log = generate()
    st = stats_table(ctx, out)
    old = old_ergo_table()
    t = ctx.tree
    lines = ["# Build simulation report", "",
             "Generated by `simulate.py` from the current rules and overrides. Stats are summed with the",
             "game's stacking rules. `old` is today's ergonomics of the same build.", ""]
    problems = defaultdict(list)
    summary = []
    for w in sorted(weapons or t.weapons):
        if w not in st:
            continue
        builds, refs, opt = weapon_builds(t, st, w)
        lines += [f"## {w}", "", "| build | handling | reload | stability | weight | recoil h/v | old ergo |", "|---|---|---|---|---|---|---|"]
        real = {}
        for name, names in list(builds.items()) + list(refs.items()):
            tot = evaluate(t, st, w, names)
            o = t.sum_stats(w, names, old, ["ergonomics"])["ergonomics"]
            real[name] = (tot, o)
            lines.append(f"| {name} | {tot['handling']:.1f} | {tot['reload_speed']:.1f} | {tot['stability']:.1f} | {tot['weight']:.2f} | {tot['horizontal_recoil']:.0f}/{tot['vertical_recoil']:.0f} | {o:.1f} |")
            for s in NEW_STATS:
                if tot[s] < 0 or tot[s] > 100:
                    problems["clamp_realistic"].append(f"{w} {name}: {s} {tot[s]:.1f}")
        opt_tot = {}
        for name, names in opt.items():
            tot = evaluate(t, st, w, names)
            o = t.sum_stats(w, names, old, ["ergonomics"])["ergonomics"]
            opt_tot[name] = (tot, names)
            lines.append(f"| opt:{name} | {tot['handling']:.1f} | {tot['reload_speed']:.1f} | {tot['stability']:.1f} | {tot['weight']:.2f} | {tot['horizontal_recoil']:.0f}/{tot['vertical_recoil']:.0f} | {o:.1f} |")
        lines.append("")
        # checks
        mx = {s: opt_tot[s][0][s] for s in NEW_STATS}
        mn = {s: opt_tot[s + "_min"][0][s] for s in NEW_STATS}
        for s in NEW_STATS:
            if mx[s] > 100:
                problems["clamp_max"].append(f"{w}: max {s} {mx[s]:.1f}")
            if mn[s] < 0:
                problems["clamp_min"].append(f"{w}: min {s} {mn[s]:.1f}")
        tri = []
        for name, (tot, _) in list(opt_tot.items()) + [(k, (v[0], None)) for k, v in real.items()]:
            if all(tot[s] >= mx[s] - 3 for s in NEW_STATS):
                tri.append(name)
        if tri:
            problems["maxes_all_three"].append(f"{w}: {', '.join(tri)} within 3 of every per-stat maximum ({mx})")
        arche = [k for k in ARCHETYPES]
        sets = {k: set(opt_tot[k][1]) for k in arche}
        ov = []
        for i, a in enumerate(["handling", "reload", "stability"]):
            for b in ["handling", "reload", "stability"][i + 1:]:
                u = sets[a] | sets[b]
                ov.append(len(sets[a] & sets[b]) / len(u) if u else 1)
        diff = 1 - max(ov)
        if diff < 0.10:
            problems["archetypes_same"].append(f"{w}: handling/reload/stability builds share {max(ov):.0%} of parts")
        refs_tot = [v[0] for k, v in real.items() if k != "stock"] or [real["stock"][0]]
        refs_old = [v[1] for k, v in real.items() if k != "stock"] or [real["stock"][1]]
        summary.append({
            "weapon": w, "n_ref": len(refs_tot),
            "stock": real["stock"][0],
            "ref_med": {s: statistics.median(x[s] for x in refs_tot) for s in NEW_STATS},
            "ref_old": statistics.median(refs_old),
            "max": mx, "min": mn, "archetype_overlap": max(ov),
        })
    dom = dominance(ctx, st)
    hard = [d for d in dom if d["dominant_cheaper_or_equal"]]
    old3 = {n: dict(v, **{k: v.get("ergonomics", 0.0) for k in NEW_STATS}) for n, v in old.items()}
    old_hard = [d for d in dominance(ctx, old3) if d["dominant_cheaper_or_equal"]]
    head = ["## Summary", "",
            "Median of reference builds (official setups + presets; stock if none) against today's ergonomics",
            "of the same builds, the stock build, and the per-stat range the optimiser finds.", "",
            "| weapon | refs | ref h | ref r | ref s | old ergo | stock h/r/s | max h/r/s | min h/r/s | archetype overlap |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for s in summary:
        r = s["ref_med"]
        head.append(f"| {s['weapon']} | {s['n_ref']} | {r['handling']:.0f} | {r['reload_speed']:.0f} | {r['stability']:.0f} | {s['ref_old']:.0f} | "
                    f"{s['stock']['handling']:.0f}/{s['stock']['reload_speed']:.0f}/{s['stock']['stability']:.0f} | "
                    f"{s['max']['handling']:.0f}/{s['max']['reload_speed']:.0f}/{s['max']['stability']:.0f} | "
                    f"{s['min']['handling']:.0f}/{s['min']['reload_speed']:.0f}/{s['min']['stability']:.0f} | {s['archetype_overlap']:.0%} |")
    head += ["", "## Checks", ""]
    names = {"clamp_realistic": "Realistic builds (stock, references) outside 0-100",
             "clamp_max": "Per-stat maximum above 100 (clamped in game)",
             "clamp_min": "Per-stat minimum below 0 (clamped in game)",
             "maxes_all_three": "A single build within 3 points of every per-stat maximum",
             "archetypes_same": "Handling, reload and stability builds nearly identical"}
    for k, title in names.items():
        head.append(f"### {title}: {len(problems[k])}")
        head += [f"- {p}" for p in problems[k]] or ["- none"]
        head.append("")
    n_items = len({d["dominated"] for d in hard})
    n_old = len({d["dominated"] for d in old_hard})
    head.append(f"### Strict dominations inside competing sets: {n_items} items dominated by a not-more-expensive like-for-like alternative (old sheet, with ergonomics in all three: {n_old})")
    head.append("")
    head.append("Compared on handling, reload, stability, capacity, velocity, damage, weight, recoil, deviation and loudness; items hosting different child slots are not compared.")
    seen = set()
    for d in sorted(hard, key=lambda d: (d["set"], d["dominant"])):
        k = (d["dominant"], d["dominated"])
        if k in seen:
            continue
        seen.add(k)
        head.append(f"- `{d['dominant']}` dominates `{d['dominated']}` in {d['set']} (price {d['price_dominant']:g} vs {d['price_dominated']:g})")
    head.append("")
    write_dominations(ctx, st, hard, old_hard, write)
    text = "\n".join(lines[:5] + head + lines[5:]) + "\n"
    if write:
        open(os.path.join(HERE, "review", "simulation_report.md"), "w").write(text)
    return summary, problems, hard, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weapon", nargs="*")
    a = ap.parse_args()
    summary, problems, hard, text = report(a.weapon, write=not a.weapon)
    if a.weapon:
        print(text)
    else:
        print(text[: text.index("\n## ", text.index("## Checks"))] if "## Checks" in text else text[:8000])


if __name__ == "__main__":
    main()
