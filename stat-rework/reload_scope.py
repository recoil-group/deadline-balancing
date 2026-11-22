"""Lead rule (round 5): which parts may carry reload_time, and what happens to the rest.

Only parts that change the reload action itself carry reload:

- every magazine and capacity extension (family `magazine`) and every magazine control (family
  `mag_control`: releases, magwells, mag assists, loop and bottom plates, sleeves);
- the receiver, internals and misc parts listed in PARTS, each with its reason. Lower receivers
  only where the lower is the magazine well or brings ambidextrous or flared reload controls;
  bolt catches and releases, charging handles, the Mosin bolt and handles, R700 bottom metal.

Everything else (stocks, pistol grips, foregrips, handguards, barrels, muzzle devices, optics,
sights, uppers, slides, frames, triggers, tactical devices, ammunition, bayonets, other misc) holds
reload 0.

Two steps, both on the rules' reload points before they become reload_time:

1. Scope. A part outside the list loses its reload. A part inside it whose reload would be under
   MIN_TIME (0.5% of reload time, i.e. 1 point or less) is dropped to 0; that value is simply gone.
2. MOVE_VALUE ("reload value to handling and stability"). A part that loses a reload share it had
   as part of its value gets that value back in handling and stability, in the proportions of
   value it already has there, so its EV is unchanged. Set MOVE_VALUE = False to switch this off
   (the parts then just lose the reload share).
"""

FAMILIES = {"magazine", "mag_control"}
MIN_TIME = 0.005
MOVE_VALUE = True

_LOWER_WELL = "the Scalar lower is the magazine well: it sets which magazine the gun takes"
PARTS = {
    # lower receivers and chassis
    "novacek_n4_gen3_ar15_lower_receiver": "flared magazine well",
    "novacek_n4_gen3_ar15_lower_receiver_ar9": "flared magazine well",
    "ardian_weapons_ax556_adac15_lower_receiver": "fully ambidextrous lower: ambi magazine release and bolt catch",
    "lingle_industries_ar17_scar_h_lower": "AR-pattern lower for the FANG-H: AR magazine release and bolt catch",
    "kalis_scalar_gen2_early_9x19_lower_receiver": _LOWER_WELL,
    "kalis_scalar_gen2_late_9x19_lower_receiver": _LOWER_WELL,
    "kalis_scalar_gen2_early_40sv_lower_receiver": _LOWER_WELL,
    "kalis_scalar_gen2_late_40sv_lower_receiver": _LOWER_WELL,
    "kalis_scalar_gen3_45acp_lower_receiver": _LOWER_WELL,
    "kalis_scalar_gen3_10mm_lower_receiver": _LOWER_WELL,
    "precision_intercontinental_roosevelt_700_sa_at_aics_gen2_folding_chassis_frame": "R700 chassis with a detachable-magazine well",
    "mcs_lss_gen2_carbine_chassis": "R700 chassis with a detachable-magazine well",
    "kosch_ambidextrous_slide_catch": "ambidextrous slide catch: releases the slide on empty reloads",
    # bolt catches and releases
    "ardian_weapons_ar15_extended_bolt_catch": "bolt catch",
    "kf_416a5_enhanced_ambi_bolt_catch": "bolt catch",
    "pmm_scar_battery_control_bolt_release": "bolt release",
    "magtap_ar15_bar_lever": "bolt release lever",
    "kosch_ambidextrous_mag_catch": "magazine catch",
    # charging handles (empty reloads)
    "aquila_defensio_aug_charging_handle": "charging handle",
    "kalis_scalar_std_charging_handle": "charging handle",
    "kfp_knurled_extended_mpi54_charging_handle": "charging handle",
    "sg58_std_charging_handle": "charging handle",
    "apex_bolt_handle_for_scar": "charging handle",
    "tss_custom_ak_bolt_on_oversize_gen3_charging_handle": "charging handle",
    "hart_m4a1_charging_handle": "charging handle",
    "veles_rp1_ak_charging_handle": "charging handle",
    "cerberus_arms_aug_raptor_charging_handle": "charging handle",
    "dynamic_development_group_ambi_scarging_handle": "charging handle",
    "ecm_gunslinger_charging_handle": "charging handle",
    "tc_enforcer_small_charging_handle": "charging handle",
    "diemaco_c7_ambi_charging_handle": "charging handle",
    "kf_416_e1_ambi_charging_handle": "charging handle",
    "tc_enforcer_charging_handle": "charging handle",
    "novacek_love_ar15_charging_handle": "charging handle",
    "tactispec_victory_charging_handle": "charging handle",
    "combat_arms_rack_charging_handle": "charging handle",
    "ardian_weapons_raptor_ambi_ar15_charging_handle": "charging handle",
    "hera_arms_straight_pull_charging_handle": "charging handle",
    "aft_charging_handle": "charging handle",
    # bolt-action reload hardware
    "mosin_default_bolt": "Mosin bolt: worked for every stripper-clip reload",
    "resolute_bolt": "Mosin bolt: worked for every stripper-clip reload",
    "mosin_infantry_bolt_handle": "Mosin bolt handle",
    "ivan_bolt_handle": "Mosin bolt handle",
    "corvus_mounts_m4_trigger_guard": "R700 bottom metal: the magazine well and release",
    # misc parts that are really magazine parts
    "9x19_kriss_magex2_vector": "magazine extension",
    "nexa_tactical_p226_4r_mag_extension": "magazine extension",
    "sig_sauer_p320_x_mag_funnel": "magazine funnel",
}


def allowed(item):
    return item["family"] in FAMILIES or item["name"] in PARTS


def apply(item, vals):
    """vals: handling, reload_points, stability in points. Modifies in place; returns a note or ''."""
    import rules

    r = rules.round_half(vals.get("reload_points", 0.0))
    if r == 0:
        vals["reload_points"] = 0.0
        return ""
    if allowed(item):
        if abs(rules.time_of(r)) < MIN_TIME - 1e-9:
            vals["reload_points"] = 0.0
            return f"reload {r:+g} pt under 0.5% of time: dropped"
        return ""
    vals["reload_points"] = 0.0
    if not MOVE_VALUE:
        return f"reload {r:+g} pt removed (not a reload part)"
    dv = rules.W_R * r
    wh, ws = abs(rules.W_H * vals["handling"]), abs(rules.W_S * vals["stability"])
    if wh + ws < 1e-9:
        a_h, _, a_s = rules.DEFAULT_VECTORS.get(item["family"], rules.DEFAULT_VECTORS["misc"])[:3]
        wh, ws = (abs(rules.W_H * a_h), abs(rules.W_S * a_s)) if a_h or a_s else (1.0, 0.0)
    vals["handling"] += dv * wh / (wh + ws) / rules.W_H
    vals["stability"] += dv * ws / (wh + ws) / rules.W_S
    return f"reload {r:+g} pt moved to handling and stability (not a reload part)"
