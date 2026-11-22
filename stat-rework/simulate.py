"""Build simulation and validation for the reworked sheet.

    python stat-rework/simulate.py                # full report -> review/simulation_report.md
    python stat-rework/simulate.py --weapon M4A1  # one weapon, printed
    python stat-rework/simulate.py --sheet path   # evaluate a written sheet instead of generating

Builds per weapon:
    stock       the weapon's `defaults` build in Studio
    reference   official gun-game setups and the weapon's Studio presets
    archetypes  optimiser builds for handling, reload, stability, recoil and all-round play
    pure max    each of handling, reload_time, stability at its best alone (clamping check)

Reload (contract v5) is reported as the parts' sum of reload_time, the percent of the weapon's base
reload time the parts add (lower is better), clamped in game to -40%..+60%. The weapon row's own
reload_time is the base factor; `vs today` compares a build's reload duration with today's
duration of the same build (today's playback from its old ergonomics on the place reload range).
Nothing is in seconds: animation lengths are not in the data. In objectives and gaps, 1% of reload
time counts as 2.75 points (RT_POINTS per unit of reload_time).

The optimiser is a dynamic programme over the attachment tree. It does not respect incompatibility
rules while searching (each finished build is checked against the item-level rules afterwards and
marked), and it lets each rail mount hold one item, adding the single best foregrip afterwards; the stats of
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

RT_POINTS = 275.0   # points of reload per unit of reload_time (1% of time ~ 2.75 points)
RT_CLAMP = (-0.4, 0.6)  # count_stats clamps 1 + sum of parts to 0.6..1.6
KEYS = NEW_STATS + ["fire_rate", "weight", "horizontal_recoil", "vertical_recoil", "magazine_capacity", "bullet_velocity", "barrel_deviation"]


def _obj(h, r, s, recoil, weight):
    """Objective with reload weighted in points (r) and applied to reload_time (lower is better)."""
    return {"handling": h, "reload_time": -RT_POINTS * r, "stability": s, "avg_recoil": recoil, "weight": weight}


ARCHETYPES = {
    "handling": _obj(1.0, 0.2, 0.2, -0.5, -2.0),
    "reload": _obj(0.2, 1.0, 0.2, -0.5, -2.0),
    "stability": _obj(0.2, 0.2, 1.0, -0.5, -2.0),
    "recoil": _obj(0.1, 0.1, 0.1, -2.0, -1.0),
    "all_round": _obj(rules.W_H, rules.W_R, rules.W_S, -0.5, -3.0),
}
SIGN = {"handling": 1.0, "reload_time": -1.0, "stability": 1.0}   # +1: higher is better
PURE = {s: {s: SIGN[s]} for s in NEW_STATS}          # each stat at its best
PURE_MIN = {s + "_min": {s: -SIGN[s]} for s in NEW_STATS}  # each stat at its worst


def points(stat, x):
    """A stat total on the 0-100 points scale used by the gaps: reload_time sum -> points."""
    return -RT_POINTS * x if stat == "reload_time" else x


def clamp_pts(stat, x):
    """Game clamp in points: 0-100 for handling and stability, -40%..+60% of time for reload."""
    if stat == "reload_time":
        return points(stat, min(max(x, RT_CLAMP[0]), RT_CLAMP[1]))
    return min(max(x, 0.0), 100.0)


def pct(x):
    return f"{x * 100:+.1f}%" if abs(x) >= 0.0005 else "0%"


CLAMPED_MARGIN = 10.0
BLEND_WEIGHTS = sorted({(a / m, b / m, c / m) for a in (1, 2, 3) for b in (1, 2, 3) for c in (1, 2, 3)
                        for m in [max(a, b, c)]})


def blend_builds(tree, st, weapon):
    """Builds maximising blends of the three stats, to search for one build near every ceiling."""
    out = []
    for a, b, c in BLEND_WEIGHTS:
        obj = _obj(a, b, c, 0.0, 0.0)
        out.append(((a, b, c), Optimizer(tree, st, weapon, obj).run()))
    return out


def item_score(st, name, obj, weight_only=False):
    s = st.get(name, {})
    v = obj.get("weight", 0.0) * s.get("weight", 0.0)
    if weight_only:
        return v
    for k in NEW_STATS + ["fire_rate"]:
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
    tot["reload_time"] -= st.get(weapon, {}).get("reload_time", 0.0)  # the weapon row is the base factor, not a part
    tot["avg_recoil"] = (tot["horizontal_recoil"] + tot["vertical_recoil"]) / 2
    return tot


def weapon_builds(tree, st, weapon):
    builds = {"stock": [n for _, n in tree.stock_build(weapon)]}
    refs = {}
    for s in tree.setups:
        if s["weapon"] == weapon:
            refs["setup:" + s["name"]] = [n for _, n in tree.resolve(weapon, s["map"])]
    for pn, pm in sorted(tree.weapons[weapon]["presets"].items()):
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
    better_high = ["handling", "stability", "magazine_capacity", "bullet_velocity", "bullet_damage", "fire_rate"]
    better_low = ["reload_time", "weight", "horizontal_recoil", "vertical_recoil", "barrel_deviation", "muzzle_loudness"]
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
    for d in sorted(hard, key=lambda d: (d["dominant"], d["dominated"], d["set"])):
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
    rows.sort(key=lambda r: (r["category"], r["family"], r["dominated"], r["dominant"]))
    if write and rows:
        with open(os.path.join(HERE, "review", "dominations.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return rows


def fmt_build(tot):
    return (f"h{tot['handling']:6.1f} rt{pct(tot['reload_time']):>7s} s{tot['stability']:6.1f} "
            f"w{tot['weight']:5.2f} rec{tot['horizontal_recoil']:5.0f}/{tot['vertical_recoil']:<4.0f}")


def old_ergo_table():
    meta, header, rows = read_sheet(os.path.join(HERE, "data", "source_balancing.csv"))
    return sheet_stats(rows)


def vs_today(tree, st, weapon, tot, old_ergo):
    """This build's reload duration against today's duration of the same build, in percent."""
    lo, hi, a, b = tree.weapons[weapon].get("place_ranges", {}).get("reload") or [0, 100, 0.9, 1.3]
    t = min(1.0, max(0.0, (old_ergo - lo) / (hi - lo)))
    today = 1 / (a + (b - a) * t)
    rt = min(max(tot["reload_time"], RT_CLAMP[0]), RT_CLAMP[1])
    now = (1 + st[weapon].get("reload_time", 0.0)) * (1 + rt)
    return now / today - 1


def cycling_report(t, st, weapons=None):
    """RPM range of the manually cycled weapons (cycling.py): stock, references, fastest, slowest."""
    import cycling

    lines = ["### Cycling on manually cycled weapons (fire_rate, round 6)", "",
             "| weapon | base RPM | stock | references | fastest legal build | slowest legal build |", "|---|---|---|---|---|---|"]
    for w, base in cycling.BASE_RPM.items():
        if w not in t.weapons or (weapons and w not in weapons):
            continue
        _, refs, _ = weapon_builds(t, st, w)
        rpm = lambda names: base * (1 + t.sum_stats(w, names, st, ["fire_rate"])["fire_rate"])
        stock = rpm([n for _, n in t.stock_build(w)])
        ref = sorted({round(rpm(b), 1) for b in refs.values()})
        ext = []
        for sign in (1.0, -1.0):
            names = Optimizer(t, st, w, {"fire_rate": sign}).run()
            ext.append(f"{rpm(names):.1f}" + (" (illegal)" if t.violations(w, names) else ""))
        lines.append(f"| {w} | {base} | {stock:.1f} | {', '.join(f'{x:g}' for x in ref) or '-'} | {ext[0]} | {ext[1]} |")
    return lines + [""]


def report(weapons=None, write=True):
    ctx, out, log = generate()
    st = stats_table(ctx, out)
    old = old_ergo_table()
    t = ctx.tree
    lines = ["# Build simulation report", "",
             "Generated by `simulate.py` from the current rules and overrides. Stats are summed with the",
             "game's stacking rules. `old` is today's ergonomics of the same build. Reload is the parts'",
             "reload_time sum (percent of the weapon's base reload time, lower is better); `vs today` is the",
             "build's reload duration against today's duration of the same build.", ""]
    problems = defaultdict(list)
    summary = []
    illegal_counts = {"opt": 0, "illegal": 0}
    for w in sorted(weapons or t.weapons):
        if w not in st:
            continue
        builds, refs, opt = weapon_builds(t, st, w)
        lines += [f"## {w}", "", f"Base reload factor (weapon row): {pct(st[w]['reload_time'])}.", "",
                  "| build | handling | reload (parts) | reload vs today | stability | weight | recoil h/v | old ergo |",
                  "|---|---|---|---|---|---|---|---|"]
        real = {}
        for name, names in list(builds.items()) + list(refs.items()):
            tot = evaluate(t, st, w, names)
            o = t.sum_stats(w, names, old, ["ergonomics"])["ergonomics"]
            real[name] = (tot, o)
            tot["vs_today"] = vs_today(t, st, w, tot, o)
            lines.append(f"| {name} | {tot['handling']:.1f} | {pct(tot['reload_time'])} | {pct(tot['vs_today'])} | {tot['stability']:.1f} | {tot['weight']:.2f} | {tot['horizontal_recoil']:.0f}/{tot['vertical_recoil']:.0f} | {o:.1f} |")
            for s in NEW_STATS:
                if s == "reload_time":
                    if not RT_CLAMP[0] <= tot[s] <= RT_CLAMP[1]:
                        problems["clamp_realistic"].append(f"{w} {name}: reload parts {pct(tot[s])}")
                elif tot[s] < 0 or tot[s] > 100:
                    problems["clamp_realistic"].append(f"{w} {name}: {s} {tot[s]:.1f}")
        opt_tot = {}
        for name, names in opt.items():
            tot = evaluate(t, st, w, names)
            o = t.sum_stats(w, names, old, ["ergonomics"])["ergonomics"]
            opt_tot[name] = (tot, names)
            bad = t.violations(w, names)
            illegal_counts["opt"] += 1
            if bad:
                illegal_counts["illegal"] += 1
            tag = f" (breaks {len(bad)} incompatibility rule{'s' if len(bad) > 1 else ''})" if bad else ""
            tot["vs_today"] = vs_today(t, st, w, tot, o)
            lines.append(f"| opt:{name}{tag} | {tot['handling']:.1f} | {pct(tot['reload_time'])} | {pct(tot['vs_today'])} | {tot['stability']:.1f} | {tot['weight']:.2f} | {tot['horizontal_recoil']:.0f}/{tot['vertical_recoil']:.0f} | {o:.1f} |")
        lines.append("")
        # checks; best and worst per stat (for reload_time, best is the lowest)
        mx = {s: opt_tot[s][0][s] for s in NEW_STATS}
        mn = {s: opt_tot[s + "_min"][0][s] for s in NEW_STATS}
        for s in ("handling", "stability"):
            if mx[s] > 100:
                problems["clamp_max"].append(f"{w}: max {s} {mx[s]:.1f}")
            if mn[s] < 0:
                problems["clamp_min"].append(f"{w}: min {s} {mn[s]:.1f}")
        if mx["reload_time"] < RT_CLAMP[0]:
            problems["clamp_max"].append(f"{w}: fastest reload parts {pct(mx['reload_time'])}")
        if mn["reload_time"] > RT_CLAMP[1]:
            problems["clamp_min"].append(f"{w}: slowest reload parts {pct(mn['reload_time'])}")
        tri = []
        for name, (tot, _) in list(opt_tot.items()) + [(k, (v[0], None)) for k, v in real.items()]:
            if all(points(s, tot[s]) >= points(s, mx[s]) - 3 for s in NEW_STATS):
                tri.append(name)
        if tri:
            problems["maxes_all_three"].append(
                f"{w}: {', '.join(tri)} within 3 points of every per-stat best "
                f"(h {mx['handling']:.1f} / reload {pct(mx['reload_time'])} / s {mx['stability']:.1f})")
        # clamp-aware: effects read clamped stats, so judge against the clamped best. Handling and
        # stability are 0-100 stats; reload is judged against the best its parts reach on this weapon
        # (and the -40% clamp), in points (1% of time = 2.75).
        candidates = list(opt_tot.items()) + [(k, (v[0], None)) for k, v in real.items()]
        candidates += [(f"blend {a:g}/{b:g}/{c:g}", (evaluate(t, st, w, names_), names_))
                       for (a, b, c), names_ in blend_builds(t, st, w)]
        # only legal builds count, for the maxima as well as for the build judged against them
        candidates = [(n_, v_) for n_, v_ in candidates if v_[1] is None or not t.violations(w, v_[1])]
        cmx = {k: max(clamp_pts(k, v_[0][k]) for _, v_ in candidates) for k in NEW_STATS}
        best_name, best_gap = None, 1e9
        for name, (tot, names_) in candidates:
            gap = max(cmx[k] - clamp_pts(k, tot[k]) for k in NEW_STATS)
            if gap < best_gap:
                best_name, best_gap = name, gap
        all_cmx = {k: clamp_pts(k, mx[k]) for k in NEW_STATS}
        short = [k for k in NEW_STATS if cmx[k] < all_cmx[k] - CLAMPED_MARGIN]

        def ceil(c):
            return f"h {c['handling']:.0f} / reload {pct(-c['reload_time'] / RT_POINTS)} / s {c['stability']:.0f}"
        if best_gap <= CLAMPED_MARGIN and short:
            problems["maxes_all_three_inconclusive"].append(
                f"{w}: `{best_name}` is within {best_gap:.1f} of the legal maxima, but the optimiser found no legal "
                f"build near the {', '.join(short)} ceiling (legal {ceil(cmx)} against {ceil(all_cmx)} including illegal builds)")
        elif best_gap <= CLAMPED_MARGIN:
            problems["maxes_all_three_clamped"].append(
                f"{w}: `{best_name}` is within {best_gap:.1f} of every clamped per-stat maximum "
                f"({ceil(cmx)})")
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
            "ref_med": {s: statistics.median(x[s] for x in refs_tot) for s in NEW_STATS + ["vs_today"]},
            "ref_old": statistics.median(refs_old),
            "max": mx, "min": mn, "archetype_overlap": max(ov), "choice_margin": best_gap,
        })
    cycling_lines = cycling_report(t, st, weapons)
    dom = dominance(ctx, st)
    hard = [d for d in dom if d["dominant_cheaper_or_equal"]]
    old3 = {n: dict(v, **{k: v.get("ergonomics", 0.0) * (-1 / RT_POINTS if k == "reload_time" else 1) for k in NEW_STATS})
            for n, v in old.items()}
    old_hard = [d for d in dominance(ctx, old3) if d["dominant_cheaper_or_equal"]]
    head = ["## Summary", "",
            "Median of reference builds (official setups + presets; stock if none) against today's ergonomics",
            "of the same builds, the stock build, and the per-stat range the optimiser finds (best and worst;",
            "reload as the parts' percent of base reload time, lower is better). `ref vs today`: the median",
            "reference build's reload duration against today's. Choice margin: over every build tried, the",
            "smallest worst-stat gap to the clamped per-stat bests, in points (reload: 1% of time = 2.75);",
            "the larger, the more a build has to give up one stat to reach another (flagged at 10 or less).", "",
            "| weapon | refs | ref h | ref reload | ref vs today | ref s | old ergo | stock h/reload/s | best h/reload/s | worst h/reload/s | archetype overlap | choice margin |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in summary:
        r = s["ref_med"]
        head.append(f"| {s['weapon']} | {s['n_ref']} | {r['handling']:.0f} | {pct(r['reload_time'])} | {pct(r['vs_today'])} | {r['stability']:.0f} | {s['ref_old']:.0f} | "
                    f"{s['stock']['handling']:.0f}/{pct(s['stock']['reload_time'])}/{s['stock']['stability']:.0f} | "
                    f"{s['max']['handling']:.0f}/{pct(s['max']['reload_time'])}/{s['max']['stability']:.0f} | "
                    f"{s['min']['handling']:.0f}/{pct(s['min']['reload_time'])}/{s['min']['stability']:.0f} | {s['archetype_overlap']:.0%} | {s['choice_margin']:.1f} |")
    head += ["", "## Checks", "",
             f"Optimiser builds that break an item-level incompatibility rule: {illegal_counts['illegal']} of "
             f"{illegal_counts['opt']} (marked in the weapon tables; the clamped check below uses legal builds "
             "only, for its maxima too). Slot-level `incompatible_with_when_mounted` rules are not checked.", ""]
    names = {"clamp_realistic": "Realistic builds (stock, references) outside the clamp (handling and stability 0-100, reload parts -40%..+60%)",
             "clamp_max": "Per-stat best past the clamp (handling or stability above 100, reload parts below -40%)",
             "clamp_min": "Per-stat worst past the clamp (handling or stability below 0, reload parts above +60%)",
             "maxes_all_three": "A single build within 3 points of every per-stat best",
             "maxes_all_three_clamped": "A single legal build within 10 points of every clamped per-stat best (handling and stability: min(max over legal builds, 100); reload: the fastest legal parts sum on that weapon)",
             "maxes_all_three_inconclusive": "Inconclusive: near every legal maximum, but the legal maxima fall well short of the optimiser's (illegal) ones",
             "archetypes_same": "Handling, reload and stability builds nearly identical"}
    for k, title in names.items():
        head.append(f"### {title}: {len(problems[k])}")
        head += [f"- {p}" for p in problems[k]] or ["- none"]
        head.append("")
    head += cycling_lines
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
