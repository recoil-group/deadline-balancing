"""Barrels, plus the barrel-slot odds and ends filed under `barrel`.

Rules, in plain words:

- A barrel keeps its old value: EV(new) = old ergonomics. Barrels were balanced to equal strength
  at 20 points per dw very precisely, so no weight credit; the length trade comes from the split.
- Stability carries barrel length (it replaces the game's hidden barrel-length sway scaling):
  -1 stability per inch longer than the weapon's standard barrel, capped at +-8. The standard
  barrel is the one old ergonomics was measured from: the set's free (price 0) barrel, else its
  0-ergonomics barrel, else the standard barrel of that weapon's barrel class, else the slot default.
- The length share never exceeds the barrel's old ergonomics difference from the standard
  barrel, and is 0 when old ergonomics disagrees with the length direction, so handling never
  moves against the old ordering (handling keeps at least 88% of the old difference).
  One hand fix in overrides/barrel.csv: the R870 211mm sawn-off, whose old ergo sits below the
  325mm and so left the length rule no room.
- Profile: heavy / HBAR / bull / straight-profile barrels +1.5 stability for their mass; fluted
  barrels -0.5 (lighter for their length).
- Handling takes the rest of the value: h = (E - 0.47 s) / 0.60, limited to +-max(12, |E|) for
  the few extreme parts (sawn-off Mosins, 24" AR).
- Velocity, recoil, deviation, damage, fire rate stay as they are: long barrels win there.
- Muzzle parts filed here (suppressors, thread adapters, barrel extensions, the Halbek, the Tiduro
  modular compensator, the ASR mount) use the muzzle rules (rules/muzzle.py).
- Shrouds, gas-block mounts, barrel nuts, bushings and launcher tubes keep the default barrel
  split (1.0 / 0 / 0.85): small front parts with no length story.
"""

import re

from rules import W_H, W_S, round_half
from rules import muzzle

STAB_PER_INCH = 1.0
STAB_CAP = 8.0
SHARE_CAP = 1.0  # length stability at most the old ergonomics difference, so handling keeps >= 88% of it
PROFILE = [  # (pattern on name, stability change, reason)
    (r"heavy|hbar|bull|straight_profile", 1.5, "heavy profile"),
    (r"fluted", -0.5, "fluted"),
]
MUZZLE_CATEGORIES = r"suppressor|compensator|muzzle|thread adapter|barrel extension"
NO_GROUP_REFERENCE_MM = {"cmmg_mk9": 406.0, "bnb_value_line": 406.0}  # unreachable AR9 barrels


def length_mm(item):
    """Barrel length from the name: the largest 'NNNmm' (calibres like 10mm are smaller), else inches."""
    text = item["name"] + " " + item["pretty"]
    mm = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*mm", text) if float(x) >= 50]
    if mm:
        return max(mm)
    inch = re.findall(r"(\d+(?:\.\d+)?)\s*(?:\"|inch)", text) or re.findall(r"_(\d+(?:\.\d+)?)i_", item["name"])
    return float(inch[0]) * 25.4 if inch else None


def is_barrel(it):
    return it["category"] == "Barrel" and not re.search(r"suppressor", it["name"]) and length_mm(it)


def pick_reference(items, default=None):
    free = [it for it in items if it["price"] == 0]
    for pool in (free, [it for it in items if it["ergonomics"] == 0]):
        if pool:
            exact = [it for it in pool if it["name"] == default] or sorted(pool, key=lambda it: abs(it["ergonomics"]))
            return exact[0]
    return None


def reference(item, ctx):
    """(standard barrel item, length mm) the length rule measures from."""
    cache = ctx.__dict__.setdefault("_barrel_ref", {})
    if item["name"] in cache:
        return cache[item["name"]]
    ref = None
    groups = [g for g in item["groups"] if ctx.groups[g].get("required")] or item["groups"]
    for g in groups:
        members = [it for it in ctx.group_items(g) if is_barrel(it)]
        ref = pick_reference(members, ctx.groups[g].get("default"))
        if ref:
            break
    if ref is None and groups:
        cls = item["studio"].get("class")
        same_class = [it for it in ctx.items.values() if it["studio"].get("class") == cls and is_barrel(it)]
        ref = pick_reference([it for it in same_class if it["ergonomics"] == 0 and it["price"] == 0])
        if ref is None:
            d = ctx.groups[groups[0]].get("default")
            ref = ctx.items.get(d)
    if ref is not None:
        out = (ref, length_mm(ref))
    else:
        mm = next((v for k, v in NO_GROUP_REFERENCE_MM.items() if item["name"].startswith(k)), None)
        out = (None, mm)
    cache[item["name"]] = out
    return out


def length_stability(item, ctx):
    ref, ref_mm = reference(item, ctx)
    own = length_mm(item)
    if ref_mm is None or own is None:
        return 0.0, "no reference length"
    d_in = (own - ref_mm) / 25.4
    d_e = item["ergonomics"] - (ref["ergonomics"] if ref else 0.0)
    s = max(-STAB_CAP, min(STAB_CAP, -STAB_PER_INCH * d_in))
    why = f"{d_in:+.1f}in vs {ref['name'] if ref else f'{ref_mm:g}mm'}"
    if s * d_e < 0:
        return 0.0, why + ", old ergo disagrees with length: no length stability"
    if abs(s) > SHARE_CAP * abs(d_e):
        s = SHARE_CAP * abs(d_e) * (1 if s > 0 else -1)
        why += f", capped at {SHARE_CAP:g}x old ergo difference"
    return s, why


def restat(item, ctx, base):
    if re.search(MUZZLE_CATEGORIES, item["category"].lower()) or "suppressor" in item["name"]:
        out = muzzle.split(item)
        out["_rule"] = "barrel family, " + out["_rule"]
        return out
    if not is_barrel(item):
        return None
    e = item["ergonomics"]
    s, why = length_stability(item, ctx)
    for pat, ds, label in PROFILE:
        if re.search(pat, item["name"]):
            s += ds
            why += f", {label} {ds:+g}"
    s = round_half(s)
    h = (e - W_S * s) / W_H
    lim = max(12.0, abs(e))
    if abs(h) > lim:
        h = lim if h > 0 else -lim
        why += f", handling limited to {lim:g}"
    return {"handling": round_half(h), "reload_points": 0.0, "stability": s,
            "_rule": f"barrel length rule ({why}); handling keeps old value"}
