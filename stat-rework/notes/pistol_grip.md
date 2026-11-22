# Pistol grip family: notes

Rules live in `rules/pistol_grip.py` (docstring states them); exceptions in
`overrides/pistol_grip.csv`. E = old ergonomics. Weight credit 0. Recoil, weight and price
unchanged.

## Rules

| Kind | h / r / s per E | Items |
|---|---|---|
| standard | 1.0 / 0.4 / 0.5 (family default) | A1, A2, MOE, Battlegrip, FANG Rogue/47, stock AK polymer, Vityaz, AK-12, Gral-S, wraps, cores, AICS standard backstrap, G3 plastic, only-choice grips |
| cqb (steep, slim, skeletonized, chopped, compact) | 1.25 / 0.4 / 0.15 | A1 chopped, TD skeletonized, Enforcer, KALIS Gen3, Gunfighter Mod 3 (AR + SCAR), MOE-K2 (AR, SCAR, AK), MCS AVP, MG-47, Khorovod, Razor G02, P320 XCARRY, EDC small backstrap |
| support (palm swell, beavertail, palm shelf, trigger guard, rubber, heavy) | 0.75 / 0.4 / 0.85 | FIT Suregrip, Battlegrip Beavertail, Axtell w/ trigger guard, Equinox Orion, Hera CQR, AK bakelite, US Pine, RK-3, PM-G, AG-FAR, PSG1 grip and palm rest, AICS thumbhole, EDC large backstrap |
| magwell | 0.3 / 1.5 / 0.3 | P226 two-piece magwell |
| stockless shotgun grip | 1.45 / 0.35 / -0.3 | R870 Raptor, MP-133 plastic pistol grip |

- Reload is 0.4 E in all grip kinds, so the trade inside a set is handling vs stability and the
  old E ordering (with the CAG/era tilt: A1 chopped 3 < A1 5 < A2 6 < modern 7-10) carries over.
  Modern CQB grips keep their handling edge (Gunfighter h 10, MCS h 11.5 vs A2 h 6).
- Typical magnitudes: AR set h 4..11.5, r 1..4, s 0.5..8.5. Support grips reach s ~ E (Axtell
  s 8.5) because EV conservation prices stability at 0.47; I kept the tilt mild so pistol grips
  stay "mostly handling" (support h is still 0.75 E).
- Stockless shotgun grips (E 14, compete with stocks in `r870_stock` / `mp133_stock`): h 20.5,
  r 5, s -4, EV 12.4. They keep the deliberate +14 (RULES_MINED §9.8) as the handling option; the
  stocks next to them will carry large positive stability, so a stockless shotgun is far less
  steady. Magnitude 20 is stock-sized on purpose. Stock-family values not checked against mine.

## Overrides (4)

- `hera_arms_cqr_gen2_pistol_grip` h 1, r 1, s 4.5: heaviest AR grip (0.14), big hand-filling
  shape; at E 3 the support rule left it dominated by the FANG Rogue.
- `rsa_sg58_wooden_grip` h -1, s 2 (E 0): heavy wood steadies, slower; also stops the SAW-style grip
  being best on all three.
- `sig_sauer_p320_xfull_grip_module` h -1, s 1.5 (E 0): full-size frame vs the XCARRY compact.
- `rogue_p226_smooth_hardwood_grip` h -0.5, s 1 (E 0): smooth, heavier wood; stops the magwell
  grip being best on all three.

## Checks

`check_family.py pistol_grip foregrip`: 0 EV drift, no pistol-grip dominations, no item best on all
three new stats in any set of 3+.

## Open points and misfiled items

- `behemoth_tacticals_featureless_grip` kept at 0 (old sheet: 0 ergo, strong recoil). A featureless
  fin is arguably slower to point; left as the recoil pick rather than invent a penalty.
- `ss_apex_ak_ar15_adapter` (E -1, hosts an AR grip) and `truelock_custom_pm_tactic_kit_pistol_grip`
  (hosts a rail) are assemblies; standard split on their own value.
- `agr_870_pistol_grip` (E 1) is the AGR stock/grip base; its child
  `agr_870_protection_cap` (filed as `optic`, E 14, +8/+8) is what makes it a stockless grip. That
  cap should get the stockless split (h 1.45E, r 0.35E, s -0.3E) by whoever owns it; not my file.
- Grip/stock combinations in the AR and AK grip slots (`thordsen_frs_15_stock`,
  `hera_arms_cqr_gen1_pistol_grip_stock`, `hera_arms_cqr_gen1_ak_stock`) belong to the stock family;
  they top every archetype in those slots, so check them against these grips.
- `talon_aug_foregrip_wrap` is filed here (it wraps the AUG foregrip); standard split is fine.
- Kinds for grips whose real shape I could not confirm (MCS AVP, Equinox Orion, MG-47, Khorovod,
  Gral-S) were chosen from weight and old stats.

## Round 5: reload scope

Pistol grips do not affect reload: reload 0. The 0.4·E reload share of every grip that had one is moved into handling and stability in its own proportions (EV kept; `reload_scope.py`).

## Round 7: profiles and roles

Handling and stability now come from each part's row in `profiles/pistol_grip.csv` (RULES.md section 15); the split rules, weight leans and overrides above are history for these two stats.

Pistol grips are `even`: most differ in comfort, not form. Roles: the chopped and skeletonized grips are compact; the PSG1 grip, the AICS thumbhole backstrap and the fully vertical chassis grip (strong) are marksman. The Raptor and MP-133 plastic grips are fitted in place of a stock, so they are stockless options (lead).

Profiles: even 64, stockless 2. Unidentified counterparts: 1.

Role parts:

- `hart_a1_chopped_pistol_grip`: compact, Colt A1 pistol grip, shortened (chopped)
- `hk_psg1_wooden_grip`: marksman, HK PSG1 precision pistol grip
- `mcs_premier_avp_grip`: marksman (strong), MDT Vertical Grip Premier (AR compatible)
- `precision_intercontinental_at_aics_gen2_thumbhole_backstrap`: marksman, Accuracy International AICS 2.0 thumbhole backstrap
- `tactical_dynamics_anodized_skeletonized_ar15_pistol_grip`: compact, Tactical Dynamics skeletonized aluminium AR-15 grip
