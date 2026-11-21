# magazine: notes

Rules live in `rules/magazine.py` (docstring has the full list). No weight credit (RULES.md section 3).

## Split rules

- **Zero reference.** Values are deltas from the set's default magazine: `E_rel = E − E(default)`.
  The default is 0/0/0 (RULES_MINED 9.2). Sets whose default had non-zero ergo shift by that
  constant, which the weapon-base calibration absorbs: AR-15 (+1, PMAG M3 30R), AUG (+1.5),
  SCAR-H (+1, AFT 20R), AKM (+1, ribbed 1955), Mosin (+3, standard 5R), KOSCH .40 (+2.5, 10R),
  KOSCH .45 (+1.5, 10R). Items with no set (unreachable) use E as is.
- **Above standard capacity:** `reload = 2.125·E_rel`, `handling = 0.25·E_rel`, which keeps EV
  exactly. Past −15 reload only half of the rest counts, and it stops at −25. Typical: 40R stick
  −2/−15; 60R quad −2.5…−4.5 / −17.5…−25; 75R/100R AK drums −3/−21 and −4/−25.
- **Drums, quads, caskets and couplers** never reload faster than the slowest stick they compete
  with. This only binds on `5.56x45_x15m_drum_50r` (−5 old ergo, now reload −15, equal to the
  PMAG 40R): the old sheet let its weight do the work.
- **Below standard capacity:** the old bonus was capacity compensation. Reload takes the first 6
  points in full, a third of the rest, at most +12 (about 5% faster). Handling `0.25·E_rel`, at
  most +2.5. 20R in a 30R set ≈ +1.5/+7.5; 10R ≈ +2.5/+10…+11; 3R and 5R Saiga both +2.5/+12.
- **Material** (relative to the default): polymer +0.5 reload, ribbed/tapered +0.5,
  straight-wall −0.5. Translucent and windowed variants equal their opaque twin.
- **Stability** 0 everywhere.
- **Shotgun tubes** (R870 cap and +2…+8 extensions; RULES_MINED 11 says they belong with the
  MP133 extensions): relative to the default 4R cap, `reload = 1.5·E_rel`, `handling = 0.5·E_rel`
  (EV 0.9). The lower reload share is deliberate: these are per-shell loaders, so one reload point
  already scales every shell, and a full tube adds shells to load anyway. The handling share is the
  extra shells' mass at the very front. Range +2: −1/−3 to +8: −6/−18.
- Plates, adapters and the coupler in this family follow `rules/mag_control.py`.

## EV drift (intended, 37 flagged items across both families)

- **Short mags (3R–20R)** fall to about half of their old value (e.g. Saiga 3R +19 → EV +6.3,
  PMAG 10R +11 → +5.9). This is the lead's rule: the old bonus was compensation for capacity.
- **Very large mags** (100R casket −25 → EV −13.9, RPK-16 95R −18 → −12.7, Centrefire 60R −17 →
  −12.7): the reload floor. Their weight (0.9–1.9 dw) now charges the draw/stow/stamina share of
  the old penalty (RULES_MINED 3.4).
- **Zero-reference shifts**: the R870 tubes (constant +11), Mosin (+3), KOSCH .40 (+2.5) sets
  are re-centred on their default; the R870 and Mosin bases absorb it at calibration. Until
  `--calibrate` runs, R870 reference builds show reload about 16 lower than today.

## Dominations and "best in all three"

- 46 pairs, all in the two shotgun tube sets: tube capacity is not a sheet column (it comes from
  the Studio `mag_space_add` flag), so `check_family` cannot see the trade. Each longer tube holds
  more shells; nothing is actually dominated. Two of the pairs are `mp153_4r_mag_cap` (see below).
- Every short mag is "best in its set on all three": stability is 0 for all mags and capacity is the
  trade, which that check ignores. Expected.

## Decided myself

- Reload cap for short mags +12, handling cap +2.5, knee −15 and floor −25 for long ones.
- Steel mags keep their old +1 over polymer (it paid for their extra weight, which still costs
  about the same) except for the small material reload term.
- `custom_hart_smg_9x19_50r_extension` (−45, deliberate per RULES_MINED 9.8, unreachable) takes
  the floor: h −11.5, r −25, EV −16.9.

## Override (1)

- `9x19_glock_stick_31r_vector`: old +16 is a known anomaly (RULES_MINED 9.9); valued as its twin
  `9x19_glock_stick_31r` (−1/−6.5). Unreachable.

## Misfiled / for the lead

- `mp153_4r_mag_cap` (MP133 default tube cap, E +12) is in the **optic** family and currently
  gets h +18, s +2.5. It should be 0/0/0 like `r870_std_4r_mag_cap` (default reference; MP133
  base absorbs the +12). I did not write it because it is outside my files.
- `kosch_default_small/large_mag_plate`, `nbs_ar15_9x19_hart_mag_adapter`,
  `custom_hart_smg_mag_coupler` are plates/adapters filed as magazine; handled by the mag_control
  rules (all 0 except the coupler, −0.5/−4.5).
- `kalis_kosch_*_magex2` capacity cells (17, 18, 23) read as rounds added, not totals (a 9x19
  KOSCH with the 23R MagEx2 would hold 40). Left alone; worth a check against the game.
