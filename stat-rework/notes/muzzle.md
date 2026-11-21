# Muzzle family: notes

Rules live in `rules/muzzle.py` (also used by `rules/barrel.py` for muzzle parts filed as barrel).
`overrides/muzzle.csv` has no rows. Weight credit is 0 (lead decision, replacing the starting
rule's `adjusted_ergo(item, 5.0)`): muzzle penalties track device type and can length, not weight.

## Rule

Every device keeps its old value, EV(new) = old ergonomics E (0 EV drift in check_family).
Stability takes a share of E set by what the device adds at the muzzle, and handling takes the
rest: `s = share · E`, `h = (E − 0.47 s) / 0.6`, both in 0.5 steps.

| Kind (Studio category) | share | reason | typical E → h / s |
|---|---|---|---|
| Suppressor | 0.3 | length and front mass: a clear handling cost, a small stability cost | −5 → −7 / −1.5; −7 → −10 / −2; −1 → −1.5 / −0.5 |
| Brake, compensator, "muzzle device" | 0.5 | blast and concussion unsettle the hold as much as the swing | −1 → −1.5 / −0.5; −2 → −2.5 / −1; Barrett-style −6 → −7.5 / −3 |
| Flash hider / eliminator / moderator, blast regulator, suppressor cover | 0.5 | short and light; the old +1…+2 over brakes is "no blast" | +2 → +2.5 / +1 |
| Thread protector | 0.5 | bare muzzle, shortest and lightest end | +3 → +4 / +1.5 |
| Thread adapter, piston, suppressor mount or cap, Tiduro module | 1.0 | pure length, nothing else | −1 → −1 / −1; 0 → 0 |
| Barrel extension | −1 stability per inch, as barrels | it is barrel length | IPS 1" −1 / −1, 2" −2 / −2, 4" −2 / −4 |

- **Decision on heavy, short cans:** no stability gain for mass. RULES section 1 says front-heavy
  ends sway more, and the barrel rule treats muzzle length the same way. Mass is not a reliable
  signal here anyway, because suppressor weight is compressed to about 0.6 of real.
  Shorter, lighter cans carry less stability cost simply because their old penalty is smaller
  (DTKP shortened −3 / −0.5 vs DTKP −4 / −1; TB Ultra 5/7/9: −1.5/−0.5, −4/−1, −7/−1.5).
- Loudness, recoil, velocity, deviation and damage are unchanged.
- Category-less unreachable rows: `ips_9x19_1inch_barrel_extension` is treated as an extension,
  `custom4port` as a brake (by name), and `fd917` as a suppressor (by its loudness).

## Stacking reminders (from the Studio flags)

- Only the last flagged muzzle device counts. Unflagged parts always count and stack:
  - thread adapters, barrel extensions;
  - the Obsidian9 body and extension, EGS Orthocone, Spiderweb SRM-6 and Tiduro modular
    compensator;
  - the Halbek, the PAC suppressor covers, the Watcher Armory comp weight, the TT PM-Laser DTK and
    the SAI JailBrake.
- So these real totals apply:
  - Obsidian long (body + extension): h −10 / s −2.
  - Spiderweb BPR-1425 + SRM-6: h −10 / s −2.
  - Tiduro 5-baffle + modular comp: h −11.5 / s −2.5.
  - Halbek on the FAR Belgian: h −4 / s −1.5.
- **PAC suppressor covers (+1, unflagged) stack on top of the can,** so a cover takes 1 point off
  the can's penalty for free (h +1.5 / s +0.5). This keeps the old value. A cover adds bulk, so a
  0 or small negative value would be more physical. **I left it for the lead to decide.**

## Remaining dominations (3)

- `alphadog_alpha9_flipped` > `alphadog_alpha9`: visual variants. The old sheet already has them
  at −5 vs −6, and the split carries that over. Equalising them would change old ergo; flagged for
  the lead.
- `ewc_5.56x45_blackout_18_tooth_flash_hider` > `hart_607_car15_3.5inch_flash_moderator`: same E,
  the Hart is 0.08 dw heavier and 1 point worse on vertical recoil. It is a retro look part and
  was dominated in the old sheet too.
- `v762_vr05t_mb` > `v762_vr05_mb`: variants, 0.01 dw apart.

## Best in set on all three

Muzzle devices have no reload effect, and the split keeps the sign of E on both handling and
stability. So the highest-E devices in each set (thread protectors +3, the +2 flash hiders,
AK-12K and VR-DTL +3) are best on all three new stats. Their trade is recoil and loudness, which is
large: a thread protector has 0/0 recoil against −10…−15 for any device. That is unchanged from
the old sheet, where they were also best in ergo.

## Items that look misfiled

- In `barrel`, but muzzle-slot parts (handled here through `rules/barrel.py`): the IPS barrel
  extensions, the thread adapters, the Obsidian9 body and extension, the EGS Orthocone suppressor
  and piston, the Spiderweb SRM-6, the Mosin Bramit, the Halbek, the Tiduro modular compensator
  and the QD ASR mount.
- `sai_jailbrake_handguard_extension` (Muzzle Device, hosts rails) is a handguard-and-brake
  combination. It is treated as a brake.
