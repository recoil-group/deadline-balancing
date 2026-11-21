"""Pistol grips, grip cores and modules, backstraps, grip wraps, palm rests.

A pistol grip is mostly handling: grip angle, shape and texture get the gun onto target. Palm
swells, beavertails, palm shelves, trigger guards, rubber and heavier grips add steadiness. A good
grip also lets the hands work a little faster on a reload. Recoil columns are left as they are.

Rules, in plain words (E = old ergonomics, no weight credit):

1. Standard grips (A1/A2, MOE, stock AK and pistol grips, wraps, cores, backstraps):
   handling 1.0 * E, reload 0.4 * E, stability 0.5 * E (the family default).
2. Steep / CQB grips (vertical angle, slim, skeletonized, chopped, compact frames):
   handling 1.25 * E, reload 0.4 * E, stability 0.15 * E.
3. Support grips (palm swell, beavertail, palm shelf, trigger guard, rubber or heavy grips,
   thumbhole and large backstraps): handling 0.75 * E, reload 0.4 * E, stability 0.85 * E.
4. Magwell grips (P226 two-piece magwell): the flare guides the magazine:
   handling 0.3 * E, reload 1.5 * E, stability 0.3 * E.
5. Stockless shotgun pistol grips (R870 Raptor, MP-133 plastic grip) replace the stock: very
   quick to the eye, no shoulder to steady the gun: handling 1.45 * E, reload 0.35 * E,
   stability -0.3 * E (E = 14 gives h 20.5, r 5, s -4). Stocks in the same slot carry large
   positive stability, so the gap to a stock is far larger than -4.
6. Every reload share is the same 0.4 * E (rules 1-3), so the trade inside a set is handling
   against stability, with the old ergonomics ordering kept.
Items not listed in a table use rule 1.
"""

SPLITS = {
    "standard": (1.0, 0.4, 0.5),
    "cqb": (1.25, 0.4, 0.15),
    "support": (0.75, 0.4, 0.85),
    "magwell": (0.3, 1.5, 0.3),
    "stockless": (1.45, 0.35, -0.3),
}

KIND = {
    # AR-15 family (incl. SCAR variants)
    "hart_a1_chopped_pistol_grip": "cqb",
    "tactical_dynamics_anodized_skeletonized_ar15_pistol_grip": "cqb",
    "timber_creek_enforcer_pistol_grip": "cqb",
    "kalis_scalar_gen3_ar15_pistol_grip": "cqb",
    "ecm_gunslinger_mod3_ar15_pistol_grip": "cqb",
    "pww_ecm_gunslinger_mod3_scar_pistol_grip": "cqb",
    "magtap_moa_k2_ar15_pistol_grip": "cqb",
    "magtap_moa_k2_scar_pistol_grip": "cqb",
    "mcs_premier_avp_grip": "cqb",
    "fit_deluxe_ar15_suregrip": "support",
    "kf_ar15_battlegrip_beavertail": "support",
    "axtell_defense_pistol_grip_with_trigger_guard": "support",
    "equinox_ex15_orion_pistol_grip": "support",
    "hera_arms_cqr_gen2_pistol_grip": "support",
    # AK
    "magtap_moa_k2_ak_pistol_grip": "cqb",
    "mg47": "cqb",
    "kazarov_ak74_bakelite_6p4_sb8v": "support",
    "us_pine_ak_pistol_grip": "support",
    "veles_rk3_ak_pistol_grip": "support",
    # pistols, SMGs, others
    "khorovod_pm_pistol_grip": "cqb",
    "pro_tactical_pm_g_pistol_grip": "support",
    "protac_ergonomic_ag_far_pistol_grip": "support",
    "razor_arms_g02": "cqb",
    "sic_sturmer_p226_std_two_piece_magwell_grip": "magwell",
    "sig_sauer_p320_xcarry_grip_module": "cqb",
    "whitner_defense_edc_x9_backstrap_small": "cqb",
    "whitner_defense_edc_x9_backstrap_large": "support",
    "precision_intercontinental_at_aics_gen2_thumbhole_backstrap": "support",
    "hk_psg1_wooden_grip": "support",
    "hk_psg1_grip_palm_rest": "support",
    # stockless shotgun grips (compete with stocks)
    "r870_earthquake_raptor_pistol_grip": "stockless",
    "mp133_153_plastic_pistol_grip": "stockless",
}


def restat(item, ctx, base):
    e = item["ergonomics"] or 0.0
    kind = KIND.get(item["name"], "standard")
    a_h, a_r, a_s = SPLITS[kind]
    return {"handling": a_h * e, "reload_speed": a_r * e, "stability": a_s * e,
            "_rule": f"{kind} grip ({a_h}/{a_r}/{a_s})"}
