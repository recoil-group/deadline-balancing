# Foregrip family: notes

Rules live in `rules/foregrip.py` (docstring states them); exceptions in `overrides/foregrip.csv`.
E = old ergonomics. Weight credit 0. Recoil, weight and price unchanged. Reload is 0 for every
foregrip: nothing on the front of the gun plausibly changes the reload.

## Stacking facts that shaped the rules

- **Handstops are grips.** Every handstop, finger stop, index panel and the Vallais indexer has
  attach type `grip`, so it competes for the single counted grip slot (RULES_MINED §9 agrees).
  The lead's "handstops are not grips and stack" holds only for `hk_ump_handstop` (no attach type,
  only-choice add-on on the UMP). That one is kept small (h 6, s 2.5, EV 4.8 vs 6); the rail
  handstops get the full handstop split.
- **Pump forends are grips.** `r870_*_handguard` and `mp133_*_handguard` have attach type `grip` and
  are mounted before anything on their rails, so on the R870 a rail foregrip on the MOE or PR870
  forend only ever adds weight. The forend therefore carries the "foregrip" value of the shotgun.
- **Smite bipod-grip bug (for the lead, not patched).** `smite_industries_ar_picatinny_bipod_foregrip`
  is a `grip` and is mounted before its legs (also `grip`), so the legs' stats and their recoil
  (-3/-4, -5/-6) never apply in game; the Smite is effectively 0 / 0 recoil today. The grip-pod body
  has no attach type, so its legs are the counted grip, as intended. I mirrored the old sheet
  (bodies 0, legs carry the values) so the data is right once the Smite body loses `grip` in
  Studio. If the lead prefers a sheet-side fix, move the legs' values onto the body instead.

## Rules and magnitudes

| Kind | Rule | Example (E) -> h / s |
|---|---|---|
| Handstop, finger stop, index panel, indexer, RK-6 | h 1.25E, s 0.5E | 6 -> 7.5 / 3 |
| Angled (AFG, AFG-2, KAG, Cobra, SI Link, Alpha Four, RK-4) | h 1.0E, s 0.85E | 4 -> 4 / 3.5 |
| Stubby / half (Gunfighter short, Romanian half, Equinox, PSRL, RK-0, RK-5) | h 0.8E, s 1.1E | 6 -> 5 / 6.5 |
| Full vertical (everything else with `grip`) | h 0.75E - 1.5, s 1.2E + 2 | 5 -> 2.5 / 8; 2 -> 0 / 4.5; -1 -> -2.5 / 1 |
| RK grip on the angled B-25 mount | its kind, then +1 h, -1 s | |
| Grip-pod / Smite legs | collapsed h -5.5, s 7; extended h -7.5, s 7 | |
| Folded bipods that stack (Harris HBR base, AUG HBAR) | h 1.5E, s -0.5E | -4 -> -6 / 2 |
| AUG A3 grip | unfolded = vertical; folded h 1.5E, s 0.2E | 2 -> 0 / 4.5; 7 -> 10.5 / 1.5 |
| Pump forend | default 0.8/1.1; slim (MOE 870, MP133 plastic) 1.1/0.75; heavy (PR870, MP133 beech) 0.5/1.5 | |

- The +2 stability / -1.5 handling support term on full verticals is EV-neutral. It keeps the
  low-E recoil grips (VPG, SE-5, RK-1, RK-2) from getting zero or negative stability: they pay in
  handling, which is the physics (long grips are slow, never unsteady).
- Resulting trade in the big rail sets: handstops are the handling pick (h 7.5, weak recoil),
  full verticals the stability pick (s 7-9, good recoil), stubby/angled grips sit between, and the
  low-E recoil grips (VPG, SE-5, Romanian full) are the recoil pick. The optimiser's archetype
  builds confirm it: handling picks handstops, stability the CQR / UVG / Gunfighter, recoil the
  SE-5 / VPG / Romanian full, all-round the Gunfighter short.
- Grip-pod legs: "high stability" is s 7, top tier but below the heaviest verticals (CQR s 9),
  because EV from E -1/-3 does not support more without a handling cost beyond -8. EV -0.0 / -1.2.
  Magnitudes exceed 1.5x|E| on purpose (deliberate trade-off); the deployed payoff stays in
  `bipods.csv`.
- EV: every item within max(2, 25%) of E; full verticals land ~+0.3 above E, handstops ~-0.1.
- Old EV ordering inside sets is kept (E 6 handstops/stubby ~6, E 5 verticals ~5.3, ...).

## Overrides (2)

- `okb_crazy_romanian_picatinny_full_grip`, `okb_crazy_romanian_mlok_full_grip`: h -2, s 5. The
  longest vertical in the set; the rule (E 1) gave s 3 and left it dominated by the SE-5.

## Remaining domination (1 item)

- `launchtron_psrl_plastic_foregrip` (E 3, -2/-2, 0.10 dw, 800 credits) is dominated by the
  Gunfighter vertical, UVG, AFG-2 and Romanian half. It was dominated in the old sheet too (3 ergo
  with the worst recoil of its weight class). It is the PSRL launcher's own grip and only worth
  taking for looks; fixing it would mean inflating it or touching recoil. Left for the lead.

## Misfiled / decided myself

- `hk_mp5k_polymer_handguard` (only choice on the MC51K): a handguard; handguard default split
  0.9/0.1/0.8 -> h 13.5, r 1.5, s 12 (EV 14.3 vs 15). Its value belongs to the G3/MC51K base anyway.
- `r870_*_handguard`, `mp133_*_handguard`: pump forends (handguards), kept here because they are
  the counted grip (see above).
- `r870_shorty_std_bolt` (Serbu shorty pump, only choice, E 0): internals; 0.
- `harrison_pra_adapter`, `grip_pod_gps_02_body`, Smite body: 0 (adapters / bodies).
- Uncertain real-world identities, typed by shape and old stats: Equinox EX M-LOK grip (stubby),
  Veles RK-0/RK-5 (stubby), RK-4 (angled), RK-6 (handstop-like), Timber Creek Enforcer foregrip,
  PTS Validus Shift, TargetDown BGV (full verticals).

## Round 5: reload scope

No foregrip affects reload. The one part with reload (`hk_mp5k_polymer_handguard`) has it moved into handling and stability (EV kept; `reload_scope.py`).

## Round 6: pump forends

The pump forends are the shotguns' cycling interface and carry `fire_rate` (`cycling.py`, RULES.md
section 14), priced at 1.5 EV per 1% and taken out of (or given back to) their handling and
stability, EV kept:

- R870: SpeedFeed (default) 0; Magtap MOE +3% (h 11 / s 3 → h 5 / s 1.5); P.R.O Tactical PR870
  −2% (h 1 / s 11 → h 4.5 / s 13.5: the steady, slower forend).
- MP-133: beechwood (default) 0; plastic +2% (h 6.5 / s 4.5 → h 3.5 / s 2.5).

## Round 7: profiles and roles

Handling and stability now come from each part's row in `profiles/foregrip.csv` (RULES.md section 15); the split rules, weight leans and overrides above are history for these two stats.

Foregrips lean by shape: vertical grips and grip-pods towards stability (h 0.5 V, s 1.49 V), angled grips and handstops towards handling (h 1.15 V, s 0.66 V). A vertical grip with a negative value costs handling only. Both replace the weight-in-set lean and the ×2 lean pass, which had made the grip slot the most extreme family (handling spread 2.0× the old ergonomics spread; now 1.17×).

Profiles: grip_vertical 40, grip_angled 23, even 6, zero 4, grip_pod 4, handling 2. Unidentified counterparts: 0.
