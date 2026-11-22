"""Round 8: whole numbers by default in handling and stability.

Every part's handling and stability are rounded to whole points as the last step of the
generator. For each part the candidates are the integers just below and above each stat, and the
pair with the lowest cost wins: how far the part's value (EV, 0.60 h + 0.47 s) moves, plus half a
point of EV per point the furthest-moved stat travels, so the value is kept without pushing one
stat far from its own number (a cheek riser at 0.4 / 2.7 becomes 0 / 3, not 1 / 2). A tie goes to
the smaller total move, then to the pair nearer zero. An even part (h equal to s before
rounding) takes the same integer for both.

A half point stays only where whole numbers would misstate a competing set. Inside every
competing set, among like-for-like parts (parts that host the same child slots, as in the
domination check; on a rail, where every kind of accessory competes, also the same family and
profile, so a red dot is not held apart from a mount):

- no reversal: a part that is ahead of another on handling or stability before rounding is not
  behind it after;
- no new difference: two parts equal on a stat before rounding stay equal on it;
- no new tie: two parts that differed at half-point precision do not become identical (handling,
  reload_time and stability all equal).

A part in such a conflict first tries its other whole-number pair, if that pair keeps its value
within ALT_LIMIT EV; otherwise it keeps half points (the nearest half-point pair that resolves the
conflict, else plain half rounding, which can never reverse an order). review/half_points.csv
lists every half value that remains, with the part it is separated from.

Weapon base rows are rounded to whole points in weapons.py (they compete with nothing).
"""

import math
from collections import defaultdict
from itertools import product

import profiles

W_H, W_S = 0.60, 0.47
EPS = 1e-6
MOVE_COST = 0.5  # EV per point the furthest-moved stat travels: keeps value without pushing a stat far from its own number
ALT_LIMIT = 0.55  # EV; about what rounding both stats to the nearest whole point can cost anyway


def round_int(x):
    """Nearest integer, ties away from zero."""
    y = math.floor(abs(x) + 0.5)
    return math.copysign(y, x) if y else 0.0


def round_half(x):
    y = math.floor(abs(x) * 2 + 0.5) / 2
    return math.copysign(y, x) if y else 0.0


def _ev(h, s):
    return W_H * h + W_S * s


def _near(x, step):
    lo = math.floor(x / step + EPS) * step
    hi = math.ceil(x / step - EPS) * step
    return sorted({lo + 0.0, hi + 0.0})


def candidates(h, s, step):
    """Grid pairs around (h, s), best first."""
    if abs(h - s) < EPS:
        pairs = [(a, a) for a in _near(h, step)]
    else:
        pairs = list(product(_near(h, step), _near(s, step)))
    target = _ev(h, s)
    return sorted(pairs, key=lambda p: (round(abs(_ev(*p) - target) + MOVE_COST * max(abs(p[0] - h), abs(p[1] - s)), 9),
                                        round(abs(p[0] - h) + abs(p[1] - s), 9), abs(p[0]) + abs(p[1]), p))


def apply(ctx, out):
    """Round handling and stability of every part in `out` in place. Returns {name: note}."""
    raw = {}
    for n, v in out.items():
        it = ctx.items[n]
        if it["family"] == "weapon" or v.get("handling") is None or v.get("stability") is None:
            continue
        raw[n] = (v["handling"], v["stability"])
    half = {n: (round_half(h), round_half(s)) for n, (h, s) in raw.items()}
    rt = {n: round(out[n].get("reload_time") or 0.0, 3) for n in raw}
    cur = {n: candidates(h, s, 1.0)[0] for n, (h, s) in raw.items()}
    mode = {n: "whole" for n in raw}

    pairs = set()
    neigh = defaultdict(set)
    for g in ctx.groups.values():
        by_fam = defaultdict(list)
        for n in g["items"]:
            if n in raw:
                by_fam[_kind(ctx, n, g["rail"])].append(n)
        for ns in by_fam.values():
            ns = sorted(set(ns))
            for i, a in enumerate(ns):
                for b in ns[i + 1:]:
                    pairs.add((a, b))
                    neigh[a].add(b)
                    neigh[b].add(a)

    def conflict(a, b, va, vb):
        """Why va (for a) and vb (for b) misstate the pair, or None."""
        for k, stat in ((0, "handling"), (1, "stability")):
            xa, xb = raw[a][k], raw[b][k]
            if xa > xb + EPS and va[k] < vb[k] - EPS:
                return f"keeps {stat} ahead of {b}"
            if xb > xa + EPS and vb[k] < va[k] - EPS:
                return f"keeps {stat} behind {b}"
            if abs(xa - xb) <= EPS and abs(va[k] - vb[k]) > EPS:
                return f"keeps {stat} equal to {b}"
        if va == vb and rt[a] == rt[b] and half[a] != half[b]:
            return f"stays distinct from {b} ({_fmt(half[a])} vs {_fmt(half[b])} at half points)"
        return None

    def conflicts_of(n, v):
        return [(m, c) for m in sorted(neigh[n]) if (c := conflict(n, m, v, cur[m]))]

    note = {}
    for _ in range(100):
        bad = [(a, b) for a, b in sorted(pairs) if conflict(a, b, cur[a], cur[b])]
        if not bad:
            break
        done = set()
        for a, b in bad:
            if a in done or b in done or not conflict(a, b, cur[a], cur[b]):
                continue
            # move the part that strayed further from its own value, or the one that is not whole at half points
            def stray(n):
                return (any(x % 1 for x in half[n]), abs(cur[n][0] - raw[n][0]) + abs(cur[n][1] - raw[n][1]))
            n = max((a, b), key=lambda x: (mode[x] != "fixed", stray(x), x))
            if mode[n] == "fixed":
                n = a if n == b else b
            other = b if n == a else a
            why = conflict(n, other, cur[n], cur[other])
            done.add(n)
            target = _ev(*raw[n])
            if mode[n] == "whole":
                alt = [p for p in candidates(*raw[n], 1.0)[1:]
                       if abs(_ev(*p) - target) <= ALT_LIMIT + EPS and not conflicts_of(n, p)]
                if alt:
                    cur[n] = alt[0]
                    note[n] = "other whole pair: " + why
                    continue
            ok = [p for p in candidates(*raw[n], 0.5) if not conflicts_of(n, p)]
            cur[n] = ok[0] if ok else half[n]
            mode[n] = "half" if ok else "fixed"
            note[n] = "half point kept: " + why
    for n, (h, s) in cur.items():
        out[n]["handling"], out[n]["stability"] = h, s
    return {n: t for n, t in note.items() if any(x % 1 for x in cur[n]) or t.startswith("other")}


def _kind(ctx, n, rail):
    """Like-for-like key inside a set, as in the domination check: parts that host the same child
    slots; on a rail, where every kind of accessory competes, also the same family and profile."""
    kids = tuple(sorted({m["class"] for m in ctx.tree.att.get(n, {}).get("map", []) if m.get("class")}))
    if rail:
        return (ctx.items[n]["family"], profiles.profile_of(ctx.items[n]), kids)
    return kids


def _fmt(p):
    return "/".join(f"{x:g}" for x in p)


def round_reload_part(raw_rt, siblings):
    """Whole percent for a part's reload_time, half percent where a neighbour in the same set that
    differs from it by at least half a percent would round to the same whole percent."""
    whole = round_int(raw_rt * 100) / 100
    for o in siblings:
        if abs(o - raw_rt) >= 0.005 - EPS and round_int(o * 100) / 100 == whole:
            return round_half(raw_rt * 100) / 100
    return whole
