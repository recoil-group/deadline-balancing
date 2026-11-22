"""Optics, mounts and optic accessories.

Rules, in plain words (old ergonomics `E`; no weight credit, see RULES.md section 3):

- Sights (red dots, reflexes, holos, prisms, scopes, NV scopes, magnifiers) cost handling: bulk,
  height and eye box decide how fast you get on target. Reload is 0. The old sheet set `E` by
  class, so `E` is used as the class:
    - compact class (E >= -2: 1x dots, reflexes, holos, small prisms, magnifiers):
      handling = E, stability 0. These now sit close to zero, since a small sight never slowed
      the reload and its draw/stamina cost is now carried by its weight.
    - magnified or bulky class (E < -2: fixed prisms and ACOGs, LPVOs, big scopes, NV, the two
      oversized reflexes): handling = 1.5 E, stability = 0.2 E (a heavy tube high above the
      bore, a small top-heavy cost). Keeps the old value (EV ~ E).
- Mounts, risers, rings, spacers, footprints, plates, offset mounts: handling = E, the rest 0.
  Most are 0 (the team made mounts free in 0.25.4) and stay 0; mounts that kept a bulk penalty
  (carry-handle rails, AK side rails, tall Mosin rails) keep it as handling only.
- Caps, covers, eye cups, hoods: split with the same factors as the sight they fit, so the
  sight-plus-cap total moves exactly as the old total did. (Eye cups on magnified scopes
  therefore carry a little stability: a cup braces the eye.)
- Iron sights filed here (night-sight inserts, a few rear sights) use the iron sight rule.
- Parts filed here that are really something else (handguard rails, AUG rails, foregrip adapters,
  a shotgun tube cap, a charging-handle mount, sling mounts) use their real family's rules
  (MISFILED). Suppressor heat shields keep their old value as handling only: their +2.5 offsets
  the shield's and coupler's own weight in the team's strength score (~0.13 dw), so they stay a
  free cosmetic choice.
"""

import rules
from rules import iron_sight

COMPACT_LIMIT = -2.0           # E at or above this: compact class
COMPACT = (1.0, 0.0, 0.0)      # (handling, reload, stability) per old point
MAGNIFIED = (1.5, 0.0, 0.2)

SIGHT_CATEGORIES = {
    "Sight", "Red Dot Sight", "Red dot Sight", "Red dot sight", "Holo Sight", "Holo sight",
    "Collimator Sight", "Collimator sight", "Prism Sight", "Battle Sight", "Scope",
    "Dovetail Optic", "NV Scope", "Optic", "Magnifier",
}
ACCESSORY_CATEGORIES = {"Cap", "Caps", "Cover", "Lens Caps", "Eye Cup", "Access Point Cap", "Sight Hood"}
ACCESSORY_NAMES = {"z24_covers"}
IRON_IN_OPTIC = {
    "gdr_zvn_64_night_front_sight", "gdr_zvn_64_night_rear_sight_ak74", "gdr_zvn_64_night_rear_sight_akm",
    "r870_std_rear_sight", "glock20_lf_rear_sight", "strauss_cq_deltapoint_pro_rear_ironsight",
}
HEAT_SHIELDS = {
    "taclite_rac_gen2_6inch_suppressor_shield", "taclite_rac_gen2_7inch_suppressor_shield",
    "taclite_rac_gen3_6inch_suppressor_shield", "taclite_rac_gen3_7inch_suppressor_shield",
}

MISFILED = {
    # rail sections, panels and top rails on handguards
    "pro_tactical_upr_16_4_bottom": "handguard", "pro_tactical_upr_16_4_top": "handguard",
    "cosmotac_marsv2_bottom": "handguard", "cosmotac_marsv2_top": "handguard",
    "calsport_handguard_long_accessory_rail_bottom": "handguard",
    "calsport_handguard_long_accessory_rail_side": "handguard",
    "calsport_handguard_short_accessory_rail_bottom": "handguard",
    "calsport_handguard_short_accessory_rail_side": "handguard",
    "veles_b_2l_34mm_rail_side": "handguard", "veles_b_2l_34mm_rail_top": "handguard",
    "veles_b_2l_34mm_rail_grips": "handguard", "veles_b_2u_75mm_rail_side": "handguard",
    "veles_b_2u_75mm_rail_top": "handguard", "veles_b_2u_75mm_rail_grips": "handguard",
    "ihs_aug_a3_sa_cqc_top_rail": "handguard", "ihs_aug_a3_sa_cqc_handguard": "handguard",
    "cerberus_arms_aug_cantiliver_forend_top_rail": "handguard",
    "cerberus_arms_aug_cantiliver_forend_side_rail": "handguard",
    "pac_mre_standard_front_filler_tube": "handguard", "pac_mre_railed_front_filler_tube": "handguard",
    "pmm_scar_heavy_duty_mlok_bottom_panel": "handguard",
    "target_sports_mmh94_mlok_top": "handguard", "target_sports_mmh94_picatinny_top": "handguard",
    "archient_technologies_ak_gastube_mount_type1": "handguard",
    "archient_technologies_ak_gastube_mount_type2": "handguard",
    # foregrip slot / foregrip adapters
    "aquila_defensio_aug_forward_accessory_rail": "foregrip",
    "steyr_aug_a3_xs_bottom_accessory_rail": "foregrip",
    "rk_foregrip_mount": "foregrip", "rk_short_foregrip_mount": "foregrip", "rk_b25_angled_mount": "foregrip",
    # others
    "mp153_4r_mag_cap": "mag_control",
    "arid_concepts_charging_handle_mount": "internals",
    "aug_a3_sling_mount": "misc", "windsor_armory_sling_swivel": "misc", "sling_mount_ar": "misc",
    "nariakira_momentary_tailcap": "tactical", "centrefire_z68_clicky_tailcap": "tactical",
    "kalis_scalar_gen2_late_folding_stock_mount": "stock", "kalis_scalar_gen3_folding_stock_mount": "stock",
}


def split(e, vec, why):
    a_h, a_r, a_s = vec
    return {"handling": a_h * e, "reload_points": a_r * e, "stability": a_s * e, "_rule": why}


def sight_vector(e):
    return COMPACT if e >= COMPACT_LIMIT else MAGNIFIED


def is_sight(item):
    if item["category"] in SIGHT_CATEGORIES:
        return True
    # rows missing from Studio (alt colourways): treat negative ones as sights
    return item["category"] == "" and item["ergonomics"] < 0


def host_of(item, ctx):
    """The item the accessory fits (first parent of its slot that is a sheet item)."""
    for g in item["groups"]:
        for p in ctx.groups[g].get("parents", []):
            if p in ctx.items:
                return ctx.items[p]
    return None


def accessory(item, ctx):
    host = host_of(item, ctx)
    e = item["ergonomics"]
    if host is not None and host["family"] == "optic" and is_sight(host):
        vec = sight_vector(host["ergonomics"])
        cls = "compact" if vec is COMPACT else "magnified"
        return split(e, vec, f"accessory of {cls} sight {host['name'][:30]}: host factors")
    if host is not None and host["family"] != "optic":
        a = rules.DEFAULT_VECTORS.get(host["family"], rules.DEFAULT_VECTORS["misc"])[:3]
        return split(e, a, f"accessory of {host['family']} {host['name'][:30]}: host family split")
    return split(e, COMPACT, "accessory: handling only")


def restat(item, ctx, base):
    n, e = item["name"], item["ergonomics"]
    fam = MISFILED.get(n)
    if fam:
        return iron_sight.delegate(item, fam, ctx, f"misfiled optic, really {fam}")
    if n in IRON_IN_OPTIC:
        return iron_sight.iron(item)
    if n in HEAT_SHIELDS:
        return {"handling": e / rules.W_H, "reload_points": 0.0, "stability": 0.0,
                "_rule": "suppressor heat shield: old value as handling (offsets its own weight; cosmetic)"}
    if item["category"] in ACCESSORY_CATEGORIES or n in ACCESSORY_NAMES:
        return accessory(item, ctx)
    if is_sight(item):
        vec = sight_vector(e)
        cls = "compact sight" if vec is COMPACT else "magnified/bulky sight"
        return split(e, vec, f"{cls}: {vec[0]:g}/{vec[1]:g}/{vec[2]:g} x old ergo")
    return split(e, COMPACT, "mount/riser/adapter: bulk as handling only")
