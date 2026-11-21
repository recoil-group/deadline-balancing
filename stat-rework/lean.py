"""Lead rule: steepen the handling-versus-stability lean inside the slots that carry the choice.

For an item with positive value in its handling and stability (V = 0.60·h + 0.47·s > 0), its
handling share is x = 0.60·h / V. Inside its main competing set (the largest set it belongs to
that has a real choice), the shares are spread away from the set's median share p:

    x' = p + FACTOR · (x − p),   clamped to [SHARE_MIN, SHARE_MAX]
    h' = x'·V / 0.60,  s' = (1 − x')·V / 0.47

so every item keeps its EV exactly, the set's centre stays put, and options differ more in
direction and less in overall size. Reload is untouched. Items with no positive value (zero
reference parts, penalty parts) are untouched, as are hand-tuned overrides, which apply after.

Whole gun bodies set by the stock family's furniture table (Mosin stocks, the AUG Para conversion,
the Remington 700 stocks, the GLR-17) are not steepened: they are not stocks picked for feel.

Barrels and muzzle devices are not steepened: there, length moves handling and stability the same
way (short is handier and steadier) and the trade is recoil and velocity, so a handling-versus-
stability spread would contradict the length rule.

Set FACTOR to 1 (or empty FAMILIES) to switch this pass off.
"""

FAMILIES = {"stock": 2.0, "handguard": 2.0, "pistol_grip": 2.0, "foregrip": 2.0}
SHARE_MIN, SHARE_MAX = -0.25, 1.25   # at most a small negative in the other stat
# no steepened stat may exceed this magnitude (or the item's own pre-lean value, if larger)
CAP = {"stock": 25.0, "handguard": 25.0, "pistol_grip": 15.0, "foregrip": 12.0}
MIN_VALUE = 0.75                     # items worth less than this are left alone

W_H, W_S = 0.60, 0.47


def _value_share(v):
    h, s = v["handling"], v["stability"]
    V = W_H * h + W_S * s
    return V, (W_H * h / V if V > 0 else None)


def _excluded():
    try:
        from rules import stock
        return set(getattr(stock, "FURNITURE", {}))
    except Exception:
        return set()


def _fits(x, V, cap, before):
    h, s_ = x * V / W_H, (1 - x) * V / W_S
    return abs(h) <= max(cap, abs(before["handling"])) + 1e-9 and abs(s_) <= max(cap, abs(before["stability"])) + 1e-9


def main_set(item, ctx, eligible):
    best, size = None, 0
    for g in item["groups"]:
        grp = ctx.groups[g]
        n = sum(1 for m in grp["items"] if m in eligible)
        if grp["only_choice"] or n < 3:
            continue
        if n > size:
            best, size = g, n
    return best


def steepen(ctx, vals):
    """vals: name -> dict with handling/stability (floats). Modifies in place; returns notes."""
    notes = {}
    skip = _excluded()
    eligible = {n for n, it in ctx.items.items() if it["family"] in FAMILIES and n in vals
                and n not in skip and _value_share(vals[n])[0] >= MIN_VALUE}
    before = {n: dict(vals[n]) for n in eligible}
    pivots = {}
    for n in sorted(eligible):
        it = ctx.items[n]
        k = FAMILIES[it["family"]]
        if k == 1:
            continue
        g = main_set(it, ctx, eligible)
        if g is None:
            continue
        if g not in pivots:
            shares = sorted(_value_share(before[m])[1] for m in ctx.groups[g]["items"] if m in eligible)
            mid = len(shares) // 2
            pivots[g] = shares[mid] if len(shares) % 2 else (shares[mid - 1] + shares[mid]) / 2
        p = pivots[g]
        V, x = _value_share(before[n])
        x2 = min(SHARE_MAX, max(SHARE_MIN, p + k * (x - p)))
        cap = CAP.get(it["family"], 1e9)
        if not _fits(x2, V, cap, before[n]):  # pull back toward x until inside the cap
            lo, hi = 0.0, 1.0
            for _ in range(30):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if _fits(x + mid * (x2 - x), V, cap, before[n]) else (lo, mid)
            x2 = x + lo * (x2 - x)
        vals[n]["handling"] = x2 * V / W_H
        vals[n]["stability"] = (1 - x2) * V / W_S
        notes[n] = f"lean x{k:g} in {g.split('#')[0]} (handling share {x:.2f} -> {x2:.2f}, set median {p:.2f})"
    return notes
