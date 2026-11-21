"""Iron sights: front and rear sights, apertures, posts, sight bases and blocks, carry handles.

Rules, in plain words:

- An iron sight changes how quickly you find the sight picture, so its value is handling only.
  Reload is 0. Stability is 0: a sight does not steady the gun.
- Every sight that counts (the game counts the first two flagged iron sights) keeps the +1 it has
  had since 0.25.2, worth +1.5 handling. Folded and raised states are the same part and score
  the same.
- Fixed tall sights that compete with folding back-up sights on the same rails (Axtell fixed,
  Vectorworks Peak, KF standard posts and diopter, the M4 front sight gas block) score a little
  lower: 1.0 handling per old point instead of 1.5. Weapon-integrated sights with no folding
  alternative (AK, Mosin, pistols, SA58, UMP, G3, RPG) use the normal 1.5.
- Bases, blocks, hoods and posts that carried 0 stay 0; their value lives in the sight on top.
- Carry handles keep their old premium (they also host the carry-handle optics), split the same
  way as fixed sights.
- Parts filed here that are really something else are re-statted by their real family's rules
  (see MISFILED).
"""

import rules

FOLDING_FACTOR = 1.5   # handling per old ergonomics point, normal and folding sights
FIXED_FACTOR = 1.0     # fixed tall sights that compete with folding ones

FIXED_TALL = {
    "axtell_defense_fixed_sight_front_post",
    "axtell_defense_fixed_sight_rear_aperture",
    "vectorworks_peak01_front_post",
    "vectorworks_peak01_rear_aperture",
    "kf_pattern_half_front_sight_post",
    "kf_std_picatinny_rear_diopter_sight",
    "hart_m4fs_gasblock",
}

CARRY_HANDLES = {
    "hart_m4a1_carry_handle",
    "tristar_compact_carry_handle",
    "cosmotac_vism_gen2_carry_handle",
    "sg58_stg58_carry_handle",
    "af_far_long_carry_handle",
}

# real family of parts that ended up in iron_sight
MISFILED = {
    "kazarov_group_std_rpk16_559mm_barrel": "barrel",
    "ak12_std_415mm_barrel": "barrel",
    "kazarov_group_ak12k_314mm_barrel": "barrel",
    "ak12_gen2_dustcover": "receiver",
    "archient_technologies_elysium_addon_module": "handguard",
    "sanxian_qbz95_carry_handle": "handguard",
}


def delegate(item, fam, ctx, why):
    """Re-stat an item with another family's rules (its real physics)."""
    out = rules.restat(dict(item, family=fam), ctx)
    out["_rule"] = f"{why}; {fam} rules: {out.get('_rule', '')}"
    return out


def iron(item, factor=None):
    """One iron sight: handling only."""
    e = item["ergonomics"]
    if factor is None:
        factor = FIXED_FACTOR if (item["name"] in FIXED_TALL or item["name"] in CARRY_HANDLES) else FOLDING_FACTOR
    kind = "fixed tall" if factor == FIXED_FACTOR else "iron sight"
    return {"handling": factor * e, "reload_speed": 0.0, "stability": 0.0,
            "_rule": f"{kind}: handling {factor:g} x old ergo"}


def restat(item, ctx, base):
    fam = MISFILED.get(item["name"])
    if fam:
        return delegate(item, fam, ctx, f"misfiled iron_sight, really {fam}")
    return iron(item)
