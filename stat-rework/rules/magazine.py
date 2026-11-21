"""Magazines: reload_speed carries most of the value, capacity is the trade.

Rules, in plain words (E = old ergonomics, no weight credit):

1. Zero reference. Every value is a delta from the set's default magazine (the standard
   capacity), which is 0 on all three stats: E_rel = E - E(default). The default's old offset
   moves into the weapon base at calibration. Items with no set use E as it is.
2. Above standard (E_rel < 0): reload = 2.125 * E_rel, handling = 0.25 * E_rel (EV kept exactly:
   the slower reload is most of it, a little ADS bulk under the gun). Past -15 reload only half
   the rest counts, and it never goes below -25: the biggest old penalties also paid for
   draw/stow/stamina that the mag's own weight now charges, so their EV falls (100R casket:
   -25 -> about -14 EV; 75R/100R AK drums -11/-15 -> about -10/-12).
3. Drums, quads, caskets and couplers never reload faster than the slowest stick mag they compete
   with (the old sheet under-charged light-ergo drums because their weight did the work).
4. Below standard (E_rel > 0): the old bonus was mostly compensation for capacity. Reload takes
   the first 6 points in full, a third of the rest, at most 12 (about 5% faster); handling gets
   0.25 * E_rel, at most 2.5 (a short mag is a little less bulk under the gun). EV of 3R-10R mags
   falls well below the old value on purpose.
5. Material, relative to the default: polymer +0.5 reload, ribbed/tapered steel +0.5, straight-wall
   -0.5. Translucent and windowed variants equal their opaque twin.
6. Stability is 0: a magazine does not steady the gun.
7. Shotgun tube caps and extensions (R870 here, MP133 in mag_control) use `tube_split`: added
   shells against the default cap, reload 1.5 * E_rel and handling 0.5 * E_rel. These are per-shell
   loaders, so each reload point already scales every shell; the long tube also puts the extra
   shells' mass at the front.
8. Plates, adapters and couplers in this family use the mag_control rules.
"""

import re

RELOAD_PER_E = 2.125          # above standard: reload per old ergonomics point
HANDLING_PER_E = 0.25         # both sides: handling per old ergonomics point
RELOAD_KNEE = -15.0           # long mags: reload taken in full down to here
RELOAD_FLOOR = -25.0          # ... then half the rest, never below this
SHORT_FULL = 6.0              # short mags: reload taken in full up to here
SHORT_REST = 1 / 3            # ... then this share of the rest
SHORT_RELOAD_CAP = 12.0
SHORT_HANDLING_CAP = 2.5
TUBE_RELOAD_PER_E, TUBE_HANDLING_PER_E = 1.5, 0.5

MATERIAL = [  # (regex on name + pretty name, reload delta); first match wins
    (r"straight", -0.5),
    (r"polymer|pmag|plastic|bakelite|adapt2|l5awm|l7awm|translucent|transparent|promag|proclip|fang-h|carpe_diem|6l23|6l20|ak12", 0.5),
    (r"ribbed|taper", 0.5),
]


def text(item):
    return (item["name"] + " " + item["pretty"]).lower()


def material(item):
    for rx, d in MATERIAL:
        if re.search(rx, text(item)):
            return d
    return 0.0


def is_tube(item):
    return item["category"].lower() in ("magazine cap", "magazine extension") and "ammo_12g" in str(item["studio"].get("map"))


def set_default(item, ctx):
    """The default item of the item's first required set, or None."""
    for g in item["groups"]:
        d = ctx.groups[g].get("default")
        if d and d in ctx.items:
            return ctx.items[d]
    return None


def capacity(item):
    return item["magazine_capacity"] or 0.0


def is_bulky(item, std_cap):
    t = text(item) + " " + item["category"].lower()
    if re.search(r"drum|quad|casket|coupl", t):
        return True
    return std_cap > 0 and capacity(item) >= max(50, 2 * std_cap)


def box_split(e_rel):
    """(handling, reload) for a box magazine or capacity extension from its relative old ergo."""
    if e_rel >= 0:
        r = RELOAD_PER_E * e_rel
        if r > SHORT_FULL:
            r = SHORT_FULL + SHORT_REST * (r - SHORT_FULL)
        return min(HANDLING_PER_E * e_rel, SHORT_HANDLING_CAP), min(r, SHORT_RELOAD_CAP)
    r = RELOAD_PER_E * e_rel
    if r < RELOAD_KNEE:
        r = RELOAD_KNEE + 0.5 * (r - RELOAD_KNEE)
    return HANDLING_PER_E * e_rel, max(r, RELOAD_FLOOR)


def tube_split(item, ctx):
    d = set_default(item, ctx)
    e_rel = item["ergonomics"] - (d["ergonomics"] if d else 0.0)
    return {"handling": TUBE_HANDLING_PER_E * e_rel, "reload_speed": TUBE_RELOAD_PER_E * e_rel, "stability": 0.0,
            "_rule": f"shotgun tube: E{e_rel:+g} vs default cap, reload 1.5x / handling 0.5x (per-shell loader)"}


def mag_values(item, ctx):
    """(handling, reload, e_rel, std_cap) before the drum floor."""
    d = set_default(item, ctx)
    e0 = d["ergonomics"] if d else 0.0
    e_rel = item["ergonomics"] - e0
    h, r = box_split(e_rel)
    if d is not None:
        r = max(r + material(item) - material(d), RELOAD_FLOOR)
    std_cap = capacity(d) if d else 0.0
    return h, r, e_rel, std_cap


def restat(item, ctx, base):
    cat = item["category"].lower()
    if is_tube(item):
        return tube_split(item, ctx)
    if not item["magazine_capacity"] and re.search(r"plate|adapter|coupler", cat):
        from rules import mag_control
        return mag_control.restat(item, ctx, base)

    h, r, e_rel, std_cap = mag_values(item, ctx)
    why = f"mag E{e_rel:+g} vs default"
    if e_rel > 0 and RELOAD_PER_E * e_rel > SHORT_FULL:
        why += ", short-mag reload capped (rest was capacity compensation)"
    if RELOAD_PER_E * e_rel < RELOAD_KNEE:
        why += ", reload past -15 halved, floor -25 (weight now charges the rest)"
    if is_bulky(item, std_cap):
        sticks = [mag_values(c, ctx)[1] for c in ctx.competitors(item)
                  if capacity(c) and not is_bulky(c, std_cap) and not is_tube(c)]
        if sticks and min(sticks) < r:
            r = min(sticks)
            why += ", drum/quad: no faster than the slowest stick"
    if material(item):
        why += f", material {material(item):+g}"
    return {"handling": h, "reload_speed": r, "stability": 0.0, "_rule": why}
