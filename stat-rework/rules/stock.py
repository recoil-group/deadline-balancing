"""Stocks, braces, buttpads, cheek rests, spacers, buffer tubes, adapters, hinges and stock parts.

Rules, in plain words (E = old ergonomics, no weight credit; EV = 0.6 h + 0.4 r + 0.47 s):

1. A stock is the main handling-versus-stability choice. Each stock that carries its assembly's
   value gets a lean t from its type, plus a lean from the assembly's weight against the other
   stocks it competes with (heavier = more mass at the shoulder = steadier):
       precision +1.0, fixed +0.5, adjustable 0, folding -0.5, minimal/PDW/skeleton -1.0
       weight: +-0.5 for +-0.1 dw from the competing stocks' median assembly weight
   Split: reload 0.25 E (stocks barely touch reloads), handling (0.83 - 0.25 t) E, and stability
   takes the rest of the old value, so EV stays at E. t runs -1.5..+1.5: a heavy precision stock
   is about h 0.45 E / s 1.33 E, a light minimal stock about h 1.2 E / s 0.38 E.
2. Braces, tailhooks and the FRS-15 buffer-tube cover: handling 1.3 E, reload 0.25 E, stability
   -0.1 E. Keeping the full old value with negative stability would need handling far past the
   +-20 range, so braces give up about 15% of EV.
3. No stock (sling-swivel end plates and castle nuts, bufferless kits): handling 18, about what
   the handiest stocks reach, reload 0, and stability takes what is left of the old value,
   clamped to -14..-6. A stockless gun must be handier than a stocked one or it is never a
   choice; its sway is the price.
4. Buttpads, stock pads, recoil pads: stability only (s = E / 0.47).
5. Cheek rests, cheek pads, risers and length-of-pull spacers: stability (cheek weld), with a
   small handling cost for bulk: h = -E/3, s carries the rest.
6. Buffer tubes, adapters, mounts, hinges, locks, end plates and base parts: zero stays zero.
   A negative value is extra length and joints: h 0.9 E, s 0.95 E, no reload. A small positive
   value on a rigid adapter goes mostly to stability.
7. Full furniture (Mosin stocks, the AUG Para conversion, the two Remington 700 stocks) and the
   GLR-17 pistol stock are set by a small table: whole gun bodies are not comparable to AR or AK
   stocks, and a stock added to a pistol trades handling for stability.
"""

from rules import ev, round_half

LEAN = {"precision": 1.0, "fixed": 0.5, "adjustable": 0.0, "folding": -0.5, "minimal": -1.0}
R_FRAC = 0.25
NO_STOCK_HANDLING = 18.0
REF_WEIGHT = 0.25  # typical carbine stock assembly, used when a stock has fewer than 2 rivals
H_CAP = 22.0  # the handiest stocks stop here; the rest of their value goes to stability

# Value-carrying stocks by type. Anything not listed falls back to name/category keywords.
TYPES = {
    # AR receiver-extension stocks
    "si_viper_mod1_stock": "minimal", "whtnls_xm177_car": "minimal",
    "magtap_moa_sl_k_carbine_stock": "minimal", "talvern_m7a1_pdw_base_stock": "minimal",
    "hart_607_car15_buffer_tube": "minimal", "kf_416c_type_1_buttstock": "minimal",
    "kf_416c_type_2_buttstock": "minimal",
    "axtell_defense_collapsible_milspec_buttstock": "adjustable", "magtap_moa_carbine_stock": "adjustable",
    "hart_m4ss_stock": "adjustable", "validus_la_stock": "adjustable", "hera_arms_ccs_stock": "adjustable",
    "ar_tr2_stock": "adjustable", "magtap_rts_carbine_stock": "adjustable", "lmt_sopmod": "adjustable",
    "kf_416_slim_line_stock": "adjustable", "vyctor_emod_stock": "adjustable", "kf_416_e1_stock": "adjustable",
    "tas_cbs_ar15_stock": "adjustable", "starsurp_apex_m4_socom_gen4_stock": "adjustable",
    "hera_hrs_light_stock": "fixed", "ubr_gen2_stock": "fixed", "hera_arms_cqr_gen2_stock": "fixed",
    "leopard_atg_model_15_fixed_a2_ar15_stock": "fixed",
    "thordsen_frs_15_stock": "fixed", "hera_arms_cqr_gen1_pistol_grip_stock": "fixed",
    "magtap_prs_gen3_stock": "precision", "magtap_prs_gen2_stock": "precision",
    "mcs_v5_skeleton_rifle_stock": "precision", "mcs_v5_skeleton_rifle_stock_short": "precision",
    # AK
    "kazarov_ak74_polymer_6p20_sb7": "fixed", "kazarov_ak74_wooden_6p20_sb5": "fixed",
    "kazarov_akm_wooden_6p1_sb5": "fixed", "magtap_moa_a_frame_fixed_ak_stock": "fixed",
    "ellipse_30_fixed_ak_triangle_stock": "fixed", "hera_arms_cqr_gen1_ak_stock": "fixed",
    "kazarov_group_rpl_20_stock": "fixed", "pro_tactical_uas_akn_p": "adjustable",
    "al_qadissiya_tabuk_sniper_wooden_stock": "precision",
    "kazarov_ak74m_polymer_6p34_sb15": "folding", "kazarov_pp-19-01_vityaz_folding_stock": "folding",
    "magtap_zhukov_s_main_body": "folding", "kazarov_aks74u_6p26_sb5_skeletonized_stock": "minimal",
    "ak12_gen1_std_stock": "adjustable", "ak12_gen2_stock": "adjustable",
    "veles_pt_3_buttpad": "adjustable", "veles_pt_1_klassika_buttpad": "minimal",
    # SCAR, ACR, G3, MP5, UMP, SG58, Scalar
    "aft_stock_connector": "adjustable", "aft_sc_stock_adapter": "minimal", "aft_ssr_stock_assembly": "precision",
    "dynamic_development_group_sas_acr_stock": "adjustable",
    "hk_g3_std_fixed_plastic_stock": "fixed", "hk_psg1_stock_base": "precision",
    "spuhr_g3_r410_stock_assembly_adapter": "precision", "hk_g3a3_stock_endplate": "folding",
    "hk_mp5a2_plastic_fixed_stock": "fixed", "hk_mp5a3_early_gen_collapsible_stock": "minimal",
    "hk_mp5_hk94_cartman_stock": "minimal", "hk_ump_polymer_stock": "folding", "bt_mp5/ump_folding_stock": "folding",
    "rsa_sg58_polymer_humpback_stock": "fixed", "rsa_sg58_wood_humpback_stock": "fixed",
    "rsa_sg58_x_series_stock": "fixed", "rsa_sg58_adjustable_brs_stock_mount": "adjustable",
    "rsa_sg58_folding_spr_para_stock_body": "adjustable", "rsa_sg58_metric_para_folding_stock": "folding",
    "kalis_scalar_gen1_fsbl00_hinged_folding_stock": "folding",
    "kalis_scalar_gen2_late_folding_stock": "folding", "kalis_scalar_gen3_folding_stock": "folding",
    # shotguns, AUG, Remington 700 AICS
    "strikon_scr_high_impact_polymer_stock": "fixed", "strikon_scr_wooden_rifle_stock": "fixed",
    "magtap_moe_870_sga_polymer_stock": "fixed", "r870_sps_polymer_stock": "fixed",
    "mp133_153_plastic_stock": "fixed", "mp133_153_wooden_stock": "fixed",
    "lowenherz_aug_a3_austrian_stock": "fixed", "lowenherz_aug_a3_nato_stock": "fixed",
    "rbm_aug_carbon_fiber_stock": "fixed",
    "precision_intercontinental_roosevelt_700_sa_at_aics_gen2_folding_chassis_standard_stock": "precision",
    "precision_intercontinental_roosevelt_700_sa_at_aics_gen2_folding_chassis_thumbhole_stock": "precision",
    # braces and no-stock states
    "sb_tactical_vector_brace": "brace", "gxw_tailhook_mod1_brace_big": "brace",
    "gxw_tailhook_mod1_brace_small": "brace", "isle_mfg_veles_pt_1_tailhook_adapter": "brace",
    "thordsen_frs15_cover_stock": "brace",
    "kalis_scalar_pistol_pqdbl00_qd_sling_swivel": "no_stock", "ews_bufferless_system_ar15_castlenut": "no_stock",
    "rsa_sg58_pistol_qd_sling_endplate": "no_stock", "hk_mp5_endcap_sling_swivel": "no_stock",
    # sub-parts filed under "Stock" in Studio
    "rpl_20_cheek_pad_high": "cheek", "rpl_20_cheek_pad_low": "cheek",
    "kazarov_group_ak12_gen3_stock_cheekpad": "cheek", "kazarov_group_ak12_gen3_stock_cheekpad_extended": "cheek",
}

# Whole gun bodies: (handling, reload_points, stability, reason)
FURNITURE = {
    "mosin_standard_stock": (1, 0, 9.5, "full-length sniper stock: the steady reference"),
    "mosin_carbine_stock": (3, 0, 3, "shorter carbine stock: handier, less steady"),
    "mosin_promag_archangel_stock": (-6, 0, 12.5, "PRS chassis with cheek riser: steadiest, bulkiest"),
    "mosin_sawn_off_full_stock": (4, 0, -15, "cut-down furniture: handier, much less steady"),
    "mosin_sawn_off_stock": (1, 0, -20, "obrez, no buttstock: stockless sway; the old sheet did not call it handier"),
    "lowenherz_aug_a3_para_9x19_stock": (32, 12, 29, "9x19 conversion chassis (SMG): leans handling; old 40 kept within 6%"),
    "rogue_roosevelt_model_700_overmolded_bdl_full_bed_block_stock": (21, 8.5, 34, "full-length sporter stock"),
    "magtap_hunter700_short_action": (16, 9.5, 46, "precision stock with riser and LOP spacers: steadier, bulkier"),
    "glr_17": (-11, 0, 3.5, "shoulder stock on a pistol: steadier, much slower to bring up"),
}

PAD_WORDS = ("buttpad", "butt pad", "stock pad", "recoil pad", "shoulder pad", "cloth")
CHEEK_WORDS = ("cheek", "riser", "spacer")
BRACE_WORDS = ("brace", "tailhook")
HOST_WORDS = ("adapter", "tube", "mount", "hinge", "lock", "endplate", "end plate", "endcap", "castle",
              "base", "part", "rail", "block", "piece", "connector", "extendable", "extension", "plank",
              "retractor", "body", "swivel")


def kind(item):
    n = item["name"]
    if n in FURNITURE:
        return "furniture"
    if n in TYPES:
        return TYPES[n]
    cat = (item["category"] or "").lower()
    words = (cat + " " + item["pretty"].lower() + " " + n.replace("_", " "))
    if any(w in cat for w in PAD_WORDS):
        return "pad"
    if any(w in cat for w in CHEEK_WORDS):
        return "cheek"
    if any(w in words for w in BRACE_WORDS):
        return "brace"
    if cat != "stock" and any(w in cat for w in HOST_WORDS):
        return "host"
    for t, ws in (("precision", ("precision", "sniper", "prs")), ("minimal", ("skeleton", "pdw", "minimal")),
                  ("folding", ("folding",)), ("fixed", ("fixed", "wood"))):
        if any(w in words for w in ws):
            return t
    return "adjustable"


def assembly_weight(item, ctx, depth=0):
    """Own weight plus the default stock-family parts it brings (extendable parts, buttpads...)."""
    w = item["weight"] or 0.0
    if depth > 8:
        return w
    for e in item["studio"].get("map") or []:
        d = e.get("default")
        child = ctx.items.get(d) if d else None
        if child and child["family"] == "stock":
            w += assembly_weight(child, ctx, depth + 1)
    return w


def weight_lean(item, ctx):
    rivals = [c for c in ctx.competitors(item) if kind(c) in LEAN and (c["ergonomics"] or 0) > 0]
    ws = sorted([assembly_weight(c, ctx) for c in rivals] + [assembly_weight(item, ctx)])
    ref = ws[len(ws) // 2] if len(ws) >= 3 else REF_WEIGHT
    return max(-0.5, min(0.5, (assembly_weight(item, ctx) - ref) / 0.2))


def finish(h, r, s, why):
    return {"handling": round_half(h), "reload_points": round_half(r), "stability": round_half(s), "_rule": why}


def lean_split(item, ctx, t_type, k):
    e = item["ergonomics"]
    t = max(-1.5, min(1.5, t_type + weight_lean(item, ctx)))
    h = round_half(min(H_CAP, (0.83 - 0.25 * t) * e))
    r = round_half(R_FRAC * e)
    s = (e - 0.6 * h - 0.4 * r) / 0.47
    return finish(h, r, s, f"stock {k}: lean {t:+.2f} (type {t_type:+.1f}, weight {t - t_type:+.2f})")


def restat(item, ctx, base):
    e = item["ergonomics"] or 0.0
    k = kind(item)
    if k == "furniture":
        h, r, s, why = FURNITURE[item["name"]]
        return finish(h, r, s, f"furniture table: {why}")
    if abs(e) < 1e-9:
        return finish(0, 0, 0, f"stock {k}: zero stays zero")
    if k in LEAN and e > 0:
        return lean_split(item, ctx, LEAN[k], k)
    if k == "brace":
        return finish(1.3 * e, R_FRAC * e, -0.1 * e, "brace: handling 1.3E, stability -0.1E (gives up ~15% EV)")
    if k == "no_stock":
        h = NO_STOCK_HANDLING
        s = max(-14.0, min(-6.0, (e - 0.6 * h) / 0.47))
        return finish(h, 0, s, "no stock: handling 18, stability carries the rest (clamped -14..-6)")
    if k == "pad":
        return finish(0, 0, e / 0.47, "pad: stability only")
    if k == "cheek":
        h = round_half(-e / 3)
        return finish(h, 0, (e - 0.6 * h) / 0.47, "cheek weld / LOP: stability, small handling cost")
    if e < 0:
        return finish(0.9 * e, 0, 0.95 * e, f"stock {k}: negative = extra length and joints (h 0.9E, s 0.95E)")
    h = round_half(0.3 * e)
    return finish(h, 0, (e - 0.6 * h) / 0.47, f"stock {k}: small rigid part, mostly stability")
