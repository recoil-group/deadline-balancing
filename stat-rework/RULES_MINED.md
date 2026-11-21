# Unwritten balancing rules in the current sheet

Mined 2026-11-21 for the stat rework (ergonomics split into `handling`, `reload_speed`, `stability`; weapon weight takes over draw/stow, sprint-out, aimed move speed, aim stamina and turn lag at about 15.4 mobility points per dw).

## How this was made, and what to trust

- **Current values:** `balancing.csv` 0.25.4 (Nov 15 2026) through `stat-rework/data/items_index.csv` (2,595 rows) and `competing_sets.json` (1,062 slot groups, 477 once duplicates are removed).
- **History:** the `archive/` snapshots from 0.22.12 to 0.25.3, with names mapped through `renames.csv`; the formulas and notes in the `changes/*.xlsx` sheets; and the balancing repo's git log of 1,656 commits. The generated `changelogs/*.md` are pure diffs and contain **no designer prose**. All the "why" below comes from commit messages, change-sheet notes and change-sheet formulas.
- **Method:** most statistics are computed inside competing sets (items that fill the same slot), not over whole families. "e/dw" means the least-squares slope of ergonomics against weight within one set, and "median" means the median over sets. Recoil is reported as the average `(h + v) / 2`.
- **Family labels are heuristic.** Section 11 lists the misclassifications found. They are small enough that the family medians hold, but check the slot before re-statting a specific item.
- **Not covered:** these are rules *read off the data*. Nothing was playtested, and Studio-side `property_patch` effects were not examined.

---

## 0. The rule behind most of the sheet: the team's "strength" score

Almost every attachment change sheet has a `strength` column with essentially the same formula. Examples are `changes/template.xlsx`, `m4-handguards.xlsx`, `ak-stocks.xlsx`, `optics.xlsx`, `foregrips.xlsx` and `556-mags.xlsx`:

```text
strength = ergonomics − 20·weight − 0.8·h_recoil − 0.6·v_recoil
           − (5…15)·barrel_deviation + (5…40)·bullet_damage + bullet_velocity/(200…300)
           − 5·muzzle_loudness            (+ capacity/1.3 on 556/9mm mag sheets)
```

The ammo "super" sheets (`*-ammo-super.xlsx`, sheet `Model`) state the same weights as a table: ergonomics 1, weight −20, h −0.8, v −0.6, deviation −10, damage 10, velocity 0.005 ("1 point per +200 vel"), fire_rate 10, loudness −5, price 0 ("excluded from performance strength").

What the formula implies:

- **1 dw is worth 20 ergonomics points today, and the team prices weight explicitly.** 0.05 dw is worth 1 ergo point, which the commit "steel mags .05 weight for 1 ergo" (0318104) states outright.
- 1 ergo ≈ 1.25 h recoil ≈ 1.67 v recoil. One point of average recoil (h and v each −1) is worth 1.4 ergo.
- **Price carries zero weight in strength.** Price is meant to be orthogonal (see section 6).
- Within competing sets, the formula equalizes items best **when weight is valued at 20/dw**. The median spread of strength within a set (SD):

| Family | weight valued at 0 | at 20 | at 35 (≈ 20 + new mobility) |
|---|---|---|---|
| barrel (12 sets) | 3.6 | **1.0** | 2.4 (heavier is now clearly weaker: r = −0.96) |
| handguard (15) | 1.8 | 1.5 | 1.8 (heavier now weaker: r = −0.59) |
| muzzle (15) | 3.1 | 2.9 | 2.6 |
| optic (9) | 1.2 | 1.9 | 2.6 |
| magazine (9, incl. capacity) | 3.6 | 4.7 | 6.0 (the formula never equalized mags) |
| stock (12) | 14.0 | 12.3 | 11.2 (stockless options dominate the spread) |

**Consequence for the rework:** barrels, and to a lesser degree handguards, were balanced on the assumption that weight already costs 20 points per dw through travel speed. If weight also starts costing mobility, heavy barrels and long handguards lose relative strength unless something is given back. This is the clearest double-charge, and it is caused by weight being priced *in addition to* ergo, not by ergo standing in for weight (see section 3).

---

## 1. Per family and slot

### Stocks (`stock`, 224 rows)

- **Having a stock is worth about +14…+18 ergo and −6…−12 h / −6…−19 v.** This is the largest single ergo source in a build: about +14 on average in stock long-gun builds, where the weapon row gives +30 and handguards +6.
- AR receiver-extension stocks (`rail:stock:stock`, 17 items) are flat on ergo: 14–18, covering `si_viper_mod1_stock` 18 @ 0.14 dw, `hart_m4ss_stock` 16 @ 0.20 and `magtap_prs_gen3_stock` 18 @ 0.33. They differ mainly in recoil and weight. The e/dw is +24 (r 0.45), so **heavier stocks are not penalized in ergo; they come with more recoil reduction** (rec/dw −35, r −0.76).
- AK fixed stocks: all 13–21 (`kazarov_akm_wooden_6p1_sb5` 15, −9/−12 @ 0.29; `al_qadissiya_tabuk_sniper_wooden_stock` 21). The same set holds the zero-stat adapters, locks and hinges.
- **Stockless and pistol-brace states:** a buffer tube, castle nut or sling swivel alone. Examples:
  - `hart_a2_buffer` −2.
  - `ews_bufferless_system_ar15_castlenut` +3 with +7/+10 recoil and +0.5 deviation.
  - `kalis_scalar_pistol_pqdbl00_qd_sling_swivel` +5 with +7/+7 and +0.5 deviation.
  - **Rule:** no stock gives roughly 0…+5 ergo, a large recoil penalty and **+0.5 barrel deviation**.
  - Mosin `mosin_sawn_off_stock` −10 ergo with +5/+5: removing the buttstock costs ergo here, so stockless is not treated as "more handy".
- Precision stocks take −0.05 deviation (`magtap_prs_gen2/3`, `mcs_v5_skeleton_*`, `hk_psg1_stock_base`, `aft_ssr_stock_assembly`).
- Sub-parts (buttpads, cheek rests, spacers) carry 0…+1.5 ergo, or nothing. Since Oct 2026 **assembly ergo and recoil sit on the gun-contact node, and sub-parts carry weight only**. See commits 6203675, ef7037c, 60ad191, fe20f7b and 962b0c0 ("move sub-part ergonomics onto the base part").
- Usually zero: velocity, damage, loudness, fire rate.
- Outliers that are really chassis: `lowenherz_aug_a3_para_9x19_stock` 40 ergo (+0.35 deviation), `rbm_aug_carbon_fiber_stock` 22. Mosin stocks are full furniture (−10…+5 at 0.5–0.95 dw).

### Handguards (`handguard`, 340 rows, including rail panels)

- **A handguard is worth about +10…+17 ergo and −5…−15 per recoil axis.** Ergo falls and recoil reduction rises with length:
  - M4 set (54 items): **−3.0 ergo and −2.9 average recoil per 100 mm**, +0.07 dw per 100 mm.
  - Examples: 4" Quix 14 (−2/−5), 7" 15–16, 10" 11–13, 12–13" 7–9, 15" 6–9, 18" `sp18m` 5 (−12/−20).
- AK lower handguards: 6–17. Wooden issue parts sit at the top (`kazarov_akm_wooden_6p1_sb6_1_lower_handguard` 15, −7/−9 @ 0.12; `cugir_pm_md63_wooden_sharkfin_bottom_handguard` 17). Long railed systems sit at the bottom (`tdiarms_ak_x47_rail_system` 6 @ 0.36).
- **Drop-in (non free-float) handguards get +0.03 barrel deviation.** Examples: `hart_m4_std_carbine_plastic_handguard`, `usgi_m16a1_triangle_handguard`, `pac_ras_m4a1_handguard`, the wooden and Belgian SG58 handguards. `kf_416_dmr_extra_long_handguard` gets −0.05.
- Top covers, rails and side rails: −1…+1. **Side-rail ergo penalties were deliberately removed** (c864e5c "mk17/20 side rail ergo penalty removed", 166a088, 199fdb1 "Vector Side Rails −1→0").
- History: `changes/handguard-recoil.csv` added "+4 +4 recoil to every handguard to account for the muzzle device buff". Handguard recoil is tuned *relative to muzzle devices*.
- Usually zero: velocity, damage, loudness.

### Rail panels and covers (flag `is_rail_panel`, 70 rows; only the first four count)

- **Panel covers carry positive ergo proportional to weight: 1 ergo per 0.04 dw** (6507df1 "rail panels: 1 ergo per 0.04 weight"; earlier be2462d "1:.03 exchange"). Examples: `magtap_xtm_enhanced_panel_1` 0.5 @ 0.02, `xtm_4_piece` 1.75 @ 0.07, `axtell_defense_5inch_picatinny_rail_panel` 1.5 @ 0.06. Cosmetic CGR panels are 0.5 @ 0.02 at 1000 credits.
- **MLOK and picatinny rail *sections* are a flat −0.5 ergo**, with weight scaled by slot count. In 0.25.3 they went from −2 to −0.5 while weights went from a flat 0.06 to 0.05–0.13 (`generic_*_slot_mlok_rail_*`). The ergo cost was moved into weight.
- These are the only items where ergo is a literal function of weight. A panel's ergo is grip comfort, not stability.

### Pistol grips (`pistol_grip`, 66 rows)

- **+3…+10 ergo and −1…−7 per recoil axis.** AR set median ergo 6, recoil −3/−3.
- Ergo *rises* with weight (e/dw +20…+86): rubberized grips and grips with a palm shelf or trigger guard are better. Examples: `axtell_defense_pistol_grip_with_trigger_guard` 10 @ 0.13; `mcs_premier_avp_grip` 9, 0/−1; `ecm_gunslinger_mod3` 8.
- **Era and "cool" tilt:** `hart_a1_chopped_pistol_grip` 3, `hart_a1` 5, `hart_a2` 6, modern MOA/Gunslinger/Orion 7–9. The California-compliant `behemoth_tacticals_featureless_grip` gets 0 ergo but −6/−2.
- Within a set, ergo and recoil trade loosely: ergo plus average recoil reduction ≈ 9–11.
- Usually zero: everything except ergo, weight, recoil and price.

### Foregrips, handstops and index panels (`foregrip`, 79 rows; only the first grip counts)

- **Handstops and index panels: a flat +6 ergo, 0…−2 recoil.** Examples: `magtap_xtm_enhanced_handstop_1`, `veles_rl_1_handstop`, `magtap_mlok_index_panel`; a60a349 "xtm enhanced short handstop: grip stats (6 ergo, 0.02…)".
- **Vertical and angled grips: +1…+5 ergo with −2…−6 h** (`pac_vpg` 2, −6; `atg_super_slim_vertical_foregrip` 5, −1). The trade is ergo + h reduction ≈ 7–8.
- Weight is not charged in ergo. `hera_arms_cqr_gen1/2_foregrip` is 6 ergo at 0.23 dw.
- **Bipods: −3…−4 ergo with small recoil reduction** (`harrison_hbr_base` −4 @ 0.20; `lowenherz_aug_hbar_folding_bipod` −3). Their payoff is in `bipods.csv`; f210f61 "buff bipods stamina bonus". The grip-pod body is 0 ergo with no recoil (a0c2292 "make grippods make your recoil worse", then ed1ad59).

### Barrels (`barrel`, 198 rows)

- **The default barrel is the zero reference.** Shorter barrels gain ergo and lose velocity, damage, accuracy and recoil reduction; longer barrels do the opposite.
- Per 100 mm within sets:

| Set | ergo | dw | avg recoil | velocity | damage | deviation |
|---|---|---|---|---|---|---|
| M4 (15) | −4.1 | +0.16 | −3.5 | +141 | +0.11 | −0.16 |
| AUG (9) | −3.7 | +0.16 | −3.7 | +97 | +0.08 | −0.09 |
| MP133 (13) | −3.5 | +0.12 | −2.6 | +72 | +0.09 | −0.10 |
| SA58 (7) | −7.2 | +0.21 | −5.3 | +135 | +0.05 | −0.18 |
| R870 (10) | −1.2 | +0.11 | −1.4 | +84 | +0.07 | −0.09 |

- Within-set e/dw ≈ **−24** (median of 27 sets, r −0.97) and rec/dw ≈ −21. Ergo, weight, recoil and velocity are all near-linear in length (|r| ≥ 0.94).
- Extremes: `custom_2inch_ar15_barrel` +6, +5/+5, −866 vel, −0.4 damage, +5 deviation; `cmmg_ar_15_5.56x45_610mm_fluted_r_barrel` −12, −16/−16, +262, +0.3.
- Short-gas barrels get +fire_rate (`hart_m4a1_5.56x45_190mm` +0.03, `custom_2inch` +0.125). Rifle-gas barrels get −0.03…−0.06.
- **Barrel weight is the most realistic in the sheet** (ratio to real 1.04), and it was raised 40% from 0.22.12 while mean barrel ergo moved from −1.0 to 0.0.

### Muzzle devices (`muzzle`, 142 rows; only the *last* device counts, but every device's weight counts)

Typical values by type (medians):

| Type | ergo | dw | h / v | velocity | deviation | damage | loudness | price |
|---|---|---|---|---|---|---|---|---|
| Flash hider | **+1…+2** | 0.07 | −10…−11 / −11…−12 | 0 | 0 | 0 | 0 | 500 |
| Compensator | 0 | 0.08 | −7 / −10 | +10 | 0 | 0 | 0 | 500 |
| Muzzle brake | **−1** | 0.08–0.10 | −13…−15 / −13…−14 (more horizontal) | 0…+10 | 0 | 0 | **+0.04** | 600–750 |
| Suppressor | **−5** (−1…−5 in 5.56) | 0.23 | −13 / −13 | +40…+80 | −0.04…−0.13 | +0.04…+0.12 | **−0.08…−0.20** | 1500–3500 |

- **Brake vs flash hider at the same weight differ by about 3 ergo.** That is blast and concussion, not weight.
- Thread adapters and barrel extensions: −1…−3 ergo, +0.05…+0.2 deviation (`ips_5.56x45_4inch_barrel_extension` −3).
- Suppressor ergo grows with can length and weight within a set (e/dw −16…−40), while weight is deliberately compressed (section 2). 2706fae: sleeve suppressors keep a "slightly lower" strength because they are "considerably shorter" — **shortness itself is valued.**
- Muzzle-device ergo penalties softened over time: the mean went from −3.1 in 0.22.12 to −1.45 now, as weights rose.

### Optics and mounts (`optic`, 360 rows)

- **Mounts, risers and spacers: 0 ergo** (since 0.25.4: 38 mounts went from −0.5/−1 to 0; f0db2dc "make risers and some scope mounts free"; 7a3a261 "Corvus mounts. Not supposed to take ergo"). A few mounts keep −0.5…−4.5 for bulk.
- **Optic ergo is set by class, not weight.** Regressing optic ergo on magnification and weight gives a weight coefficient of only about −1.7 per dw.
  - 1x red dots and reflexes: −1…−2 (big ones −6/−7: `gunther_mrs_red_dot_sight`, `emberfield_mg_kemper_xl_reflex_sight`).
  - Holos: −1…−2.
  - **Fixed-magnification prisms and scopes: a flat −3**, from 0.10 dw (`virticon_compact_arcs_3x24_ta50c`) to 0.33 dw (`elcan_c79a2` −2.5).
  - LPVOs and big scopes: −5…−7 (`holotec_vudu_1_6x24` −6, `nightforce_atacr7_35x56_f1` −7).
  - NV scopes: −7…−8.
  - Magnifiers: −1.
- Optics carry small vertical recoil reduction (−1…−4) from mass. Horizontal is almost always 0 (H/V 0.07).
- Eye cups give +1…+5. Two red dots carry +0.25 deviation.

### Iron sights (`iron_sight`, 175 rows; only the first two count)

- **+1 ergo per sight, folded or not**, since 0.25.2 (22 sights went from 2–3 to 1; 9a43e1b "port irons ergo reduction"). Two sights give +2 per build.
- Carry handles +3…+4 (`tristar_compact_carry_handle` 7 → 4); sight bases and blocks 0…+2. Weight about 0.01. Price is usually 0.

### Receivers, slides and dust covers (`receiver`, 223 rows)

- Lowers and uppers: 0 ergo for the default, aftermarket 0…+6. Recoil is mostly 0, ±1…3. Weight 0.25–0.5 (realistic, ratio 1.0–1.04).
- **Aftermarket receivers are mild upgrades:** 75% of alternatives score above the default. Examples: `noveske-lower-buff.csv` 2 → 5 ergo plus −2/−1; AK dust covers with rails +3…+8.
- Pistol slides: +1…+4. Cutout slides cost more than flat ones (0b8cf52).

### Internals (`internals`, 243 rows) and small parts

- Defaults are 0 (83%). **Upgrades are pure ergo:**
  - charging handles +2 (up to +5)
  - triggers 0…+4 (precision triggers also −0.02…−0.06 deviation, AR match triggers +0.03…+0.05 fire rate)
  - fire selectors +0.5…+2
  - trigger guards +2…+3
  - gas blocks 0…+3
- Weight about 0.01–0.15 and inflated for tiny parts (section 2). These are the main "free ergo" sources in a min-maxed build. Together receiver and internals average +3 ergo even in stock builds.

### Tactical devices (`tactical`, 38 rows)

- **Lights: 0 ergo. Lasers and combo units: −0.5…−2 ergo** with −1…−3 vertical recoil from front mass. Weight is compressed (3049a9e "x300 … lighter than in real-life"). Price is high (500–4000).

### Bayonets (`bayonet`, 11 rows)

- Blades: −3…−4 ergo, −4…−5 v, +0.05 deviation, 0.19–0.25 dw. Grips and slings +1 each. The July 2026 "bayonet buff pass" raised these.

### What is "usually zero" (a column carries a value in under 10% of rows)

| Column | Where it carries values |
|---|---|
| `bullet_velocity`, `bullet_damage` | Barrels, muzzles, ammo only |
| `barrel_deviation` | Barrels, muzzles, ammo; the stock/handguard/trigger/receiver exceptions listed above |
| `muzzle_loudness` | Muzzles, a few barrels, subsonic ammo |
| `fire_rate` | AR triggers, short-gas barrels, auto sears (`kosch_metal_auto_sear` +0.71), UMP9 upper |
| `magazine_capacity` | Magazines and mag extensions |
| `horizontal_recoil` | Rare on optics, internals, mag parts |

**No current `fire_rate` part reaches a bolt or pump gun**, so the contract's "fire_rate now drives cycling" changes nothing in the existing data.

---

## 2. Weight vs real world

The conversion is 1 dw = 1.18 kg = 41.7 oz; 0.024 dw = 1 oz.

The change sheets record "irl weight (oz)" and the formula used to convert it. Across 143 items that match the current sheet, the ratio of sheet weight to real weight is:

| Family | median ratio | spread (p10–p90) | conversion formula in the sheets |
|---|---|---|---|
| barrel | 1.04 | – | `oz × 0.024` |
| handguard | 1.07 | 1.01–1.07 | `oz × 0.024` (`ak-handguards.xlsx`) |
| receiver / dust cover | 1.04 | 1.01–1.39 | `oz × 0.024` (`dovetails-dustcovers.xlsx`) |
| magazine (loaded) | 0.88 | 0.79–0.95 | 5.56: `oz × 0.024`; 9mm: `oz × 0.022 + 0.02` |
| muzzle / suppressor | 0.83 | 0.62–1.01 | **`oz × 0.015 (+0.03)`** (`556-muzzles`, `545-muzzles`, `308-barrels-muzzles`, `45-muzzles`) |
| stock | 0.80 | 0.44–1.04 | `oz × 0.024`, but a few rows use `oz × 0.015 + 0.15` (`m4-stocks.xlsx`) |
| optic | **0.60** | 0.49–1.11 | **`oz × 0.013 + 0.02`** (`optics.xlsx`, "sight weight formula" in `dovetails-dustcovers.xlsx`) |

Deviations and the reasons they appear to exist:

- **Suppressors and muzzle devices are compressed to about 60% of real weight plus a 0.03 floor.** Big cans are lighter than real; flash hiders end up slightly *heavier* than real (`jg_usgi_a2_birdcage` 1.32×, `pac_qdc_3prong` 1.27×).
- **Heavy optics are compressed** (`nightforce_atacr7_35x56_f1` 0.45×, `npz_usp_1_4x_1p29_tulip` 0.50×, `monstrum_tactical_s232p` 0.44×). The +0.02 floor makes micro dots heavier than real (`swampfox_kingslayer` 1.67×).
- **Heavy precision stocks are compressed** (`mcs_v5_skeleton_rifle_stock` 0.42×, `magtap_prs_gen3_stock` 0.49×). dab7c5f notes that the other FAL stocks "are lighter than irl anyway".
- **High-capacity mags are under-weighted.** Standard mags are close (`5.56x45_magtap_pmag_m3_30r` 0.41 dw = 0.48 kg loaded). Drums run light (`7.62x39_rwb_ak47_100r_drum_mag` 1.86 dw = 2.2 kg, well under a loaded 100-round drum). The 0.24.0 rework raised many mag weights toward real (`springfield_armory_m14…20r` 0.39 → 0.63, `sgm_tactical_saiga308_20r` 0.40 → 0.57).
- **Tactical devices are lighter than real** (stated for the X300).
- **Tiny parts are inflated:** a 0.01–0.02 floor, so castle nuts are 1.39× and buttpads 1.25×. This makes small parts "cost" something.
- **Ammo weight is a damped delta from the default load:** 4df74b2 "make bullet weights less exaggerated (80gr/30 bullets to 0.01 weight)". Values range from −0.16 to +0.13, with subsonic and heavy loads positive. One exception: e45bc7a set the Bramit subsonic to 0.
- **Weapon base rows carry 0 weight** (moved to parts in 0.25.3: AK12 0.6, AK308 0.75, SA58 0.75, R870/MP133 0.9 → 0). Exceptions are `Glock20` 0.4 and `Turret` 3.0.
- **Long-run drift toward realism:** from 0.22.12 to 0.25.4 total weight rose 40% for barrels, 37% for magazines, 35% for receivers, 50% for internals and 19% for stocks. Optics stayed flat.
- **Built weapons land near real loaded weights, with SMGs and battle rifles slightly light.** M4A1 stock build 2.76 dw (3.3 kg), MP5 2.28 (2.7 kg), AK_9 2.16, G3 3.91 (4.6 kg), SA58 3.95, SCARH 3.51, Mosin 3.36, RPG7 5.80 with a 1.2 dw HEAT warhead (lighter than real). These real-world comparisons are approximate.

---

## 3. Does negative ergonomics stand for weight? (double-charge candidates)

**Short answer: rarely *purely*.** In most families negative ergo tracks a physical *size* variable (length, capacity, magnification class) that happens to correlate with weight. Weight is already charged separately at 20 points per dw in the team's scoring (section 0).

Within-set ergo per dw (median over sets with at least 4 items of the family):

| Family / set | e/dw | r | What the ergo actually tracks |
|---|---|---|---|
| Magazines (10 sets) | −14…−40 (median −23) | −0.87…−0.99 | **Capacity.** Capacity alone explains R² 0.93–0.98. With capacity held fixed, the weight coefficient is ≈0 or *positive* (+6…+31/dw). |
| Shotgun tube extensions (`magazine_12g_r870`) | −52 | −0.99 | Capacity: 11 at stock, then −2 per extra round (`dragoon_systems_lsx_8rnd_extension` −1) |
| Pistol mag extensions (`magex2`, `+5` plates) | −26 | −0.91 | Capacity: about −0.4 ergo per round (`kalis_kosch_9x19_23r_magex2` −10) |
| Barrels (27 sets) | −24 | −0.97 | **Length.** Barrel weight is real, so length and weight are interchangeable here. |
| Suppressors and muzzles (20 sets) | −14…−40 (median −30) | −0.83 | Device type (brake −1, flash hider +2) plus can length |
| Handguards, M4 / KF416 / G3 sets | −40 / −35 / −47 | −0.8…−0.9 | **Length** (−3 per 100 mm) |
| Handguards, AK, SA58, SCAR and others | −19…+13 | ≈0 | Nothing; flat |
| Optics on picatinny rails (3 big sets) | −15 | −0.70 | **Class** (1x vs magnified vs NV), not weight |
| Foregrips (mlok/pic sets) | −28…−96 | −0.66…−0.97 | Grip type (handstop vs vertical); the weight range is tiny (0.02–0.11) |
| Bayonet blades, bipods | about −20 | – | Bulk on the muzzle |
| Stocks | **+24…+100** | +0.45…+0.94 | "Has a real stock"; heavier stocks are *better* |
| Pistol grips | **+20…+86** | +0.3…+0.8 | Fuller grips are better |
| Rail panel covers | **+25** (rule) | 1.00 | Coverage |
| Internals, small receiver parts | +25…+60 | +0.5…+0.8 | Upgrade parts are heavier and better |

Where a re-statter should expect double-charging after the rework:

1. **Barrels: the strongest case.** A 20" M4 barrel against the 14.5" default is −9 ergo and +0.23 dw today, which equals strength at 20/dw. After the rework the same barrel also pays about −3.5 mobility. Of today's −4 ergo per 100 mm:
   - the strafe-sway part belongs in `stability` (the plan removes hidden barrel-length sway scaling);
   - the ADS part belongs in `handling`;
   - whatever stood for "slow to draw, slow out of sprint, tiring to aim" is now paid by weight and should be **dropped**.
2. **Long handguards (M4, KF416, G3 sets).** Same pattern at about −3 ergo and +0.07 dw per 100 mm.
3. **Suppressors.** Weight is understated (×0.6), so the mobility double-charge is milder: 0.3 dw ≈ −4.6 mobility. The −5 ergo is mostly length and blast. Keep it as handling and stability, and consider trimming 1–2 points.
4. **High-capacity magazines.** The ergo tracks capacity. The plan sends mag ergo to `reload_speed`, which fits (bigger mag, slower reload). But drums and quads now also pay mobility on 1.0–1.9 dw. Today's penalties are steep: about −0.3…−0.5 ergo per round over the standard mag on rifles, −0.6…−1.6 per round on 20-round .308 platforms. Removing the mobility-like share is appropriate. This is the largest absolute double charge: `5.56x45_centrefire_mag5100_100r_mag` −25 ergo @ 1.29 dw; `5.45x39_rpk16_mag` −18 @ 1.16.
5. **NV scopes and LPVOs** (−6…−8 at 0.27–0.45 dw). Since optic weight is compressed to 0.6×, the mobility hit is small. Their ergo mostly stands for bulk and belongs in `handling`.
6. **Weapon base rows, battle rifles in particular** (section 7). Across 23 long guns, stock-build ergo against stock-build weight has a slope of **−15.5 ergo per dw (r −0.70)**, almost exactly the new mobility rate. SCARH (28.5 ergo @ 3.51 dw), SA58 (35 @ 3.95), G3 and AK308 (48 @ 3.9) will lose another 8–12 mobility against 5.56 rifles.

Places where ergo was *already moved out* in favour of weight (precedents for the rework):

- MLOK rail sections went from −2 to −0.5 while their weight became proportional to length (0.25.3).
- Mount and riser ergo went to 0 (0.25.4).
- Side-rail penalties were removed (Aug–Sep 2026).
- Mean muzzle ergo went from −3.1 to −1.45 while muzzle weight rose (0.22.12 → 0.25.4).

Places where ergo stands for **bulk or awkwardness rather than weight** (keep as `handling` or `stability`, not weight):

- Muzzle brakes (−1, blast) and thread adapters (−1).
- Magnified-optic class (−3 flat).
- Bipods (−3…−4).
- Featureless grip (0).
- Stockless configurations (+0.5 deviation, big recoil).
- "Made of knives" parts: the plan wants these on worse stability.

---

## 4. Magazines and magazine parts

### Magazine bodies (`magazine`, 141 rows)

- **The default or issue mag is 0 ergo and 0 price;** 30 rounds on rifles, 20 on .308. Examples: `5.56x45_hart_ar15_stanag_30r`, `kazarov_ak74_5.45x39_6l20_30r_mag`, `rsa_sg58_far_metric_magazine_20r`, `tt33_std_8rnd` (moved to 0 in 0.25.4 when its ergo was folded into the base row).
- Capacity drives ergo. Per extra round over standard: 5.56 −0.40, 5.45 −0.32, 7.62x39 −0.26…−0.47, .308 −0.55…−0.85. Shorter mags gain:

| Platform | Short and standard mags | High-capacity mags |
|---|---|---|
| 5.56 | 10r +11, 20r +5…+6 | 40r −6, 60r −10…−17, 100r −25 |
| .308 Saiga | 3r +19, 5r +13, 10r +6.5 | 25r −3 |
| AK 7.62x39 | 10r +9, 20r +4.5 | 40r −6, 75r drum −11, 100r drum −15 |

- **Drums vs sticks and quads:** at similar capacity, drums are *less* penalized than long sticks and quads but heavier. Examples: `5.56x45_x15m_drum_50r` −5 @ 1.05 dw vs `5.56x45_centrefire_mag560_60r_mag` (quad) −17 @ 0.87 and `5.56x45_magtap_pmag_60r` −10 @ 1.12. Ergo therefore tracks **length below the gun** more than rounds. In the rework, this is a reload and handling cost.
- **Material: weight buys ergo.** Steel and aluminium mags are heavier and get about +1 ergo per 0.05 dw over polymer (0318104).
  - Examples: `7.62x39_kazarov_akm_6l10_30r_mag` +1 @ 0.63 vs `7.62x39_magtap_pmag_akm_30r` 0 @ 0.55; `rsa_sg58_far_metric_magazine_10r` (steel) +7 @ 0.32 vs polymer 10r +5 @ 0.28; `aft_mk_17_7.62x51_20r` +1 @ 0.65 vs CDI polymer 20r −1 @ 0.57.
  - This is the opposite of a weight penalty. After the rework the steel mag pays mobility for its extra 0.05–0.15 dw, so its +1 might go.
- Aftermarket 30-round mags sit at 0…+2 (`5.56x45_magtap_pmag_m3_30r` +1, `5.56x45_adapt2_mod3_30r` +2 at 2000). The translucent `dragoon_systems_l5awm_gen2_30r` is −1.5 at 0.28 dw: lighter yet worse, presumably bulk.
- **Price scales with capacity, not with strength.** Spearman(price, ergo) is −0.87 within mag sets: 10r 300–500, 30r 500–2000, 60r 4000, 100r 5500–6000.
- History: 0.24.0 cut Saiga/M14 .308 mag ergo by 25–40 points while raising weights (`sgm_tactical_saiga308_3r_mag` 60 → 19, `10r` 45 → 7). 0.25.4 cut pistol extended mags (`tt33_extended_16r_mag` 10 → −7, `sig_sauer_p320_9x19_30r_mag` −6 → −8).

### Magazine-related parts (`mag_control`, 91 rows)

| Part | ergo | weight | Notes |
|---|---|---|---|
| Mag release / paddle | **+1** (0.5 for a standard paddle) | 0.01–0.05 | Price 200–650 |
| Mag assist / Ranger plate | **+1** | 0.03 (reduced from 0.04, 47792b1) | Bottom plates otherwise 0…+1 |
| Magwell / funnel | **+2** (range 1…3) | 0.03–0.13 | `tactispec_rhino_r23_tactical_magwell` +3 |
| Mag sleeve (P320) | +1 / +1.5 | – | – |
| Capacity extensions | about −0.4 ergo per added round | – | `equinox_plus_5_pmag_mag_extension` −2 (+5); `allpistolsprings_tt33_+1r` −1 (+1); `kalis_kosch_9x19_23r_magex2` −10 (+23) |

- The flat +1/+2 "QoL" parts are reload-themed and **map cleanly to `reload_speed`**.
- Under the plan a capacity extension's penalty becomes reload plus weight.

---

## 5. Ammunition rows (`ammo`, 134 rows)

- **The default round is 0 everywhere** (86–93% of defaults) and costs 0. Exception: the 12g default `12g_mili_275_00buck_9x` has −3 ergo.
- Ammo ergo ranges from −4 to +3 (ignoring the bean bag at +10). Weight runs −0.16…+0.13; recoil about ±5 per axis, plus two 9x18 outliers; velocity −1200…+600; deviation −0.25…+0.4.

Archetype patterns (consistent across 12 calibers):

| Archetype | ergo | recoil | other |
|---|---|---|---|
| Tracers | **+1…+3** | −1…−3 | +0.1…+0.15 deviation, cheap (500–1500) |
| Subsonics | **+1…+3** | −3…−4 | −0.5/−0.6 loudness, velocity −250…−1200, often +0.1 dw |
| Frangible / light fast (RHT, RIP, 7N21, APC) | 0…+1 for frangible, −1…−3 for AP | lower | big +velocity |
| Hot, +P, JHP, match, heavy AP (HST, Gold Dot, M118LR, 7N37) | **−1…−3** | **+2…+5** (up to +7 v) | – |
| Shotgun specials | bean bag +10 (−15/−10, −400 vel); birdshot +5; slug +4 (+3/+3, +600 vel) | – | – |

- **Ammo ergo correlates with ammo recoil** (r −0.33): roughly ergo ≈ 0.1 − 0.08·avg recoil − 0.19·(velocity/100). It encodes **felt recoil, blast and "harshness"**, not mass. The `762x25-ammo-super.xlsx` round notes describe the archetypes this way, for example "Soft shooter: least recoil, best handling" and "Hot surplus: … harsh, loud, flashy".
- The 9x18 "heavy hitters" carry intentional huge recoil: `9x18_bison_caliber_115gr_hcfn` +32/+65 and `9x18_tsniitekhmash_sp7_gzh_80gr` +40/+55 (commits de5d142, 9f538d0).
- Ammo price rises with AP and penetration (top AP 4000–5000), not with ergo.
- **The ammo super sheets treat ergo as a full 1-point stat in `balance_score`.** Ammo ergo therefore buys real strength today. If ammo ergo is dropped, those sheets need re-scoring.
- **For the lead's decision:**
  - **Option A:** fold ammo ergo into recoil and drop it.
  - **Option B:** map it to `stability`, since "soft shooting" reads as steadier.
  - **Option C:** map it to `handling`. This fits the data worst: subsonic or tracer rounds making ADS faster is unphysical.
  - In every option, keep ammo off `reload_speed`.
  - Data oddities: 10mm/.40 rows with `bullet_velocity` 0.02 (`10mm_roosevelt_umc_180gr_fmj`, `40sv_federal_american_eagle_180gr_fmj`, `40sv_federal_premium_180gr_hst`, `10mm_polar_cartridge_220gr_hcfp`) look like a misplaced value.

---

## 6. Price and the "CAG" tilt

- Price has weight 0 in strength by design.
- **Raw price-to-strength correlation within sets is zero overall.** Across 131 sets the median Spearman is 0.00, positive in 50% of sets. Where price does track something, it tracks *capability or size*, not efficiency:
  - **Magazines:** price ∝ capacity; Spearman(price, ergo) −0.87.
  - **Optics:** price ∝ magnification; Spearman(price, strength) −0.63, because magnified optics cost 1500–5000 and carry −3 or worse.
  - **Muzzles:** suppressors cost 1500–3500 against 300–750 for brakes and flash hiders.
  - **Barrels:** long and heavy profiles cost more.
- **With weight held fixed, the tilt is slight and positive.** The median Spearman between price and weight-adjusted strength is:
  - barrels +0.30 (slope about 0)
  - muzzles +0.35 (+0.9 strength per 1000 credits)
  - receivers +0.20
  - handguards +0.11
  - tactical +0.75 (+0.9 per 1000)
  - internals +0.71 (+2 per 1000)
  - stocks −0.03, pistol grips +0.03
  - **Size of the tilt:** about **0–2 strength points per 1000 credits**, i.e. at most 1–2 ergo across a slot's whole price range. This matches `knowledge/stats.md` ("can trend slightly better").
- **Issue (default) parts are not weak.** Default handguards out-score 89% of alternatives (`hart_m4_std_carbine_plastic_handguard` 14, −10/−10, free; AK wooden 15); default stocks out-score 75%. Default receivers and internals, by contrast, are the 0 floor, and 75–100% of alternatives beat them. **Progression lives in small parts, not in furniture.**

Where "cooler is better" is visible:

- **Modern ergonomic designs get +2…+4 ergo over retro equivalents at similar weight.** Examples: A1 chopped grip 3 → A2 6 → MOA/Gunslinger/AVP 7–9; mags 0 → PMAG/ADAPT2 +1/+2; aftermarket lowers and charging handles +2…+5.
- **Aesthetic items are statted to be worth taking:**
  - b89c793 NATO AUG barrels: their "initial motivation … was aesthetic appeal so their stats reflect that".
  - `cugir_pm_md63_wooden_sharkfin_bottom_handguard` is the best AK lower at 17.
  - Wooden AK furniture is top-tier (15).
- **Premium barrels are priced as premium** (bfed37d "increased price, since these are premium barrels").
- **Cosmetic premiums don't buy stats:** CGR printed rail panels cost 1000 and are identical to 50-credit XTM panels.
- **Counter-examples (realism wins over cool):**
  - The translucent L5AWM is −1.5.
  - Heavy railed AK systems are bad (`tdiarms_ak_x47_rail_system` 6).
  - The KALIS Gen III 10" handguard was nerfed on 2026-11-18.
  - ea21a23: "AK ACR: surely it can't be that ergonomic".
- **Takeaway:** CAG operates as "a modern or aesthetic option should not be a trap, and may edge out its retro counterpart by 1–3 ergo". It does not mean "more expensive equals stronger". Preserve that ordering when splitting ergo, e.g. modern grips should not lose their edge in `handling`.

---

## 7. Weapon base rows

Base values per class (weight is 0 except where noted):

| Class | Weapon | Base ergo | Stock-build ergo | Stock-build dw | Base h / v |
|---|---|---|---|---|---|
| pistol | Makarov | 75 | 76 | 0.72 | 25 / 25 |
| pistol | TT33 | 77 | 77 | 0.92 | 40 / 40 |
| pistol | EDC_X9 | 85 | 90 | 0.78 | 25 / 45 |
| pistol | KOSCH | 70 | 75 | 0.81 | 25 / 35 |
| pistol | P320 | 70 | 77 | 0.94 | 25 / 35 |
| pistol | P226 | 63 | 71 | 0.99 | 20 / 25 |
| pistol | Glock20 | 60 (w 0.4) | – | – | 40 / 70 |
| rifle 5.56/5.45 | M4A1 | 15 | 61 | 2.76 | 65 / 85 |
| rifle 5.56/5.45 | KF416 | 25 | 68 | 3.15 | 65 / 80 |
| rifle 5.56/5.45 | AK_545 | 15 | 56 | 2.94 | 65 / 70 |
| rifle 5.56/5.45 | AK_545_Carbine | 20 | 76 | 2.48 | 65 / 70 |
| rifle 5.56/5.45 | AK12 | 35 | 64 | 3.17 | 50 / 55 |
| rifle 5.56/5.45 | SCARL | 35 | 61.5 | 2.79 | 60 / 65 |
| rifle 5.56/5.45 | AUG_A3 | 40 | 65.5 | 2.71 | 55 / 65 |
| rifle 5.56/5.45 | QBZ95 | 49 | 61 | 2.64 | 55 / 55 |
| rifle 7.62x39 | AK_762 | 17 | 55 | 3.25 | 70 / 85 |
| rifle 7.62x39 | SCAR47 | 40 | 62.5 | 3.39 | 60 / 70 |
| rifle .308 | SCARH | **5** | **28.5** | 3.51 | 75 / 80 |
| rifle .308 | SA58 | 15 | 35 | 3.95 | 85 / 105 |
| rifle .308 | AK308 | 20 | 48 | 3.90 | 80 / 100 |
| rifle .308 | G3 | 25 | 48 | 3.91 | 70 / 100 |
| bolt | Mosin | 65 | 73 | 3.36 | 80 / 90 |
| bolt | Remington700 | 30 | 64 | 2.79 | 80 / 90 (damage 1.2, dev 0.2) |
| shotgun | R870 | 25 | 63.5 | 2.65 | 90 / 90 |
| shotgun | MP133 | 25 | 60.5 | 2.66 | 60 / 70 |
| smg | MP5 | 40 | 59 | 2.28 | 45 / 55 |
| smg | MK9 | 30 | 68 | 2.38 | 55 / 70 |
| smg | AK_9 | 30 | 75 | 2.16 | 50 / 50 |
| smg | SCALAR | 40 | 66.5 | 2.40 | 60 / 60 |
| smg | UMP | 60 | 77.5 | 2.32 | 80 / 90 |
| launcher | RPG7 | 40 | 51 | 5.80 | 80 / 90 |
| launcher | PSRL | 30 | 41 | 5.38 | 75 / 95 |
| turret | Turret | 30 (w 3.0, cap 200) | – | – | – |

What the base ergo encodes:

1. **An offset that lands the stock build in a band.** The bands are pistols 71–90, SMGs 59–78, 5.56 rifles and shotguns 56–76, .308 battle rifles 28–48 and launchers 41–51. Modular guns get low bases because their parts add +30…+50 (M4 15 → 61). Guns with few statted parts get high bases (Mosin 65 → 73, QBZ95 49 → 61, UMP 60 → 77.5).
2. **A sink for "swap-exclusive" ergo.** ca16199 moved TT-33 base ergo from 45 to 77 and zeroed the standard mag, grip, bottom plate and slide; the "alternatives become offsets" and the "stock build total [is] unchanged". The same was done for Kosch .45 mags. **Rule: default parts carry 0, and the base row carries the platform.**
3. **Calibre and mass class.** .308 guns sit 15–30 points below 5.56 guns of the same layout (SCARH 5 vs SCARL 35; AK308 20 vs AK12 35). Together with the −15.5 ergo/dw slope across guns (section 3), the low base ergo of battle rifles partly *is* their weight penalty. Expect to raise .308 bases (or their `handling` and `reload_speed`) once mobility charges their 3.5–3.95 dw.
4. **Per-weapon feel.** Recent base edits are framed per gun: "scalar: base ergonomics 45 → 40", "p226 base ergo 65 → 60", "r700 base ergo nerf", "scarh ergo nerf", and in 0.25.4 TT33 45 → 77, EDC 80 → 85, SCALAR 25 → 40.
5. Base rows also hold the platform recoil, deviation, velocity and damage multiplier (R700 damage 1.2, TT33 0.98).

For the three new stats, the contract asks weapon rows to carry all three bases. The anchor is "a typical built rifle ~55–60" with stability 50 meaning today's feel. The current base ergo is not a handling value on its own, because +30…+50 of a rifle's total comes from parts. Set the bases from target *build* totals, not by copying.

---

## 8. Design reasons found in history

These are paraphrases, or quotes under 15 words, from commit messages and change sheets (commit ids in the balancing repo).

**Weight and ergo exchange**

- 0318104: steel mags were given "0.04 weight for 1 ergo vs. poly"; this was raised to 0.05 dw per ergo.
- 6507df1 and be2462d: rail panels get 1 ergo per 0.04 dw (earlier 0.03).
- f0db2dc: risers and some scope mounts made free (0 ergo). The Vudu's own ergo went −5 → −6 to compensate for free mounts.
- 7a3a261: Corvus mounts are "not supposed to take ergo".
- c864e5c, 166a088, 199fdb1: side-rail ergo penalties removed.
- 25cc96a: "+2 ergo for the naughty dog suppressors since they can't mount grips". **Compensation across slots is done in ergo.**
- 2706fae: sleeve suppressors keep a slightly lower strength because they are shorter.
- 4df74b2: bullet weights made "less exaggerated (80gr/30 bullets to 0.01 weight)".
- 3049a9e: the X300 light is "lighter than in real-life".
- dab7c5f: FAL stocks are "lighter than irl anyway".
- 2124f1e: the P226 weights are "close to real-life".
- 2025-07 "weight rework" commits (heavier 9mm/.45 barrels, AK mag weight rework, heavier AUG and Vector stocks): weight raised toward realism, and other parts lightened to keep totals ("compensate for barrel weight increase by reducing weight of some parts", 112540b).

**Assembly structure**

- 6203675, ef7037c, 60ad191, fe20f7b, 962b0c0: stock-assembly ergo and recoil moved to the gun-contact part; sub-parts keep weight and price; assembly totals unchanged.
- ca16199 (TT-33) and b5c4624 (KALIS Scalar): fold default-part ergo into the base or the lower and zero small parts ("Zero ergo on Gen III trigger, mag release…").
- cf82838: UMP "reorganize ergo".

**Nerfs and buffs with stated reasons**

- bfed37d: AKM carbine barrels hit hard so they are not "7v7 monsters". Their price was raised as "premium barrels".
- b89c793: NATO AUG barrels were statted for aesthetic appeal, with +0.05 deviation for a missing adapter.
- 2390dda: P226 recoil was lowered while the P229 barrels got +3 v each, to separate the two guns.
- 9b12091: "ak stocks: a series of compromises". Some wooden stock recoil was moved from horizontal to vertical.
- ea21a23: the AK ACR stock was nerfed ("surely it can't be that ergonomic").
- b0c3901: SCARH ergo was nerfed to "make lowers less far apart".
- a0c2292 "attempt to make grippods make your recoil worse"; f210f61 "buff bipods stamina bonus". The bipod payoff lives in `bipods.csv`, not in ergo.
- `handguard-recoil.csv`: "+4 +4 recoil to every handguard to account for the muzzle device buff".
- 9x18 heavy hitters: "make upsides more pronounced", then "make less nucular" (9f538d0, de5d142).
- 039a337: the 7.62x25 rounds were rebalanced so that all score "as sidegrades within 1.8 strength", down from a 12.6 spread. **The explicit target is near-equal strength inside a slot.**

---

## 9. Invariants a re-statter must not break

1. **Stacking:**
   - Only the first grip counts. Handstops, index panels and the XTM handstop are grips; they compete with foregrips at a flat 6 ergo.
   - Only the last muzzle device counts. Adapters under a can keep only their weight.
   - Only the first 4 rail panels and the first 2 iron sights count.
   - The new columns inherit all of these, so panel and iron ergo must stay small per item: 0.25–2.25 and +1.
2. **Default and reference parts are 0, with price 0.** This holds for barrels (the default length), magazines (the standard capacity), ammo (the issue load), receivers, internals and mag parts (83–93% of defaults). Alternatives are deltas from them. **Keep the zero reference in all three new stats**; otherwise stock builds drift. Exceptions to preserve deliberately: stocks, handguards and grips carry their absolute value (+15 / +12 / +5), and the 12g default ammo is −3.
3. **Only-choice parts.** Of the only-choice slots in `competing_sets.json`, about half the items carry non-zero stats. They are mostly +1 internals (`kalis_scalar_std_charging_handle`, `lockwood_impact_700_trigger`) and required handguard or stock halves (`hart_xm177_handguard_bottom_part` 17, `hk_psg1_msg90_handguard` 8). These are part of a weapon's fixed budget. Moving them to the base row is a no-op for players, and that is the direction recent commits took. Note that "only choice" in one slot can still compete in another slot.
4. **Assembly totals.** When splitting an assembly's ergo into three stats, keep the stats on the gun-contact node and leave sub-parts weight-only (section 8).
5. **Strength parity inside a slot.** The team's tool is the strength formula with weight at −20 per dw. After the rework, update that weight term, or heavy items will look fine in the sheet while playing worse. A first guess is to keep −20 for travel speed plus a mobility share. Both the size of that share and what one point of `handling`, `reload_speed` or `stability` is worth in strength units need a team decision.
6. **Comparison scope** (`knowledge/balancing.md`): only interchangeable options must compare well. FAL handguards outclassing G3 handguards is fine. Watch whole-class shifts, e.g. every .308 gun losing mobility at once.
7. **Recoil direction:** stocks, handguards and barrels favour vertical reduction (H/V 0.80–0.86 overall); brakes favour horizontal. Moving recoil around is out of scope, but don't let ergo-to-stability conversions silently change the h/v ratio.
8. **Things that look like bugs but are deliberate:**
   - +0.5 deviation on stockless parts;
   - +0.03 deviation on drop-in handguards;
   - the 9x18 recoil outliers;
   - −45 ergo on `custom_hart_smg_9x19_50r_extension` (extreme but consistent with a 50-round SMG stick);
   - +14 ergo with +6/+6 recoil on `r870_earthquake_raptor_pistol_grip` (a stockless pistol-grip shotgun).
9. **Probable genuine anomalies to review, not to propagate:**
   - `9x19_glock_stick_31r_vector` +16 ergo (the other 31-round stick is −3);
   - the 0.02 velocity cells on 10mm/.40 ammo;
   - `hart_xm177e1/e2_slim_plastic_handguard` at 0 weight and 0 stats (their stats live on `hart_xm177_handguard_bottom_part`, so the container is correct, but a 0 weight is odd);
   - `Glock20` base weight 0.4 (every other base is 0).

---

## 10. Suggested mapping of today's ergo by family

This is a proposal derived from the patterns above, not mined fact.

| Family | Today's ergo mostly means | Natural new home |
|---|---|---|
| Stock (+15) | Shouldering, cheek weld | Split `stability` and `handling` (stockless → low stability) |
| Handguard (length) | Grip and length | `stability` (length) + `handling` |
| Rail panels, handstops, foregrips | Grip comfort | `handling` (panels) / `stability` (grips) |
| Pistol grip | Comfort, control | `handling` |
| Barrel (−4 per 100 mm) | Length and swing | `stability` + `handling`; drop the mobility-like share |
| Suppressor, brake | Length, blast | `stability` (can length), `handling` (brake blast) |
| Optic class | Bulk, eye box | `handling` |
| Magazine (capacity) | Length below the gun | `reload_speed`; drop part of the drum/quad penalty |
| Mag release, magwell, mag assist (+1/+2) | Reload QoL | `reload_speed` |
| Charging handle, trigger, selector (+0.5…+5) | Manipulation QoL | `handling` (selector, trigger) / `reload_speed` (charging handle, bolt catch) |
| Iron sights (+1) | Sight picture | `handling` |
| Ammo (±3) | Felt recoil and blast | `stability`, or fold into recoil (section 5) |
| Bipod, bayonet blade (−3…−4) | Front bulk | `stability` |
| Weapon base | Platform plus calibre and mass class | All three; raise .308 bases once mobility charges them |

---

## 11. Family heuristic errors found (`items_index.csv`)

| Mislabelled items | Labelled as | Actually |
|---|---|---|
| `egs_orthocone_suppressor`, `mosin_bramit_7.62x54r_suppressor`, `resiliant_suppressors_obsidian_9_body`, `spiderweb_bpr_suppressor_system_srm_6`, `rhodesian_halbek_muzzle_device`, `odin_works_tiduro_modular_compensator` (attach type `barrel`) | `barrel` | Muzzle devices |
| `ips_5.56x45_*_barrel_extension`, `ips_1_2x28_to_5_8x24_knurled_thread_adapter`, `gt_24_1/2`, `i_24_14_ta` | `barrel` | Muzzle-slot adapters and extensions |
| R870 tube caps and extensions (`r870_*rnd_extension`, `dragoon_systems_lsx_*`, capacity 0) | `magazine` | Same kind of part as the MP133 `mp133_+2r_mag_ex`, which is labelled `mag_control` |
| `hk_mp5k_polymer_handguard` | `foregrip` | Handguard |
| `thordsen_frs_15_stock`, `hera_arms_cqr_gen1_pistol_grip_stock` (in the AR pistol-grip slot), `r870_earthquake_raptor_pistol_grip` (in the R870 stock slot) | various | Grip/stock combinations |
| `hart_m4a1_castlenut`, `hart_m4a1_receiver_endplate`, `thorsden_frs15_gen3_ar15_endplate` | `receiver` | Stock-system parts |
| Mounts, risers, eye cups and lens caps | `optic` | Not optics; filter on category `Mount` / `Sight Mount` / `Riser Mount` when analysing optic ergo |
| AUG and Mosin "stocks" | `stock` | Chassis or full furniture (16–40 and −10…+5 ergo); not comparable to AR/AK stocks |
| `lowenherz_aug_a1_stg77_1_5x_scoped_receiver` | `optic` (by aim FOV) | A receiver |
| `misc` (77 rows) | `misc` | A catch-all, including spacers, picatinny adapters and drop-on rails |
