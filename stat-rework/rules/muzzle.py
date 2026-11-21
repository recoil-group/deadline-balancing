"""Muzzle devices: suppressors, brakes, compensators, flash hiders, thread protectors, adapters.

Only the last muzzle device in a build counts (weight always counts). Parts that are not flagged
as muzzle devices in Studio (thread adapters, barrel extensions, suppressor bodies, covers, the
Halbek, the Tiduro modular compensator) always count and stack. rules/barrel.py sends the muzzle
parts filed under `barrel` here too.

Rules, in plain words:

- Every device keeps its old value: EV(new) = old ergonomics (no weight credit, lead decision:
  muzzle penalties track device type and can length, not weight).
- Stability takes a share of the old value set by what the device physically adds at the muzzle,
  handling takes the rest:  s = share * E,  h = (E - 0.47 * s) / 0.60.
    suppressor        0.3  length and front mass: a clear handling cost, a small stability cost
                           (no stability gain for mass: front-heavy ends sway more, RULES 1)
    brake/compensator 0.5  blast and concussion unsettle the hold as much as the swing
    flash hider       0.5  short and light; the old +1..+2 over brakes is "no blast"
    thread protector  0.5  bare muzzle, shortest and lightest end
    blast regulator,
    suppressor cover  0.5  same as flash hiders
    adapter / piston  1.0  pure length, nothing else
- Barrel extensions are barrel length: -1 stability per inch (as barrels), handling the rest.
- Recoil, velocity, deviation, damage, loudness unchanged.
"""

import re

from rules import W_H, W_S, round_half

STABILITY_SHARE = {
    "suppressor": 0.3,
    "brake": 0.5,
    "flash_hider": 0.5,
    "protector": 0.5,
    "regulator": 0.5,
    "cover": 0.5,
    "adapter": 1.0,
}


def kind(item):
    """Physical kind of a muzzle-slot part, from its Studio category, falling back to the name."""
    cat = (item.get("category") or "").lower()
    name = item["name"].lower()
    if "barrel extension" in cat or "barrel_extension" in name:
        return "extension"
    if "cover" in cat:
        return "cover"
    if "suppressor cap" in cat:
        return "adapter"
    if "suppressor mount" in cat:
        return "flash_hider" if item["ergonomics"] > 0 else "adapter"
    if "suppressor" in cat and "flash" not in cat or "suppressor" in name and not cat:
        return "suppressor"
    if "thread protector" in cat:
        return "protector"
    if "adapter" in cat or cat == "mount":
        return "adapter"
    if "regulator" in cat:
        return "regulator"
    if "flash" in cat:
        return "flash_hider"
    if re.search(r"brake|compensator|muzzle device", cat):
        return "brake"
    if (item.get("muzzle_loudness") or 0) <= -0.05:
        return "suppressor"
    if re.search(r"port|brake|comp", name):
        return "brake"
    return "flash_hider"


def extension_inches(item):
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:inch|\")", item["name"] + " " + item["pretty"])
    return float(m.group(1)) if m else 1.0


def keep_value(e, s):
    """Handling that keeps EV equal to the old ergonomics once stability is s."""
    s = round_half(s)
    return round_half((e - W_S * s) / W_H), s


def split(item):
    e = item["ergonomics"]
    k = kind(item)
    if k == "extension":
        inches = extension_inches(item)
        s = -inches if e < 0 else 0.0
        h, s = keep_value(e, s)
        return {"handling": h, "reload_speed": 0.0, "stability": s,
                "_rule": f"muzzle: barrel extension {inches:g}in, -1 stability/in, handling keeps old value"}
    share = STABILITY_SHARE[k]
    h, s = keep_value(e, share * e)
    return {"handling": h, "reload_speed": 0.0, "stability": s,
            "_rule": f"muzzle: {k}, stability {share:g} of old value, handling the rest (EV kept)"}


def restat(item, ctx, base):
    return split(item)
