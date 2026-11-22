"""Lead rule (round 5): which parts affect reload, and by how much.

Reload is re-statted here, not carried over. A part either has a real reason to change the reload
or it holds 0. Parts with a reason get a value from the table below, sized by how much the part
changes the reload action and the same for every comparable part. The family rules' reload points
are only used to give a non-reload part's old reload share back in handling and stability.

Values are fractions of the weapon's base reload time (negative = faster).

Magazines and capacity extensions: capacity against the slot's standard magazine
(c = capacity / standard; an extension counts as base + added rounds over the base). A longer
magazine is harder to index and seat, a shorter one quicker; drums, quads and caskets are slow to
seat whatever their length.

    c <= 0.4      short stick           -8%     (3-10 rounds where 20-30 is standard)
    c < 0.85      reduced stick         -4%     (10-25 where 20-30 is standard)
    c < 1.15      standard               0      (material, colour and curve variants included)
    c < 1.7       extended stick        +4%
    c >= 1.7      long stick            +8%
    drum / quad / casket, c < 2.5      +12%
    drum / quad / casket, c >= 2.5     +16%

Magazine controls and reload hardware:

    large competition magwell funnel                                 -5%
    flared magwell or magwell funnel (on the lower or as a part)    -3%
    enhanced magazine release (extended, ambidextrous, oversized)    -3%
    magazine pull or seating aid (mag assist, loop or bumper plate)  -3%
    large add-on release paddle                                      -2%
    enhanced bolt catch, bolt release or slide catch (empty reloads) -2%
    enhanced charging handle: -(1% + 0.25% per 0.01 dw of the part), so the size of the latch,
      which the part's weight measures, sets it: -1.5% for a 0.02 dw extended latch, -2% for a
      0.04 dw ambidextrous one, -3% for the 0.08 dw Raptor, -3.7% for the 0.11 dw side charger (rounded to 0.1%)
    standard releases, plates, magwells, handles and bolts            0

No reason to change the reload, so 0: shotgun tube extensions and caps (each shell loads the same
way, more shells just take longer by themselves), magazine sleeves, couplers and adapters,
receivers other than the flared-magwell lowers and the slide catch (their controls are separate
parts), Mosin bolts and bolt handles (they are cycling parts: fire_rate, cycling.py, round 6), R700 chassis (the R700 always takes detachable magazines), and every part of every other
family: stocks, grips, foregrips, handguards, barrels, muzzle devices, optics, sights, uppers,
triggers, tactical devices, ammunition, bayonets, misc.

What happens to the old value:

- MOVE_VALUE ("reload value to handling and stability"): a part that holds 0 because it has no
  reason, but had a reload share as part of its value (stocks at 0.25 E, pistol grips at 0.4 E,
  tube extensions, receivers, standard charging handles, ...), gets that value back in handling
  and stability, in the proportions of value it already has there, so its EV is unchanged. Set
  MOVE_VALUE = False to switch this off (the parts then just lose the reload share).
- Magazines of standard capacity drop their old reload difference (material-rule leftovers);
  that value is gone.
- Parts with a reason take the table value. Their EV follows the new reload: the carried-over
  values were too small to matter, and this step sizes them on purpose.
"""

MOVE_VALUE = True

MAG_FAMILIES = {"magazine", "mag_control"}

STICK_TIERS = [(0.4, -0.08, "short"), (0.85, -0.04, "reduced"), (1.15, 0.0, "standard"),
               (1.7, 0.04, "extended"), (float("inf"), 0.08, "long")]
BULKY = [(2.5, 0.12), (float("inf"), 0.16)]

# capacity extensions: rounds of the magazine they extend
EXT_BASE = {
    "allpistolsprings_tt33_+1r_mag_extension": 8,
    "dante_freelance_hart_smg_10r_mag_extension": 32,
    "dante_freelance_kosch_40sv_10r_carbine_magex": 10,
    "dante_freelance_kosch_40sv_10r_pistol_magex": 10,
    "equinox_plus_5_pmag_mag_extension": 30,
    "fireline_+2r_ext_pm_mag_plate": 8,
    "fireline_5_rnd_545_223_ak_mag_extension": 30,
    "kalis_kosch_10mm_18r_magex2": 15,
    "kalis_kosch_45acp_17r_magex2": 10,
    "kalis_kosch_9x19_23r_magex2": 17,
    "nexa_tactical_p226_4r_mag_extension": 15,
    "9x19_kriss_magex2_vector": 17,
    "custom_hart_smg_9x19_50r_extension": 32,
}
# magazines whose set has no default (or no set at all): the standard they are judged against
REF_CAP = {
    "9x19_glock_stick_31r": 17, "9x19_glock_stick_31r_vector": 17, "9x19_sgmt_50r_drum": 17,
    "banan_magazine": 30, "glock20_10mm_15r": 15, "hart_32rd": 32, "pf940_gen5_9x19_17r_magazine": 17,
    "custom_hart_smg_9x19_50r_mag": 32, "evermag_hart_ar9_10r_mag": 32, "evermag_hart_ar9_20r_mag": 32,
    "tt33_std_8rnd": 8, "tt33_extended_16r_mag": 8,  # the TT-33 magazine set has no default
}

LARGE_FUNNEL = -0.05
FLARED_MAGWELL = -0.03
ENHANCED_RELEASE = -0.03
PULL_AID = -0.03
LARGE_PADDLE = -0.02
BOLT_CATCH = -0.02
CH_BASE, CH_PER_DW = -0.01, -0.25   # enhanced charging handle: base + per dw of the part (latch size)

PARTS = {  # name: (reload_time, kind)
    # magazine controls
    "cosmotac_blastar_vkarmw_magwell": (FLARED_MAGWELL, "magwell funnel"),
    "hpf_concepts_rcm_ar15_milspec_magwell": (FLARED_MAGWELL, "magwell funnel"),
    "tactispec_rhino_r23_tactical_magwell": (LARGE_FUNNEL, "large competition magwell funnel"),
    "iron_claw_tactical_gen2_ak_magwell_system": (FLARED_MAGWELL, "AK magwell funnel"),
    "pmm_scar_16_magwell": (FLARED_MAGWELL, "flared FANG magwell"),
    "pmm_scar_17_magwell_type1": (FLARED_MAGWELL, "flared FANG magwell"),
    "pmm_scar_17_magwell_type2": (FLARED_MAGWELL, "flared FANG magwell"),
    "sig_sauer_p320_x_mag_funnel": (FLARED_MAGWELL, "pistol magwell funnel"),
    "sic_sturmer_p226_std_two_piece_magwell_grip": (FLARED_MAGWELL, "pistol grip with an integral flared magwell (round 7 review)"),
    "corvus_mounts_m4_trigger_guard": (FLARED_MAGWELL, "R700 bottom metal with a flared well and paddle release"),
    "aquila_defensio_aug_enhanced_release_button": (ENHANCED_RELEASE, "enhanced magazine release"),
    "arid_concepts_aug_improved_mag_release": (ENHANCED_RELEASE, "enhanced magazine release"),
    "ardian_weapons_adac15_mag_release": (ENHANCED_RELEASE, "ambidextrous magazine release"),
    "kf_416a5_ambi_mag_release": (ENHANCED_RELEASE, "ambidextrous magazine release"),
    "pmm_scar_oversized_mag_release_button": (ENHANCED_RELEASE, "oversized magazine release"),
    "ravaryn_arms_sic_p_series_extended_mag_release": (ENHANCED_RELEASE, "extended magazine release"),
    "mcs_rev21_gen2_r700_mag_release": (ENHANCED_RELEASE, "enhanced magazine release"),
    "kosch_ambidextrous_mag_catch": (ENHANCED_RELEASE, "ambidextrous magazine catch"),
    "arid_concepts_aug_mag_release_large_paddle": (LARGE_PADDLE, "large release paddle"),
    "magtap_223_mag_assist_l7awm": (PULL_AID, "mag assist"),
    "magtap_223_mag_assist_misc1": (PULL_AID, "mag assist"),
    "magtap_223_mag_assist_misc2": (PULL_AID, "mag assist"),
    "magtap_223_mag_assist_misc3": (PULL_AID, "mag assist"),
    "magtap_223_mag_assist_pmag": (PULL_AID, "mag assist"),
    "magtap_223_mag_assist_straightstanag": (PULL_AID, "mag assist"),
    "magtap_ranger_ak74/akm_bottom_plate": (PULL_AID, "loop bottom plate"),
    "magtap_ranger_m3_bottom_plate": (PULL_AID, "loop bottom plate"),
    "rsa_sg58_enhanced_bumper_magazine_bottom_plate": (PULL_AID, "bumper bottom plate"),
    # receivers
    "novacek_n4_gen3_ar15_lower_receiver": (FLARED_MAGWELL, "lower with a flared magwell"),
    "novacek_n4_gen3_ar15_lower_receiver_ar9": (FLARED_MAGWELL, "lower with a flared magwell"),
    "kosch_ambidextrous_slide_catch": (BOLT_CATCH, "ambidextrous slide catch"),
    # bolt catches and releases
    "ardian_weapons_ar15_extended_bolt_catch": (BOLT_CATCH, "extended bolt catch"),
    "kf_416a5_enhanced_ambi_bolt_catch": (BOLT_CATCH, "ambidextrous bolt catch"),
    "pmm_scar_battery_control_bolt_release": (BOLT_CATCH, "enlarged bolt release"),
    "magtap_ar15_bar_lever": (BOLT_CATCH, "bolt release lever"),
    # charging handles
}


CHARGING_HANDLES = {  # enhanced charging handles: name -> kind (value from CH_BASE + CH_PER_DW * weight)
    "kfp_knurled_extended_mpi54_charging_handle": "extended charging handle",
    "apex_bolt_handle_for_scar": "enhanced charging handle",
    "tss_custom_ak_bolt_on_oversize_gen3_charging_handle": "oversized charging handle",
    "veles_rp1_ak_charging_handle": "enhanced charging handle",
    "dynamic_development_group_ambi_scarging_handle": "ambidextrous charging handle",
    "ecm_gunslinger_charging_handle": "enhanced charging handle",
    "tc_enforcer_small_charging_handle": "enhanced charging handle",
    "tc_enforcer_charging_handle": "enhanced charging handle",
    "diemaco_c7_ambi_charging_handle": "ambidextrous charging handle",
    "kf_416_e1_ambi_charging_handle": "ambidextrous charging handle",
    "novacek_love_ar15_charging_handle": "enhanced charging handle",
    "tactispec_victory_charging_handle": "enhanced charging handle",
    "combat_arms_rack_charging_handle": "enhanced charging handle",
    "cerberus_arms_aug_raptor_charging_handle": "large-latch ambidextrous charging handle",
    "ardian_weapons_raptor_ambi_ar15_charging_handle": "large-latch ambidextrous charging handle",
    "hera_arms_straight_pull_charging_handle": "non-reciprocating side charging handle",
}


def is_tube(item):
    gfv = item["studio"].get("global_flag_values", {}) or {}
    return bool(gfv.get("mag_space", 0) or gfv.get("mag_space_add", 0)) or (
        item["category"].lower() in ("magazine cap", "magazine extension") and "ammo_12g" in str(item["studio"].get("map")))


def magazine_reload(item, ctx):
    """(reload_time, reason) for a magazine or capacity extension, or None if it has no capacity."""
    from rules import magazine as M

    cap = item["magazine_capacity"] or 0.0
    if cap <= 0:
        return None
    n = item["name"]
    if n in EXT_BASE:
        base = EXT_BASE[n]
        c, ref = (base + cap) / base, f"{base:g}+{cap:g} rounds over {base:g}"
        bulky = False
    else:
        d = M.set_default(item, ctx)
        std = (d["magazine_capacity"] or 0.0) if d else 0.0
        std = std or REF_CAP.get(n, 0.0)
        if not std:
            return 0.0, "no standard magazine to compare with"
        c, ref = cap / std, f"{cap:g} rounds over {std:g}"
        bulky = M.is_bulky(item, std)
    if bulky:
        for lim, v in BULKY:
            if c < lim:
                return v, f"drum/quad, {ref}"
    for lim, v, kind in STICK_TIERS:
        if c <= lim if kind == "short" else c < lim:
            return v, f"{kind} stick, {ref}"


def reload_of(item, ctx):
    """(reload_time, reason) for a reload part; (None, reason) for a part with no reason."""
    n = item["name"]
    if n in PARTS:
        return PARTS[n][0], PARTS[n][1]
    if n in CHARGING_HANDLES:
        return _charging_handle(item, ctx), f"{CHARGING_HANDLES[n]}, {item['weight']:g} dw"
    if n in EXT_BASE or (item["family"] in MAG_FAMILIES and not is_tube(item)):
        if is_tube(item):
            return None, "shotgun tube: each shell loads the same way"
        m = magazine_reload(item, ctx)
        if m is not None:
            return m
        if item["family"] in MAG_FAMILIES:
            cat = item["category"].lower()
            if "sleeve" in cat or "coupler" in cat or "adapter" in cat:
                return None, f"{cat}: does not change the reload"
            return 0.0, "standard magazine control"
    if is_tube(item):
        return None, "shotgun tube: each shell loads the same way"
    return None, "not a reload part"


def _charging_handle(item, ctx):
    """Round 8: whole percent, half percent where it separates two handles of one set."""
    import rounding

    raw = CH_BASE + CH_PER_DW * item["weight"]
    sib = []
    if ctx is not None:
        for g in item["groups"]:
            for m in ctx.groups[g]["items"]:
                if m != item["name"] and m in CHARGING_HANDLES and m in ctx.items:
                    sib.append(CH_BASE + CH_PER_DW * ctx.items[m]["weight"])
    return round(rounding.round_reload_part(raw, sib), 3) + 0.0


def _move(item, vals, dv):
    import rules

    wh, ws = abs(rules.W_H * vals["handling"]), abs(rules.W_S * vals["stability"])
    if wh + ws < 1e-9:
        a_h, _, a_s = rules.DEFAULT_VECTORS.get(item["family"], rules.DEFAULT_VECTORS["misc"])[:3]
        wh, ws = (abs(rules.W_H * a_h), abs(rules.W_S * a_s)) if a_h or a_s else (1.0, 0.0)
    vals["handling"] += dv * wh / (wh + ws) / rules.W_H
    vals["stability"] += dv * ws / (wh + ws) / rules.W_S


def apply(item, vals, ctx):
    """vals: handling, reload_points, stability (points). Sets vals["reload_time"]; returns a note."""
    import rules

    p = rules.round_half(vals.pop("reload_points", 0.0))
    rt, why = reload_of(item, ctx)
    is_mag = item["family"] == "magazine" or item["name"] in EXT_BASE or (item["magazine_capacity"] or 0) > 0
    if rt is None or (rt == 0 and not is_mag):
        vals["reload_time"] = 0.0
        if not p:
            return ""
        if not MOVE_VALUE:
            return f"reload 0 ({why}); old {p:+g} pt removed"
        _move(item, vals, rules.W_R * p)
        return f"reload 0 ({why}); old {p:+g} pt moved to handling and stability"
    vals["reload_time"] = rt
    if rt == 0:
        return f"reload 0 ({why})" + (f"; old {p:+g} pt dropped" if p else "")
    return f"reload {rt * 100:+g}% ({why})"
