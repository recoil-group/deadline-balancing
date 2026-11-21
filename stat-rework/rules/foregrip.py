"""Foregrips, handstops, index panels, bipods and pump forends.

Only the first part with attach type `grip` on a build applies its stats; later grips count
weight only. Every handstop, index panel and finger stop in the sheet IS a `grip` (they compete
with foregrips at a flat +6 old ergonomics); only `hk_ump_handstop` is not, and it stacks.
Recoil columns are left as they are: they already make the grip choice a recoil trade, so the
new stats only decide how the rest of the value is spent.

Rules, in plain words (E = old ergonomics, no weight credit, reload_speed 0 throughout):

1. Handstops, finger stops, index panels, indexers, the minimal RK-6: a hand reference, not a grip. They drive the
   gun onto target: handling 1.25 * E, stability 0.5 * E (E = 6 gives h 7.5, s 3).
   The UMP handstop is the one that stacks with a grip, so it is kept smaller (h 6, s 2.5).
2. Angled grips (AFG, KAG, Cobra, Link, RK-4): push the gun onto target, some support:
   handling 1.0 * E, stability 0.85 * E.
3. Stubby / half-length verticals (Gunfighter short, half grips, RK-0/RK-5, PSRL grip):
   the family default, handling 0.8 * E, stability 1.1 * E.
4. Full vertical grips: front support always steadies a little, whatever the grip's other
   merits: stability 1.2 * E + 2, handling 0.75 * E - 1.5 (the +2 support is paid with -1.5
   handling, EV-neutral). Low-ergonomics recoil grips (VPG, SE-5, RK-1/RK-2) therefore keep a
   positive stability and pay in handling.
   RK grips on the angled B-25 mount (`*_angled`) sit like an angled grip: +1 handling,
   -1 stability against the same grip on a straight mount.
5. Bipod-grips and grip-pods: heavy front support: stability +7, handling -5.5 with legs
   collapsed and -7.5 extended (the deployed bipod itself lives in bipods.csv). As in the old
   sheet the values sit on the legs and the bodies stay 0. The grip-pod body is not a `grip`, so
   its legs are the counted grip. The Smite body IS a `grip` and is mounted before its legs, so
   in game the Smite legs (stats and recoil) only ever count weight: a Studio attach-type bug
   flagged in notes/foregrip.md, not patched here.
6. Folded bipods that stack with a grip (Harris base, AUG HBAR): front mass hanging below the
   barrel: handling 1.5 * E, stability -0.5 * E (E = -4 gives h -6, s +2).
7. AUG A3 folding grip: unfolded is a full vertical grip (rule 4); folded is a bare handguard
   hold, handling 1.5 * E, stability 0.2 * E.
8. Pump forends (R870, MP133) are the grip and the front end at once: default split
   (0.8 / 1.1); a slim, light forend leans handling (1.1 / 0.75), a heavy or railed one leans
   stability (0.5 / 1.5).
9. Misfiled: `hk_mp5k_polymer_handguard` is a handguard, restatted with the handguard default
   (0.9 / 0.1 / 0.8); `r870_shorty_std_bolt` and adapters/bodies at 0 stay 0.
"""

HANDSTOP = (1.25, 0.5)
ANGLED = (1.0, 0.85)
STUBBY = (0.8, 1.1)
VERTICAL = (0.75, 1.2)
VERTICAL_SUPPORT_H, VERTICAL_SUPPORT_S = -1.5, 2.0
ANGLED_MOUNT_H, ANGLED_MOUNT_S = 1.0, -1.0
FOLDED_BIPOD = (1.5, -0.5)
AUG_FOLDED = (1.5, 0.2)
FOREND = {"default": (0.8, 1.1), "slim": (1.1, 0.75), "heavy": (0.5, 1.5)}
HANDGUARD = (0.9, 0.1, 0.8)

# grip-node values for bipod-grips: (handling, stability)
BIPOD_GRIP = {
    "grip_pod_gps_02_legs_col": (-5.5, 7.0),
    "grip_pod_gps_02_legs_ext": (-7.5, 7.0),
    "smite_industries_bipod_foregrip_collapsed_legs": (-5.5, 7.0),
    "smite_industries_bipod_foregrip_extended_legs": (-7.5, 7.0),
    "smite_industries_ar_picatinny_bipod_foregrip": (0.0, 0.0),
    "grip_pod_gps_02_body": (0.0, 0.0),
    "harrison_pra_adapter": (0.0, 0.0),
}

HANDSTOPS = {
    "magtap_xtm_enhanced_handstop_1", "timber_creek_enforcer_handstop", "xtm_full_handstop",
    "magtap_mlok_index_panel", "magtap_mlok_index_panel_flipped", "nariakira_mlok_fingerstop",
    "magtap_mlok_hand_stop", "overlord_halo_mlok_handstop", "veles_rl_1_handstop",
    "veles_leader_handstop", "nariakira_vallais_kf_rail_indexer", "veles_rk6",
}
ANGLED_GRIPS = {
    "magtap_afg_2_grip", "magtap_mlok_afg_grip", "ecm_gunslinger_kag", "smite_industries_cobra_tactical_foregrip",
    "si_link_curved_mlok_fg", "alpha_four_tactical_angled_foregrip", "veles_rk4",
}
STUBBY_GRIPS = {
    "ecm_gunslinger_mod3_picatinny_shortened_foregrip", "ecm_gunslinger_mod3_picatinny_shortened_foregrip_flipped",
    "ecm_gunslinger_mod3_mlok_shortened_foregrip", "ecm_gunslinger_mod3_mlok_shortened_foregrip_flipped",
    "okb_crazy_romanian_picatinny_half_grip", "okb_crazy_romanian_mlok_half_grip", "equinox_ex_mlok_grip",
    "launchtron_psrl_plastic_foregrip", "veles_rk0", "veles_rk5",
}
FOLDED_BIPODS = {"harrison_hbr_base", "lowenherz_aug_hbar_folding_bipod"}
FORENDS = {
    "r870_speedfeed_handguard": "default",
    "r870_magtap_moe_handguard": "slim",
    "pro_tactical_pr870_handguard": "heavy",
    "mp133_plastic_handguard": "slim",
    "mp133_beechwood_handguard": "heavy",
}


def vertical(e):
    return VERTICAL[0] * e + VERTICAL_SUPPORT_H, VERTICAL[1] * e + VERTICAL_SUPPORT_S


def out(h, s, why, r=0.0):
    return {"handling": h, "reload_speed": r, "stability": s, "_rule": why}


def restat(item, ctx, base):
    n = item["name"]
    e = item["ergonomics"] or 0.0
    if n in BIPOD_GRIP:
        h, s = BIPOD_GRIP[n]
        return out(h, s, "bipod-grip: heavy front support on the counted grip node" if h or s
                   else "bipod-grip part that never applies stats (body not a grip / legs after the grip): 0")
    if n == "hk_ump_handstop":
        return out(6.0, 2.5, "handstop that stacks with a grip: kept small (h 6, s 2.5)")
    if n == "hk_mp5k_polymer_handguard":
        a_h, a_r, a_s = HANDGUARD
        return out(a_h * e, a_s * e, "misfiled handguard (only choice): handguard default 0.9/0.1/0.8", r=a_r * e)
    if n == "aug_a3_std_foregrip_folded":
        return out(AUG_FOLDED[0] * e, AUG_FOLDED[1] * e, "AUG grip folded: bare handguard hold (h 1.5x, s 0.2x)")
    if n in FORENDS:
        kind = FORENDS[n]
        a_h, a_s = FOREND[kind]
        return out(a_h * e, a_s * e, f"pump forend ({kind}): h {a_h}x, s {a_s}x")
    if n in FOLDED_BIPODS:
        return out(FOLDED_BIPOD[0] * e, FOLDED_BIPOD[1] * e, "folded bipod, stacks: front mass (h 1.5x, s -0.5x)")
    root = n[: -len("_angled")] if n.endswith("_angled") and n.startswith("veles_rk") else n
    if root in HANDSTOPS:
        h, s, why = HANDSTOP[0] * e, HANDSTOP[1] * e, "handstop / index: drives onto target (h 1.25x, s 0.5x)"
    elif root in ANGLED_GRIPS:
        h, s, why = ANGLED[0] * e, ANGLED[1] * e, "angled grip (h 1.0x, s 0.85x)"
    elif root in STUBBY_GRIPS:
        h, s, why = STUBBY[0] * e, STUBBY[1] * e, "stubby vertical (h 0.8x, s 1.1x)"
    elif "grip" in item["attach_type"] and e:
        h, s = vertical(e)
        why = "full vertical grip (h 0.75x-1.5, s 1.2x+2)"
    else:
        return out(0.0, 0.0, "no grip value: 0")
    if root != n:
        h, s = h + ANGLED_MOUNT_H, s + ANGLED_MOUNT_S
        why += ", on angled B-25 mount (+1 h, -1 s)"
    return out(h, s, why)
