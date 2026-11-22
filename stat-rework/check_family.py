"""Check one family's re-statted values against the rules. Writes nothing.

    python stat-rework/check_family.py magazine [mag_control ...]

Reports, for the given families:
  - EV drift: items whose EV moved more than max(2, 25%) from their (weight-credited) old ergonomics
  - strict dominations inside competing sets (dominant not more expensive), deduplicated by pair
  - items best in their set on all three new stats
  - per-set spread of each stat
"""

import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import rules  # noqa: E402
from generate import generate, stats_table  # noqa: E402
from simulate import dominance  # noqa: E402
from tree import NEW_STATS  # noqa: E402


def pts(st, n, k):
    """Higher is better on every stat: reload_time in points (1% of time = 2.75)."""
    return -275.0 * st[n][k] if k == "reload_time" else st[n][k]


def main(fams):
    ctx, out, _ = generate()
    st = stats_table(ctx, out)
    mine = {n for n, it in ctx.items.items() if it["family"] in fams}
    print(f"{len(mine)} items in {', '.join(fams)}\n")

    print("== EV drift beyond max(2, 25%) of weight-credited old ergonomics")
    n_drift = 0
    for n in sorted(mine):
        it = ctx.items[n]
        credit = rules.DEFAULT_VECTORS.get(it["family"], rules.DEFAULT_VECTORS["misc"])[3]
        e = rules.adjusted_ergo(it, credit, ctx)
        h, r, s = (st[n][k] for k in NEW_STATS)
        v = rules.ev(h, r, s)
        if abs(v - e) > max(2.0, 0.25 * abs(e)):
            n_drift += 1
            print(f"  {n[:60]:60s} E{it['ergonomics']:+5.1f} adj{e:+5.1f} -> h{h:+5.1f} rt{r * 100:+5.1f}% s{s:+5.1f} EV{v:+6.1f}  {out[n]['_note'][:50]}")
    print(f"  {n_drift} items\n")

    print("== strict dominations (dominant not more expensive), by pair")
    pairs = {}
    for d in dominance(ctx, st):
        if d["dominant_cheaper_or_equal"] and (d["dominant"] in mine or d["dominated"] in mine):
            pairs.setdefault((d["dominant"], d["dominated"]), d["set"])
    for (a, b), g in sorted(pairs.items()):
        sa, sb = st[a], st[b]
        print(f"  {a[:42]:42s} > {b[:42]:42s} [{g[:40]}]  "
              f"h{sa['handling']:+.1f}/{sb['handling']:+.1f} rt{sa['reload_time'] * 100:+.1f}%/{sb['reload_time'] * 100:+.1f}% "
              f"s{sa['stability']:+.1f}/{sb['stability']:+.1f} w{sa['weight']:.2f}/{sb['weight']:.2f}")
    print(f"  {len(pairs)} pairs, {len({b for a, b in pairs})} dominated items\n")

    print("== best in set on all three new stats (sets of 3+ with some spread)")
    for gid, g in sorted(ctx.groups.items()):
        items = [n for n in g["items"] if n in st and n in mine]
        if len(items) < 3:
            continue
        best = {k: max(pts(st, n, k) for n in items) for k in NEW_STATS}
        spread = {k: best[k] - min(pts(st, n, k) for n in items) for k in NEW_STATS}
        for n in items:
            if all(pts(st, n, k) >= best[k] for k in NEW_STATS) and sum(spread.values()) > 0:
                print(f"  {n} in {gid} ({len(items)} items)")
    print()

    print("== per-set spread (sets of 3+)")
    for gid, g in sorted(ctx.groups.items(), key=lambda kv: -len(kv[1]["items"])):
        items = [n for n in g["items"] if n in st and n in mine]
        if len(items) < 3:
            continue
        rng = {k: (min(st[n][k] for n in items), max(st[n][k] for n in items)) for k in NEW_STATS}
        print(f"  {gid[:60]:60s} n{len(items):3d}  " + "  ".join(
            f"rt {lo * 100:+.1f}%..{hi * 100:+.1f}%" if k == "reload_time" else f"{k[:1]} {lo:+.1f}..{hi:+.1f}"
            for k, (lo, hi) in rng.items()))


if __name__ == "__main__":
    main(sys.argv[1:] or ["magazine"])
