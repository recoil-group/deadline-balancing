# mag_control: notes

Rules live in `rules/mag_control.py`; shared helpers (`box_split`, `tube_split`) come from
`rules/magazine.py`. No weight credit.

## Split rules

- **Reload parts** (releases, buttons, paddles, magwells and funnels, mag assists, Ranger/loop and
  bumper bottom plates): `reload = 2.5·E`, handling and stability 0, EV kept exactly. +1 parts →
  r +2.5, +0.5 paddle → +1.5, +2 magwells → +5, Rhino R-23 +3 → +7.5. Recoil cells on magwells are
  left as they were.
- **Capacity extensions** (Equinox +5, FireLine +2/+5, AllPistolSprings +1, Dante Freelance,
  KALIS MagEx2): a longer magazine, relative to the set's default plate. `reload = 2.125·E_rel`,
  `handling = 0.25·E_rel` (same as `magazine`, knee −15, floor −25). Typical: +5 PMAG/AK −0.5/−4.5;
  MagEx2 −2/−16 (17–18R) and −2.5/−18 (23R).
- **P320 grip sleeves**: they fill the gap between the grip and an extended mag, so half handling
  (full grip) and half reload (guides the insert): `h = 0.8·E`, `r = 1.3·E` (short +1/+1.5, long
  +1/+2).
- **MP133 tube extensions**: `magazine.tube_split`, relative to the default cap
  `mp153_4r_mag_cap` (E +12): +2R −1.5/−4.5, +4R −2.5/−7.5. Same rule as the R870 tubes.
- Standard releases, plates, magwells, shell carriers, shell feeders and the PM release spring
  are 0/0/0 (all were 0).
- Stability 0 throughout.

## Overrides

None.

## Dominations

- `mp133_+2r_mag_ex` > `mp133_+4r_mag_ex` and `mp153_4r_mag_cap` > both: tube capacity is not a
  sheet column, so the check cannot see that the longer tube holds more shells. Not real.
- "Best in all three" for the AUG enhanced releases, the Rhino magwell, the Ranger plate and the
  long P320 sleeve: these are pure upgrades over a 0 standard part; their trades are price and a
  few hundredths of a dw, as in the old sheet (CAG).

## Only-choice parts

Only-choice +1 parts (`mcs_rev21_gen2_r700_mag_release`, `ardian_weapons_adac15_mag_release`,
`dragoon_systems_l7awm_bottom_plate`, the optional mag assists and magwells) keep r +2.5 / +5;
their value belongs to the weapon budget either way.

## For the lead

- `mp153_4r_mag_cap` is filed as optic (h +18); it should be 0/0/0 as the zero reference of the
  MP133 tube set (see `notes/magazine.md`).

## Round 5: reload scope

Magazine controls are re-statted by kind (`reload_scope.py`, RULES.md section 13):

- Flared magwells and funnels: −3%. The large Rhino R-23 funnel: −5%.
- Enhanced, ambidextrous, extended or oversized releases: −3%.
- Mag assists, loop plates and the SG58 bumper plate: −3%.
- Large AUG release paddle: −2%.
- Capacity extensions by total capacity against their base magazine, as magazines.
- Standard releases, plates and magwells: 0.
- Sleeves and couplers: 0, with their old share moved into handling.

EV follows: a magwell worth E +1 to +3 is now worth about 3.4 (−3%) or 5.8 (the −5% Rhino). The two KOSCH .40 magex are identical apart from weight (a variant).
