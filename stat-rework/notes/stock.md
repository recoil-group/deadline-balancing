# Stock family: notes

224 items. Rules are in `rules/stock.py`. There are 3 overrides, in `overrides/stock.csv`. E is
old ergonomics. EV is 0.6 h + 0.4 r + 0.47 s. There is no weight credit.

## Rules applied

**Value-carrying stocks.** These are the parts of an assembly that carry its ergonomics: the
stock, or the base, connector or mount part that holds the assembly's value.

- Each one gets a lean `t`, made of two parts:
  - **Type lean:** precision +1, fixed +0.5, adjustable 0, folding −0.5, minimal, PDW or
    skeleton −1.
  - **Weight lean:** ±0.5 per ±0.1 dw of *assembly* weight. Assembly weight is the part plus its
    default stock-family sub-parts, such as extendable parts, buttpads and cheek pieces. It is
    measured against the median of the stocks it competes with. A fixed 0.25 dw is used when
    there are fewer than 3.
- `t` is clamped to −1.5…+1.5. The split is:
  - reload 0.25 E;
  - handling (0.83 − 0.25 t) E, capped at 22;
  - stability takes the rest, so EV equals E.
- Examples in the AR receiver-extension set:
  - PRS Gen3 is h 8 / s 24.5.
  - M4SS is h 13.5 / s 13.5.
  - Viper MOD1 is h 21 / s 7.5.
- Types are a name table in the rule, with keyword fallbacks. Each AR, AK, SCAR, G3, MP5, SG58,
  shotgun and AICS stock was placed by name.
  - Minimal: Viper, XM177, SL-K, Talvern PDW, 607 CAR-15, KF416C, AKS-74U, PT-1 Klassika, SCAR
    SC, MP5A3, Cartman.
  - Folding: AK-74M 6P34, Vityaz, Zhukov-S, UMP, Scalar hinged stocks, SG58 metric para, G3A3
    retractable.
  - Precision: PRS Gen2 and Gen3, MCS V5, Tabuk, PSG1, SSR, Spuhr R-410, AICS.
  - Fixed: AK wooden and polymer fixed, A2, UBR, HRS Light, CQR, FRS-15, humpbacks, X-series,
    G3 and MP5 fixed, the shotgun stocks, the AUG A3 stocks, RPL-20.
  - Everything else is adjustable.

**Braces and tailhooks.** This covers the SB brace, both GXW tailhooks, the Isle tailhook adapter
and the FRS-15 buffer-tube cover.

- Split: h 1.3 E, r 0.25 E, s −0.1 E.
- EV drops about 15%. Keeping the full value with negative stability would need handling of
  about 28 or more.
- The SB brace is h 23.5 / s −2. A tube plus a carbine stock is about h 12 / s 12.

**No stock.** This covers the Scalar QD sling swivel, the EWS bufferless kit and the SG58 QD
sling end plate.

- Handling is 18, about what the handiest stocks reach.
- Reload is 0.
- Stability is (E − 10.8)/0.47, clamped to −14…−6. The result is s −12.5 to −14.
- A stockless gun has to be handier than a stocked one or it is never chosen. Its price is sway,
  on top of the old +7…+10 recoil and +0.5 deviation, which are unchanged.
- EV rises by up to +1.2 (EWS: 3 → 4.2).
- The stockless MP5 end cap is an override: h 21, s −5, EV 10 against an old 12.

**Buttpads, stock pads and recoil pads.** Stability only: s = E/0.47. E 1 gives s 2, and E 2
gives s 4.5.

**Cheek rests, cheek pads, risers and spacers.**

- Split: h = −E/3, and s carries the rest.
- Hunter .25/.5/.75 risers and CQR 15/30/45 mm spacers come out as 0/+1, −0.5/+3, −0.5/+4.
- The AK-12 extended cheek pad and the high RPL-20 pad are h −1.5 / s 10.5.

**Tubes, adapters, mounts, hinges, locks, end plates and base parts.**

- Zero stays zero.
- A negative value means extra length and joints: h 0.9 E, s 0.95 E, r 0. Examples:
  - R870 LEO adapter: −6.5 / −6.5.
  - FARO SCAR adapter: −3.5 / −4.
  - Buffer tubes: −1…−2.
- A small positive value on a rigid adapter goes mostly to stability. The 3D-printed fixed ACR
  adapter is h 1 / s 7.

**Full furniture.** These are set by a table in the rule:

| Item | h | r | s | EV | Old E |
|---|---|---|---|---|---|
| Mosin standard | 1 | 0 | 9.5 | 5.1 | 5 |
| Mosin carbine | 3 | 0 | 3 | 3.2 | 3 |
| Mosin Archangel | −6 | 0 | 12.5 | 2.3 | 1 |
| Mosin sawn-off full | 4 | 0 | −15 | −4.7 | −5 |
| Mosin obrez | 1 | 0 | −20 | −8.8 | −10 |
| AUG Para conversion | 32 | 12 | 29 | 37.6 | 40 |
| R700 BDL | 21 | 8.5 | 34 | 32 | 34 |
| Magtap Hunter 700 | 16 | 9.5 | 46 | 35 | 38 |
| GLR-17 (pistol shoulder stock) | −11 | 0 | 3.5 | −5 | −5 |

- Mosin reload is 0 because its stripper-clip reload does not touch the stock.
- The old sheet did not treat the obrez as handier, so it keeps only its stability loss.
- The other three AUG A3 stocks use the fixed rule (Austrian h 12 / s 17, RBM carbon h 14.5 /
  s 23.5).

## Overrides (3)

- `hk_mp5_endcap_sling_swivel` h 21 / r 0 / s −5: the no-stock clamp left EV at 8 against an
  old 12.
- `hk_psg1_stock_base` h 7 / r 5 / s 29.5: the rule tied it with the standard G3 fixed stock on
  handling (9).
- `rsa_sg58_metric_para_folding_stock` h 13 / r 3.5 / s 8: the rule tied it with the SPR Para
  body on handling. The folding stock should be the handier one.

## Check results

- **EV drift:** 0 items outside the band.
- **Dominations:** 1 item is dominated. `kf_416a5_sling_eyelet_endplate` is 0/0/0 like the other
  end plates but 0.01 dw heavier. That weight is the old sheet's tiny-part inflation: it is a
  visual variant with a sling eyelet.
- **Best on all three stats:** 3 items, none of them a like-for-like case.
  - `kf_416a5_extended_castlenut` (+1 s): its rivals are buffer tubes that host other stocks.
  - `lowenherz_aug_a3_para_9x19_stock`: a 9x19 conversion with different child slots
    (magazine, barrel, gas block).
  - `hk_mp5a2_plastic_fixed_stock`: its rivals are 0-stat end caps that host the A3 and Cartman
    stocks (A3 is h 13.5 / s 5.5; the Cartman base and stock are h 11 / s 3).

## Magnitudes and open questions (decided, flagged for the lead)

- **Large values on a few items.** Most stocks stay within ±25 per stat. Three items exceed
  ±20, because keeping EV forces it:
  - Hunter 700: s 46.
  - R700 BDL: s 34.
  - AUG Para: h 32, s 29.
  - These sit in required slots, so weapon calibration absorbs the absolute level. Only the
    differences against the receiver-family chassis that compete with them matter: MCS LSS-XL,
    REV21 and the AICS frame plus AICS stock.
  - An alternative is to scale the R700 stocks down and let the base absorb the rest, but only
    if the receiver agent does the same with those chassis.
- **Reload is kept at 0.25 E on every stocked option.** So a stockless option has 3–5 points
  less reload than a stocked one (about 2% reload speed). I left this in rather than add reload
  to no-stock parts, which have none physically.
- **Braces give up about 15% EV.** This is deliberate (see above).
- **Unreachable items** still follow the rules:
  - `tsa_g` (E −15, recoil +7/+7, unknown part) falls to the negative rule: −13.5 / 0 / −14.5.
  - `bt_mp5/ump_folding_stock` is folding.

## Misfiled or cross-family items

- `thordsen_frs_15_stock`, `hera_arms_cqr_gen1_pistol_grip_stock` and
  `hera_arms_cqr_gen1_ak_stock` sit in pistol-grip slots and compete with plain grips. They are
  re-statted as fixed stocks, leaning to stability (FRS-15 h 8 / s 16.5; CQR h 6 / s 11.5).
- **Stockless options in other families.** These should follow the no-stock rule (high handling,
  stability about −6…−14) so that they agree with mine:
  - `agr_870_protection_cap`, filed as `optic`;
  - `mp133_153_plastic_pistol_grip` and `r870_earthquake_raptor_pistol_grip` (`pistol_grip`),
    all E 14 with positive recoil;
  - `thorsden_frs15_gen3_ar15_endplate` (`receiver`, E 2, +9/+9).
- `hunterstock_lop_0.5_*` (`misc`) are length-of-pull spacers. My cheek/spacer rule would give
  E 0.5 → h 0 / s 1. The misc owner should match this.
- Castle nuts and end plates filed under `receiver` were left alone, as instructed.

## Round 5: reload scope

Stocks are not reload parts. The reload share every stock had (0.25·E, and the furniture table's reload, e.g. the AUG Para conversion's 12 points) is moved into handling and stability in the proportions the stock already has, so EV is kept (`reload_scope.py`, RULES.md section 13). 89 stocks moved. The AUG Para conversion arguably changes the magazine well (9x19 mags); it was zeroed with the rest, and its preset now reaches handling 100.5.
