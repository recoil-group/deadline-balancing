"""Handguard family: handguards, AK lowers and top covers, rails, rail panels, M-LOK covers.

Rules in plain words (EV = 0.60 h + 0.40 r + 0.47 s is kept equal to the old ergonomics):

1. Handguards (whole handguards, AK/SA58/AK-12 lowers, the XM177 bottom half, SCAR extensions and
   bottom rails) are the front-end handling-versus-stability trade. Stability comes from reach and
   front mass: the handguard at its pool's median weight gets 0.6 x the pool's median ergonomics,
   and every dw above or below that median adds or removes 16 stability. Weight is the reach proxy
   because inside a set weight tracks length (r = 0.90 over the AR and KF416 sets), and a quad rail
   that is heavier at the same length is the "heavy quad leans stability" case. Handling carries
   the rest of the old value, so short, slim, light handguards end up with much more handling and
   long, heavy ones with little. Neither stat goes below zero for a handguard with positive
   ergonomics. Handguards do not touch reload. The pool is every main handguard sharing a set with
   the item, including handguard-like parts filed elsewhere such as the KALIS Gen III shroud (an
   `_alt` twin uses its base item's pool, a sub-part its parent's); with no competitor at all the
   item gets the median split (s = 0.6 E).
2. Upper halves that come with a lower (SA58 tops): a fixed stability lean (0.7 / 0 / 1.25); they
   add length and mass over the barrel, not grip.
3. AK top covers: 0 stays 0. A comfortable cover or long rail with +1 is grip texture (like a
   panel). Sight-mount covers (-3) are sight height: slower on target and a looser cheek weld
   (1.2 / 0 / 0.6). The vented "cheese grater" (-1) is light but uncomfortable, so worse
   stability. The extra-long Klassika rail (-3) is front bulk: handling.
4. Top rails and carry handles on bullpups (AUG, QBZ) compete with sights and optics, so they use
   the sight split (1.5 / 0 / 0.2): their ergonomics stands for sight height and bulk. A negative
   one (raised or extended rail) is bulk on handling only.
5. Rail panels and M-LOK covers (first four count): grip texture, small handling and stability,
   stability rounded first so a bigger panel is never worse. No reload.
6. Bare rail sections (M-LOK picatinny sections, -0.5 flat): sharp edge under the hand and a little
   bulk, -0.5 handling and -0.5 stability.
7. Rails, rail mounts, side rails, gas tubes, retainers: 0 stays 0; a meaningful negative value is
   bulk or a raised mount and goes to handling; a small positive value is grip texture. Only-choice
   retainers with no physical effect are zeroed (the weapon base absorbs them).
"""

import statistics

from rules import W_H, W_S, round_half

S_MID = 0.6       # stability share of the pool's median ergonomics at the pool's median weight
K_REACH = 16.0    # stability per dw of weight above the pool's median
UPPER_PIECE = (0.7, 0.0, 1.25)
SIGHT_SPLIT = (1.5, 0.0, 0.2)
SIGHT_HEIGHT = (1.2, 0.0, 0.6)

MAIN_CATEGORIES = {"Handguard", "Lower Handguard", "Bottom Part", "Bottom Rail Mount"}
TOP_RAIL_CATEGORIES = {"Top Rail Mount"}
SIGHT_CATEGORIES = {"Flip Up Sight"}

# Only-choice parts with no physical effect on the three stats; their value moves to the base.
ZEROED = {
    "kazarov_ak_handguard_retainer": "handguard retainer has no physical effect; value moves to the weapon base",
    "kazarov_aks74u_handguard_retainer": "handguard retainer has no physical effect; value moves to the weapon base",
}
NOT_IN_STUDIO_MAIN = {"haga_defense_usc_extended_handguard", "centrefire_628lmf_b_mp5_handguard"}


def kind(item):
    name, cat = item["name"], item["category"]
    is_panel = item["studio"].get("is_rail_panel", False)
    if name in NOT_IN_STUDIO_MAIN or cat in MAIN_CATEGORIES:
        return "main"
    if name == "lm2":
        return "rail_section"
    if name == "railscales_rsb_vg":
        return "grip"
    if is_panel or cat in {"Rail Panel", "MLOK Cover", "Rail Cover"}:
        return "panel" if item["ergonomics"] >= 0 else "rail_section"
    if cat == "Upper Handguard":
        return "upper_piece"
    if cat == "Handguard Top Cover":
        return "top_cover"
    if cat in TOP_RAIL_CATEGORIES:
        return "top_rail"
    if cat in SIGHT_CATEGORIES:
        return "sight"
    return "rail"


def from_stability(e, s, rule):
    """Fix stability, give handling the rest of the old value (EV kept), both >= 0 for e >= 0."""
    if e >= 0:
        s = min(max(s, 0.0), e / W_S)
    h = (e - W_S * s) / W_H
    return {"handling": h, "reload_speed": 0.0, "stability": s, "_rule": rule}


def split(e, vec, rule):
    a_h, a_r, a_s = vec
    return {"handling": e * a_h, "reload_speed": e * a_r, "stability": e * a_s, "_rule": rule}


def grip_texture(e, rule):
    """Panels and covers: stability first on the 0.5 grid, handling the rest, so value rises with size."""
    s = round_half(e)
    h = round_half((e - W_S * s) / W_H)
    return {"handling": h, "reload_speed": 0.0, "stability": s, "_rule": rule}


def is_reach_part(c):
    """A handguard-like competitor, whatever family it was filed under (e.g. the KALIS Gen III shroud)."""
    if c["weight"] <= 0:
        return False
    if c["family"] == "handguard":
        return kind(c) == "main"
    return c["category"] in MAIN_CATEGORIES or c["category"] == "Barrel Shroud"


def reach_pool(item, ctx):
    """Main handguards competing with the item (itself included), with weight."""
    items = ctx.items
    if item["name"].endswith("_alt") and item["name"][:-4] in items:
        item = items[item["name"][:-4]]
    pool = {item["name"]: item}
    for c in ctx.competitors(item):
        if is_reach_part(c):
            pool[c["name"]] = c
    if len(pool) < 2:  # a sub-part (XM177 bottom half): use the pool of the handguard that hosts it
        for g in item["groups"]:
            for p in ctx.groups[g].get("parents", []):
                if p in items:
                    for c in ctx.competitors(items[p]):
                        if is_reach_part(c):
                            pool[c["name"]] = c
    return [c for c in pool.values() if c["weight"] > 0]


def main_handguard(item, ctx):
    e = item["ergonomics"]
    pool = reach_pool(item, ctx)
    if len(pool) < 2:
        return from_stability(e, S_MID * e, "handguard, no set to compare: median split")
    e_mid = statistics.median(c["ergonomics"] for c in pool)
    w_mid = statistics.median(c["weight"] for c in pool)
    s = S_MID * e_mid + K_REACH * (item["weight"] - w_mid)
    return from_stability(e, s, f"handguard reach: s = {S_MID}*{e_mid:g} + {K_REACH:g}*(w - {w_mid:.3f}); h = rest")


def restat(item, ctx, base):
    e = item["ergonomics"]
    name = item["name"]
    k = kind(item)
    if name in ZEROED:
        return {"handling": 0.0, "reload_speed": 0.0, "stability": 0.0, "_rule": ZEROED[name]}
    if k == "main":
        if item["weight"] <= 0 and e == 0:  # containers whose stats live on a sub-part (XM177)
            return {"handling": 0.0, "reload_speed": 0.0, "stability": 0.0, "_rule": "container, stats on its sub-part"}
        return main_handguard(item, ctx)
    if k == "upper_piece":
        return split(e, UPPER_PIECE, "upper handguard half: length and mass over the barrel")
    if k == "top_cover":
        if e == 0:
            return split(0.0, (0, 0, 0), "top cover: 0 stays 0")
        if e > 0:
            return grip_texture(e, "top cover with +ergo: grip texture")
        mounts = set(item["studio"].get("mountable_types") or []) | {
            m.get("class") for m in item["studio"].get("map", []) if isinstance(m, dict)}
        if "cheese_grater" in name:
            return {"handling": 0.0, "reload_speed": 0.0, "stability": -1.5,
                    "_rule": "vented cover, light but uncomfortable: worse stability"}
        if any(m and ("sight_mount" in m or "azimuth" in m) for m in mounts):
            return split(e, SIGHT_HEIGHT, "sight-mount top cover: sight height (handling, cheek weld)")
        return split(e, (1.5, 0.0, 0.0), "long top rail: front bulk on handling")
    if k == "top_rail":
        if e < 0:
            return split(e, (1.5, 0.0, 0.0), "raised or extended top rail: bulk on handling")
        return split(e, SIGHT_SPLIT, "bullpup top rail / carry handle: sight split like its sight competitors")
    if k == "sight":
        return split(e, SIGHT_SPLIT, "handguard flip-up sight: iron sight split")
    if k == "grip":
        return split(e, (0.8, 0.0, 1.1), "rail scale with vertical grip: foregrip split")
    if k == "panel":
        return grip_texture(e, "rail panel / cover: grip texture")
    if k == "rail_section":
        return {"handling": -0.5, "reload_speed": 0.0, "stability": -0.5,
                "_rule": "bare rail section: sharp edge and bulk"}
    # plain rails, mounts, gas tubes
    if e == 0:
        return split(0.0, (0, 0, 0), "rail / mount: 0 stays 0")
    if e > 0:
        return grip_texture(e, "rail with +ergo: grip texture")
    return split(e, (1.5, 0.0, 0.0), "rail / mount penalty: bulk or raised mount on handling")
