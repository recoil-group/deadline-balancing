# Tactical devices (38 rows: lasers, flashlights, combo units, light heads/bodies)

## Rules (`rules/tactical.py`)

- **Rail and slot devices**: front-end bulk you swing onto target, nothing else. handling = 1.6 × E,
  reload 0, stability 0 (EV 0.96 × E). No weight credit (lead decision, RULES.md section 3).
  Lights were 0 and stay 0. Lasers and combo units −0.5…−2 become −1…−3 handling. Their front
  mass already buys −1…−3 vertical recoil on the sheet, and a laser's payoff (smaller hip
  free-aim) lives in lasers.csv, so neither is added here.
- Stability stays 0 on purpose: a 0.05–0.2 dw box at the muzzle does not plausibly change
  breathing or walking sway, and RULES.md counts front-heavy ends as worse stability only for real
  front mass (barrels, bayonets).
- **Guide-rod lasers** (LaseVex P226/P229) sit inside the gun, so no bulk. They had no value and
  stay empty.
- Old EV ordering and the price tilt are kept, because the mapping is linear.

## Exceptions

- `pm_laser_ltsu_pm_laser` is a Makarov **pistol grip** with a laser built in, and it competes in
  the PM grip slot. It takes the pistol-grip split 1.0/0.4/0.5: h 2, r 1, s 1. It sits beside
  Pro-Tactical (h 2 r 1 s 1, −1/−1) and Khorovod (h 3 r 1 s 1.5), and its edge is the laser.
- Override (1): `holosun_ls321g` handling −1 instead of −1.5. It tied the PEQ-2A at higher weight
  and price. It is the more compact modern unit (CAG), and its EV −0.6 is within tolerance.

## Remaining dominations and best-in-all-three (accepted)

With handling as the only axis, every 0-ergo device ties for best in its rail set on all three
stats, and lighter 0-ergo lights dominate heavier ones. The real trade-off is function, which the
checker does not see:
- light versus laser versus combo (`las_tac_2` against the Cosmotac LAM);
- beam output in flashlights.csv. The heavier WMX200, Klesch-2P and R300U are the brighter or
  wider beams (secondary brightness 5 against 3–4 for LAS/TAC 2 and Foxtrot1);
- EOLAD 2 civilian against 2VI SOCOM, where the 2VI adds the flashlight;
- Nariakira 300 against 18650 body, where the 18650 hosts the brighter PLHV2 head (5 against 4).

Giving lights a weight-based handling cost would only charge weight a second time, so I did not.

## Misfiled

- `pm_laser_ltsu_pm_laser` is a pistol grip (handled above).
- `whitehouse_rush_qe_junction_box_legacy_crane_connector` (in misc) is a RUSH sub-part. It is
  re-statted as tactical: 0.
