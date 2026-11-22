"""Misc: everything the family heuristic could not file.

Rules, in plain words:

1. Every misc item is first given the family it physically belongs to (REAL_FAMILY below) and is
   re-statted exactly as that family's rules would re-stat it (its rules/<family>.py, or that
   family's default split while the module does not exist yet). So spacers and pads follow stocks,
   rail extensions and hoods follow handguards, drop-on rails and mounts follow optics, sight
   assemblies follow iron sights, palm shelves and the RPG-7 rear grip follow pistol grips, mag
   funnels follow mag control, mag extensions follow magazines, small internal parts follow
   internals. Items with no old value stay empty.
2. One exception has its own table: the Hera CQR length-of-pull spacers (CQR_SPACERS). A longer
   spacer moves the shoulder contact back on a grip-stock: steadier, but a longer gun to bring
   up. Stability rises with length and handling falls a little, instead of the longest spacer
   being best on every stat.
3. Things that are none of these (cleaning rods, the junction box, the cat) keep the misc
   default split, which for their 0 or empty ergonomics is 0 / empty.
"""

import rules

STOCK, HANDGUARD, OPTIC, IRON, GRIP = "stock", "handguard", "optic", "iron_sight", "pistol_grip"
INTERNALS, RECEIVER, MAG, MAG_CONTROL, TACTICAL = "internals", "receiver", "magazine", "mag_control", "tactical"

REAL_FAMILY = {
    # optics: sight accessories, mounts, drop-on rails, alternates of real optics
    "adron_kobra_ekp_8_sunshade": OPTIC,
    "azimuth_t2_cordura_fabric_wrap": OPTIC,
    "deltapoint_attachment": OPTIC,
    "um_3_wilson": OPTIC,
    "paramount_arms_slx_1x_microprism_acss_g2_scope_alt": OPTIC,
    "paramount_arms_slx_1.53inch_straight_spacer_alt": OPTIC,
    "stupid_camera": OPTIC,
    "scout_scopes_ak_drop_on_rail": OPTIC,
    "si_ak_drop_on_rail": OPTIC,
    "hk_ump_top_rail": OPTIC,
    "kosch_default_slide_cover_plate": OPTIC,
    "zvetech_kosch_slide_cover": OPTIC,
    # iron sights and sight assemblies
    "akm_rear_sight_6p1_sb2_1": IRON,
    "truglo_glock_tfx_fs": IRON,
    "glock20_front_sight": IRON,
    "virticon_glock_supp_height_front_sights_wh_sf": IRON,
    "glock17l_front_sight": IRON,
    "acog_fs": IRON,
    "acog_rs": IRON,
    "hart_rear_ironsight_600m": IRON,
    "hk_g3_front_sight_assembly": IRON,
    "hk_g3_rear_sight_assembly_top": IRON,
    "hk_g3_rear_sight_assembly_base": IRON,
    "hk_mp5_std_front_sight_assembly": IRON,
    "sno_vulkan_rpg_7_rear_sight_zeroing_rail": IRON,
    "sno_vulkan_rpg_7_rear_sight_zeroing_rail_folded": IRON,
    # handguard-side rails, extensions and hoods
    "veles_dl_leader_handguard_extension": HANDGUARD,
    "veles_leader_insert_rail_handguard_extension": HANDGUARD,
    "veles_dl_2_gen2_sport_handguard_extension": HANDGUARD,
    "mcs_lss_nv_hood": HANDGUARD,
    "mcs_lss_xl_nv_hood_oversize": HANDGUARD,
    "mk10_bottom_adapter_large": HANDGUARD,
    "mk10_bottom_adapter_small": HANDGUARD,
    "mk10_side_adapter_large": HANDGUARD,
    "mk10_side_adapter_small": HANDGUARD,
    "mk10_top_adapter_large": HANDGUARD,
    "mk10_top_adapter_small": HANDGUARD,
    "rail": HANDGUARD,
    # stock parts and launcher shoulder pads
    "veles_pt_3_base_part": STOCK,
    "veles_pt_1_klassika_adjust_part": STOCK,
    "precision_intercontinental_roosevelt_700_sa_at_aics_gen2_folding_chassis_external_cover": STOCK,
    "hunterstock_lop_0.5_1": STOCK,
    "hunterstock_lop_0.5_2": STOCK,
    "hunterstock_lop_0.5_3": STOCK,
    "hunterstock_lop_0.5_4": STOCK,
    "sno_vulkan_rpg_7_wooden_shoulder_padding": STOCK,
    "launchtron_psrl_2_tube_shoulder_padding": STOCK,
    # grips
    "fit_deluxe_suregrip_palm_shelf": GRIP,
    "pachmayr_tactical_glock_grip_glove": GRIP,
    "pachmayr_rubber_grip_for_g20": GRIP,
    "sno_vulkan_rpg_7_rear_grip": GRIP,
    # magazines and magazine parts
    "9x19_kriss_magex2_vector": MAG,
    "nexa_tactical_p226_4r_mag_extension": MAG,
    "sig_sauer_p320_x_mag_funnel": MAG_CONTROL,
    "glock20_std_magazine_release": MAG_CONTROL,
    "kalis_scalar_gen3_mag_release_cover": MAG_CONTROL,
    # receivers and internals
    "kalis_scalar_std_small_ejection_port": RECEIVER,
    "kalis_scalar_std_large_ejection_port": RECEIVER,
    "kalis_scalar_std_front_cover": RECEIVER,
    "kalis_scalar_gen3_front_cover": RECEIVER,
    "kalis_scalar_std_bolt_carrier_guide_shaft": INTERNALS,
    "kalis_scalar_std_charging_handle_support": INTERNALS,
    "izhevsk_pm_trigger_connect": INTERNALS,
    "hk_ump9_bcg": INTERNALS,
    "hk_ump45_bcg": INTERNALS,
    "compact_length_gas_system": INTERNALS,
    "normal_length_gas_system_416a5": INTERNALS,
    "normal_length_gas_system_416d": INTERNALS,
    "hk_g3_charging_handle": INTERNALS,
    "sig_sauer_p320_fcu": INTERNALS,
    # tactical sub-part
    "whitehouse_rush_qe_junction_box_legacy_crane_connector": TACTICAL,
}

# Hera CQR length-of-pull spacers: name -> (handling, reload, stability). Old ergo 2 / 4 / 6.
CQR_SPACERS = {
    "15mm_cqr": (1.5, 0.5, 2.0),    # EV 2.0
    "30mm_cqr": (1.5, 0.5, 6.0),    # EV 3.9
    "45mm_cqr": (1.0, 0.5, 10.0),   # EV 5.5
}


def as_family(item, fam, ctx):
    """Re-stat `item` exactly as family `fam` would."""
    it = dict(item, family=fam)
    base = rules.default_split(it, ctx)
    out = None
    mod = rules.family_module(fam)
    if mod is not None and hasattr(mod, "restat"):
        try:
            out = mod.restat(it, ctx, dict(base))
        except Exception as e:  # another family's module being edited must not break misc
            out = None
            base["_rule"] += f" ({fam} rules raised {e!r})"
    out = dict(out or base)
    for k in ("handling", "reload_points", "stability"):
        out.setdefault(k, base[k])
    out["_rule"] = f"misc, re-statted as {fam}: " + str(out.get("_rule") or base["_rule"])
    return out


def restat(item, ctx, base):
    n = item["name"]
    if n in CQR_SPACERS:
        h, r, s = CQR_SPACERS[n]
        return {"handling": h, "reload_points": r, "stability": s,
                "_rule": "misc, CQR spacer (stock part): longer = steadier, slightly slower to shoulder"}
    fam = REAL_FAMILY.get(n)
    if fam:
        return as_family(item, fam, ctx)
    return None
