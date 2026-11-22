"""Bayonets, knives and bayonet lugs.

Rules, in plain words (E = old ergonomics, no weight credit):

1. A fixed blade is mass and length hung past the muzzle. It is slower to swing onto target
   (handling) and it makes the gun sway more when walking and costs more to hold steady
   (stability), the same way a longer barrel does in RULES.md. The heavy front's one real benefit,
   damping muzzle rise, is already on the sheet as -4..-5 vertical recoil, so stability is
   negative, not positive. Split: handling 0.8, stability 1.0 (EV 0.95 per point).
2. The blade is the gun-contact node of its assembly. Its required one-option sub-parts (bayonet
   grip, knife grip, scabbard sling) give their old ergonomics to the blade and keep only weight
   (RULES_MINED.md section 9.4, the Oct 2026 "move sub-part ergonomics onto the base part"
   commits). Assembly totals are unchanged: AKM Type I/II and M9 -2, M11 EOD -3.
3. A bayonet lug is a small clamp at the muzzle: handling = E, no sway effect.
"""

SPLIT_H, SPLIT_S = 0.8, 1.0
SUB_PART_CATEGORIES = {"Bayonet Grip", "Knife Grip", "Bayonet Sling"}


def assembly_ergo(item, ctx):
    """Blade ergonomics plus the ergonomics of the default sub-parts it hosts."""
    total = item["ergonomics"]
    for m in ctx.tree.att.get(item["name"], {}).get("map", []):
        child = ctx.items.get(m.get("default") or "")
        if child is not None and child["category"] in SUB_PART_CATEGORIES:
            total += child["ergonomics"]
    return total


def restat(item, ctx, base):
    cat = item["category"]
    if cat in SUB_PART_CATEGORIES:
        return {"handling": 0.0, "reload_points": 0.0, "stability": 0.0,
                "_rule": f"bayonet sub-part: weight only, its {item['ergonomics']:+g} moved to the blade"}
    if cat == "Bayonet Lug":
        return {"handling": item["ergonomics"], "reload_points": 0.0, "stability": 0.0,
                "_rule": "bayonet lug: small muzzle clamp, handling = E"}
    e = assembly_ergo(item, ctx)
    return {"handling": SPLIT_H * e, "reload_points": 0.0, "stability": SPLIT_S * e,
            "_rule": f"bayonet blade: assembly ergo {item['ergonomics']:+g} -> {e:+g} incl. sub-parts, "
                     f"split {SPLIT_H}/0/{SPLIT_S} (front mass and length)"}
