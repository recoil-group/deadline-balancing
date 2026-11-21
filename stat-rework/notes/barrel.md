# Barrel family: notes

Rules live in `rules/barrel.py`; one hand fix in `overrides/barrel.csv`. Weight credit is 0 (lead
decision); every barrel's EV is kept at its old ergonomics, so check_family reports 0 EV drift.

## Barrels (165 rows, category `Barrel`)

- **Value:** EV(new) = old ergonomics E. The trade comes from the direction of the split.
- **Stability = length.** −1 stability per inch relative to the weapon's standard barrel, cap ±8.
  - Standard barrel = the one old ergo was measured from: the set's free (price 0) barrel, else
    its 0-ergo barrel, else the free 0-ergo barrel of the same barrel class (used by the MC51 /
    MC51K / MC51SD and MP5SD slots, whose own barrels are not free: measured from the G3 406 mm and
    MP5 225 mm), else the slot default. The Studio slot default differs from the sheet's zero
    barrel for SCAR-H (330 mm default, 406 mm is zero), SCAR-L (254 / 355), SA58 (533 / 406) and
    AK-105 (314 / AK-74 415); the sheet's zero is used.
  - The length share is capped at |E − E_standard| and set to 0 when the old ergo moves against
    the length (threaded, match or caliber-conversion barrels of the same length get 0).
    Without this cap the shallow R870, AUG and R700 ergo slopes would have made long barrels
    *gain* handling.
  - Lengths come from the name (largest "NNNmm", ignoring calibres like 10mm) or the pretty name
    in inches. The unreachable CmmG Mk9 / KAK AR9 barrels have no set; they are measured from 406 mm.
- **Profile:** heavy / HBAR / bull / straight profile +1.5 stability (mass), fluted −0.5.
  Because EV is kept, the heavy barrel pays ~1.2 handling for it: HBAR 20" h −12 / s −4 against
  the A1 20" h −10.5 / s −5.5.
- **Handling = the rest:** h = (E − 0.47 s) / 0.6, limited to ±max(12, |E|).
- Velocity, recoil, deviation, damage and fire rate are unchanged: long barrels win there.
- Typical result (M4 set): 2" h +5.5 / s +6, 10.5" +2 / +4, 14.5" 0 / 0, 16" −5.5 / −1.5,
  20" −10.5 / −5.5, 24" fluted −12 / −8.5.

### Magnitudes and EV exceptions

- The limit on handling bites only for the extreme short barrels, which therefore land at the low
  end of the EV tolerance: Mosin 200 mm (E 25 → h 25 / s 8, EV 18.8), 220 mm (17.0 vs 22), MC51K
  145 mm (15.8 vs 20), MC51SD 125 mm (12.2 vs 14), SG58 8.25" (11.3 vs 13), FANG-H 267 mm (9.8 vs 12).
  All are within 25%. I accepted it rather than give a barrel more than |E| handling; these parts
  also gain 0.3–1.1 dw of mobility over the standard barrel.
- Standard barrels with non-zero old ergo keep EV too, so their handling is E / 0.6: AKM 415 mm
  −10, Mosin 730 mm −8.5, R870 508 mm +7.5, MP133 510 mm +2.5, AUG Para 420 mm +5, AKS-74U
  (only choice) +12. These are platform offsets that the weapon-base calibration absorbs. **The
  lead may prefer to move them into the weapon rows** (the old sheet's "default part is 0" rule).

### Override (1)

- `r870_211mm_sawn_off` h 6 / s 3: the old sheet rates it below the 325 mm (5 vs 6), so the cap
  left it with s +0.5. EV kept; the shortest barrel now leans to stability, the 325 mm to handling.

## Other barrel-slot parts filed here

- **Muzzle parts** (they follow `rules/muzzle.py`; see `notes/muzzle.md`). These are not Studio
  muzzle devices, so they always count and stack with the muzzle device:
  - IPS barrel extensions (5.56, 7.62x51): −1 stability per inch.
  - Thread adapters (IPS knurled, Gryphon 24-1/2, Infinite 24mm, CNC M14x1LH, Tubewerx M15x1RH,
    Rat Worx AUG, Fireline AK-12) and the EGS Orthocone piston: pure length.
  - Suppressor parts: Obsidian9 body and extension, EGS Orthocone, Spiderweb SRM-6, Mosin Bramit.
  - Rhodesian Halbek and the Odin Works Tiduro modular compensator: brakes.
  - Suppressors Inc. QD ASR mount: adapter, 0.
- **Default barrel split (1.0 / 0 / 0.85)**, small front parts with no length story: SCALAR
  barrel shrouds (E 3–4 → h 3–4 / s 2.5–3.5), the gas-block sling swivel (+2 → h 2 / s 1.5) and the
  tri-rail mounts (0), KF416 barrel nuts (+1 → 1 / 1), the TT-33 bushing, the RPG-7 and PSRL tubes,
  and the theoretical barrel (all 0).

## Remaining dominations (3 in this file's sets)

- `ak308_std_415mm_barrel` > `custom_ak308_..._threaded_barrel`, and `hk_ump45_200mm_flanged` >
  `hdts_ump45_200mm_threaded`: the threaded barrels pay for the thread, which opens the muzzle
  slot. The check cannot see slot access. The trade was already in the old sheet.
- `kf_416a5_14.5i` > `kf_416d_14.5i`: both free 0 / 0 standard barrels, visual variants
  (0.03 dw apart).

## Best in set on all three

Barrels have no reload effect, and both handling and stability favour short barrels. So the
shortest barrel of every set is best on all three new stats (M4 2", KF416C 9", SA58 8.25",
FANG-H, Mosin obrez, and so on). This is the lead's design: long barrels pay on all handling
stats and win on velocity, recoil, deviation and damage. I did not invent a counter-trade.

## Observations for the lead

- The hidden length scaling saturates today: `FirstPersonController.luau` uses
  `min(barrel_size / 1.5, 1)` for aimed turn sway and `min(barrel_size / 2, 1)` for strafe sway,
  with `barrel_size` the receiver-to-muzzle distance in studs. Rifle-length builds probably all
  sat at the cap, so today only short builds swayed less. With −1/inch, long rifle barrels now
  sway *more* than today, and short barrels gain as before. Not verified in Studio.
- Weapons whose standard barrel is inherently long (Mosin 730 mm, R870, MP133) lose no stability
  against shorter weapons because every standard barrel is 0. Weapon-level length identity, if
  wanted, belongs in `weapon_identity.csv`.
- `mosin_bramit_7.62x54r_suppressor` has category `Barrel` in Studio. It is a suppressor and is
  restatted as one.
