"""Round 7: handling and stability from each part's profile (SPLIT_PROPOSAL v3).

Every part has a row in profiles/<family>.csv: its profile, an optional role, the real-world
counterpart it was judged against, and one line of why. This module turns that into handling and
stability. It replaces the family rules' handling/stability splits, the weight-in-set leans and the
x2 lean pass; nothing leans by weight.

The part's value V is its old ergonomics (or the row's `value`, when the old number is a known
anomaly), less what it already carries as reload_time (reload hardware outside the magazine
families) or fire_rate (cycling parts). The profile splits V:

    even                     h = s = 0.935 V                   (EV kept)
    handling, optic_compact,
    mount, barrel            h = V, s = 0                      (today's ADS effect; EV 0.6 V)
    optic_scope              h = V, s = 0.2 V
    stock_precision,
    grip_vertical, grip_pod  h = 0.5 V,  s = 1.49 V            (EV kept)
    stock_fixed              h = 0.75 V, s = 1.17 V
    stock_adjustable         even
    stock_compact,
    grip_angled              h = 1.15 V, s = 0.66 V
    handguard_long           h = 0.8 V,  s = 1.11 V
    handguard_short          h = 1.1 V,  s = 0.72 V
    cheek_riser              h = 0.25 V, s = 1.81 V
    buttpad                  s = 2.13 V
    reload_only, zero        h = s = 0
    magazine                 the magazine rule's handling, never a bonus (large magazines cost a
                             little handling, short and standard ones none; a drum is no handier
                             than the least handy stick it competes with); shotgun tube extensions cost
                             0.5 handling per old point against the standard cap (their old
                             reload share is not moved into handling); s = 0
    stockless                handier than every stock on the weapons it reaches (+2 over the
                             handiest), and clearly unsteady: stability from what is left of V,
                             kept between -12 and -4; set in finalize()

A penalty (V < 0) on a stability-leaning profile goes to handling (a heavy precision stock, a
bulky vertical grip, a long handguard are slow to bring up, not unsteady), but the part still
steadies: since round 8 it keeps stability max(2, -V) and handling takes the rest, so its EV is
0.6 V as for a handling part (grip-pod legs -3 / +2 collapsed, -5 / +3 extended). A penalty on a
handling-leaning profile splits evenly. optic_scope stability is 0.2 min(V, 0): a scope accessory
with a positive value does not cancel the magnification tax.

Handling-only parts keep h = V rather than the 1.67 V that EV-neutrality would give: their old
ergonomics was their ADS effect, and the reload and draw it also bought were never physical for a
sight, a muzzle device or a barrel.

Roles are an EV-neutral swing on top of the profile, the same size for every part of a class:
marksman  h - H, s + 1.28 H;  compact  h + H, s - 1.28 H;  H = 3 on major parts (stocks, barrels,
handguards, receivers, and parts on a barrel, stock or handguard profile filed elsewhere), 1.5 on
the rest, 1.5x when the row asks for `strong`.

A row may also give explicit `handling` and `stability`, for the few parts no profile fits; its
`why` says why.
"""

import csv
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "profiles")

W_H, W_S = 0.60, 0.47
EVEN = 1 / (W_H + W_S)


def _ev_kept(a_h):
    return (a_h, (1 - W_H * a_h) / W_S)


COEF = {
    "even": (EVEN, EVEN),
    "stock_adjustable": (EVEN, EVEN),
    "handling": (1.0, 0.0),
    "optic_compact": (1.0, 0.0),
    "mount": (1.0, 0.0),
    "barrel": (1.0, 0.0),
    "optic_scope": (1.0, 0.2),
    "stock_precision": _ev_kept(0.5),
    "grip_vertical": _ev_kept(0.5),
    "grip_pod": _ev_kept(0.5),
    "stock_fixed": _ev_kept(0.75),
    "stock_compact": _ev_kept(1.15),
    "grip_angled": _ev_kept(1.15),
    "handguard_long": _ev_kept(0.8),
    "handguard_short": _ev_kept(1.1),
    "cheek_riser": _ev_kept(0.25),
    "buttpad": _ev_kept(0.0),
    "reload_only": (0.0, 0.0),
    "zero": (0.0, 0.0),
}
STABILITY_LEANING = {"stock_precision", "stock_fixed", "grip_vertical", "grip_pod", "handguard_long"}
HANDLING_LEANING = {"stock_compact", "grip_angled", "handguard_short"}
SPECIAL = {"magazine", "stockless"}
PROFILES = set(COEF) | SPECIAL

ROLE_SWING = {"major": 3.0, "minor": 1.5}
STRONG = 1.5
MAJOR_FAMILIES = {"stock", "barrel", "handguard", "receiver"}
ROLE_S_PER_H = W_H / W_S

# family -> default profile for a part with no row
DEFAULT = {
    "magazine": "magazine", "mag_control": "reload_only", "stock": "stock_adjustable",
    "foregrip": "grip_vertical", "optic": "optic_compact", "iron_sight": "handling",
    "barrel": "barrel", "muzzle": "handling", "bayonet": "handling", "tactical": "handling",
    "internals": "even", "pistol_grip": "even", "handguard": "even", "receiver": "even",
    "ammo": "even", "misc": "even",
}

NEG_SUPPORT = 2.0  # round 8: least stability a stability-leaning part keeps when its value is negative
STOCKLESS_MARGIN = 2.0
STOCKLESS_STABILITY = (-12.0, -4.0)

_rows = None


def rows():
    global _rows
    if _rows is None:
        _rows = {}
        for path in sorted(glob.glob(os.path.join(DIR, "*.csv"))):
            with open(path, encoding="utf-8-sig", newline="") as f:
                for r in csv.DictReader(f):
                    n = (r.get("name") or "").strip()
                    if n:
                        if n in _rows:
                            raise SystemExit(f"{n} has two profile rows ({_rows[n]['_file']} and {os.path.basename(path)})")
                        r["_file"] = os.path.basename(path)
                        _rows[n] = r
    return _rows


def row(name):
    return rows().get(name)


def profile_of(item):
    r = row(item["name"])
    p = (r or {}).get("profile", "").strip() or DEFAULT.get(item["family"], "even")
    if p not in PROFILES:
        raise SystemExit(f"{item['name']}: unknown profile {p!r}")
    return p


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def apply(item, vals, ctx=None):
    """vals: handling, stability (rule values), reload_time, optional fire_rate. Sets handling and
    stability from the part's profile and role; returns a note."""
    import cycling
    import reload_scope
    import rules

    r = row(item["name"]) or {}
    p = profile_of(item)
    e = item["ergonomics"]
    v = _num(r.get("value"))
    v = e if v is None else v
    fam = item["family"]
    if fam not in ("magazine", "mag_control") and vals.get("reload_time"):
        v -= rules.W_R * rules.points_of(vals["reload_time"])
    v -= cycling.ev(item["name"])

    if p == "magazine" and ctx is not None and reload_scope.is_tube(item):
        from rules import magazine as M
        h, s = min(M.tube_split(item, ctx)["handling"], 0.0), 0.0
    elif p == "magazine":
        # round 8: a magazine of the slot's standard capacity (reload 0) has no handling either; the
        # old same-capacity differences were material noise
        h, s = (min(vals.get("handling") or 0.0, 0.0) if vals.get("reload_time") else 0.0), 0.0
    elif p == "stockless":
        h, s = 0.0, 0.0  # set in finalize(), once every competing stock is known
    else:
        a_h, a_s = COEF[p]
        if v < 0 and p in STABILITY_LEANING:
            # round 8: still steadier, the cost goes to handling (EV 0.6 V, as for a handling part)
            s = max(NEG_SUPPORT, -v)
            h = v - s * W_S / W_H
        else:
            if v < 0 and p in HANDLING_LEANING:
                a_h, a_s = EVEN, EVEN
            h, s = a_h * v, a_s * v
            if p == "optic_scope":
                s = a_s * min(v, 0.0)  # round 8: the magnification tax never turns into a bonus
    note = f"profile {p} (V {v:+.2f})"

    role = (r.get("role") or "").strip()
    if role in ("marksman", "compact"):
        major = fam in MAJOR_FAMILIES or p == "barrel" or p.startswith(("stock_", "handguard_"))  # round 8: misfiled majors
        hsw = ROLE_SWING["major" if major else "minor"]
        if (r.get("role_strength") or "").strip() == "strong":
            hsw *= STRONG
        sign = -1 if role == "marksman" else 1
        h += sign * hsw
        s -= sign * hsw * ROLE_S_PER_H
        note += f", {role} role ({'+' if sign > 0 else '-'}{hsw:g} handling)"

    eh, es = _num(r.get("handling")), _num(r.get("stability"))
    if eh is not None or es is not None:
        h = eh if eh is not None else h
        s = es if es is not None else s
        note += ", explicit values"
    vals["handling"], vals["stability"] = h, s
    vals["_v"] = v
    return note


def finalize(ctx, out):
    """Stockless options: handier than the handiest stock on their weapons, clearly unsteady.
    Drums: no handier than the least handy stick they compete with (round 8)."""
    notes = {}
    from rules import magazine as M
    import reload_scope
    for n, it in ctx.items.items():
        if n not in out or profile_of(it) != "magazine" or not M.capacity(it) or reload_scope.is_tube(it):
            continue
        std = M.mag_values(it, ctx)[3]
        if not M.is_bulky(it, std) or _num((row(n) or {}).get("handling")) is not None:
            continue
        sticks = [out[c["name"]]["handling"] for c in ctx.competitors(it)
                  if c["name"] in out and profile_of(c) == "magazine" and M.capacity(c) and not M.is_bulky(c, std)
                  and not reload_scope.is_tube(c) and out[c["name"]]["handling"] is not None]
        if sticks and min(sticks) < out[n]["handling"]:
            out[n]["handling"] = min(sticks)
            notes[n] = f"drum: handling no better than the least handy stick ({min(sticks):g})"
    stocks = [(n, set(it["weapons"])) for n, it in ctx.items.items()
              if n in out and profile_of(it).startswith("stock_") and out[n]["handling"] is not None]
    for n, it in ctx.items.items():
        if it["family"] == "weapon" or n not in out or profile_of(it) != "stockless":
            continue
        if _num((row(n) or {}).get("handling")) is not None:
            continue
        ws = set(it["weapons"])
        best = max((out[m]["handling"] for m, mw in stocks if mw & ws), default=0.0)
        v = out[n].get("_v")
        v = it["ergonomics"] if v is None else v
        h = max(best, v) + STOCKLESS_MARGIN
        lo, hi = STOCKLESS_STABILITY
        s = min(max((v - W_H * h) / W_S, lo), hi)
        out[n]["handling"], out[n]["stability"] = h, s
        notes[n] = f"stockless: handling {h:.1f} (handiest stock on its weapons {best:.1f} + {STOCKLESS_MARGIN:g}), stability {s:.1f}"
    return notes
