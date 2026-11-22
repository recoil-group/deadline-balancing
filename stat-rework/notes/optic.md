# Optic family: re-stat notes

Rules in `rules/optic.py`, overrides in `overrides/optic.csv` (1 row). No weight credit (lead
decision, RULES.md section 3): every rule works from the old ergonomics `E`.

## Rules applied

| Sub-category | Rule | Typical result |
|---|---|---|
| Compact sights (E ≥ −2): 1x red dots, micro reflexes, holos, 1x/2x prisms, magnifiers, the −2 Russian collimators | handling = E, reload 0, stability 0 | micro dot −1.5 → h −1.5; EXPS3 −2 → h −2; G33 −1 → h −1 |
| Magnified or bulky sights (E < −2): ACOG/ELCAN/fixed prisms, PSO/PU, LPVOs, big scopes, NV, the two oversized reflexes | handling = 1.5 E, stability = 0.2 E, reload 0 | ACOG −3 → h −4.5 s −0.5; Vudu −6 → h −9 s −1; ATACR −7 → h −10.5 s −1.5 |
| Mounts, risers, rings, spacers, footprints, adapter plates, offset mounts | handling = E, rest 0 | most stay 0; carry-handle rails −4/−4.5, AK side rails −2/−3, Mosin trirail −4 |
| Caps, covers, eye cups (and other sight accessories) | same factors as the sight they fit | PSO-1 chelomo cup +5 → h +7.5 s +1; Aero covers +0.5/+1 → h +0.5/+1 |
| Iron sights filed under optic (ZVN-64 night inserts, R870/Glock20 rear, DeltaPoint rear iron) | iron sight rule (h 1.5 per old point) | +1 → h +1.5 |
| Suppressor heat shields | old value as handling | +2.5 → h +4 |
| Misfiled parts (see below) | their real family's rules (`rules.restat` with that family) | |

Why:

- **Handling only.** A sight's cost is getting the eye on it: size, height, eye box. It does not
  change the reload. The lead's rule says stability is zero or very small; I give magnified and
  bulky sights `0.2 E` (−0.5 to −1.5): a heavy tube high above the bore is a little top-heavy.
  Compact sights get 0.
- **Two bands instead of one factor.** The old sheet set optic ergonomics by class, not mass
  (RULES_MINED §1, §3), so `E` is used as the class. Compact sights take `h = E` (EV 0.6 E): they
  never slowed the reload, and their draw and stamina cost is now carried by their (small)
  weight. This is the lead's "small reflex sights near zero". Magnified and bulky sights keep
  their old value (EV ≈ E) as a clear handling cost. Every EV move is under 2 points.
- **Mounts stay free.** The team made mounts and risers 0 in 0.25.4 (f0db2dc, 7a3a261) and
  compensated the Vudu for it. I did **not** add a height cost to tall mounts, against the lead's
  starting rule: a 1.93" mount and a 1.41" mount of the same product would become strict
  dominations for a 0.3-EV difference, turning a look/co-witness preference into a trap. The
  mounts that kept a bulk penalty keep it, at h = E (EV 0.6 E, "a little handling").
  Offset/canted mounts are −0.5/−1 handling: near zero. If the lead still wants a height cost,
  the clean place is a small table in `optic.py` keyed on the height in the name (1.93", "high").
- **Accessories follow their host,** so the sight plus its caps or cups moves exactly as the old
  total did. Hosts that are not sights (the OWL laser's lens caps) use the host family's default
  split.

## Assemblies with odd positives (kept on purpose)

Eye cups, covers and caps are free, optional and positive, so in practice the sight's value is
sight + accessory. Totals with every accessory fitted (old → new):

| Assembly | old E | new h / s |
|---|---|---|
| Geiss ZFK 4x + front and rear cups | +4 | +6 / +1 |
| PSO-1 (Chelomo) + Chelomo cup | +2 | +3 / +0.5 |
| PSO-1 picatinny + both NPZ cups | 0 | 0 / 0 |
| Hetzel Z24 4x + covers | +2 | +2 / 0 |
| PSG1 ZF 6x42 + eye cup | −0.5 | −0.5 / 0 |
| NSPU-M NV + cup | −5 | −7.5 / −1 |
| Orion NV + cup | −6 | −9 / −1 |
| Holostar Aero + folded covers | 0 | 0 / 0 |

Under the team's strength score these cups mostly offset heavy Russian glass (0.27–0.45 dw). The
Geiss ZFK and Chelomo PSO-1 nets are positive for a 4x scope; that is an old oddity I kept
because the brief says to keep assembly totals. Worth a team look.

## Overrides

- `agr_870_protection_cap` (+14, +8/+8 recoil): the cap closes the AGR-870 grip when no buffer
  tube and stock is fitted, so it is a stockless configuration. h 16, r 4, s 2 (EV 12.1): fast,
  but far less steady than a real stock (stocks get about +13 stability). It should stay in line
  with `r870_earthquake_raptor_pistol_grip` (pistol_grip family), the other stockless R870 option.

## Misfiled items (re-statted with their real family's rules)

- Handguard rails, panels and top rails: `pro_tactical_upr_16_4_*`, `cosmotac_marsv2_*`,
  `calsport_handguard_*_accessory_rail_*`, `veles_b_2l/2u_*_rail_*`, `ihs_aug_a3_sa_cqc_*`,
  `cerberus_arms_aug_cantiliver_forend_*`, `pac_mre_*_front_filler_tube`,
  `pmm_scar_heavy_duty_mlok_bottom_panel`, `target_sports_mmh94_*_top`,
  `archient_technologies_ak_gastube_mount_type1/2` → handguard.
- AUG foregrip-slot rails and RK grip adapters: `aquila_defensio_aug_forward_accessory_rail`,
  `steyr_aug_a3_xs_bottom_accessory_rail`, `rk_foregrip_mount`, `rk_short_foregrip_mount`,
  `rk_b25_angled_mount` → foregrip.
- `mp153_4r_mag_cap` → mag_control. Its rule rebases the MP-133 tube slot on the default cap, so
  the cap goes to 0 and its +12 moves to the weapon base. This is the one item flagged for EV drift
  by `check_family.py`, and it is intended.
- `arid_concepts_charging_handle_mount` → internals; sling mounts and swivels → misc; light
  tailcaps → tactical; KALIS Scalar folding-stock mounts → stock.
- `agr_870_protection_cap` is a stock-slot part (override above).
- `lowenherz_aug_a1_stg77_1_5x_scoped_receiver` (RULES_MINED §11) is filed as receiver here,
  which is right; its integrated 1.5x scope is the receiver family's call.
- `cosmotac_vism_micro_green_dot_red_laser` is a 1x dot with a laser; its −3 puts it in the bulky
  band (h −4.5). The laser part may belong in `lasers.csv`.

## Remaining dominations (all explained)

`check_family.py optic iron_sight` lists 85 pairs. None is a real like-for-like trade-off failure:

- **The optic does something the stats don't show:** a slide cover plate or filler against a
  reflex sight; a 1x microprism against a 3x ACOG; 3x against 5x prisms (Alistair); Hart Retro
  against Ultracross 4x. Magnification and FOV live in `optics.csv`.
- **Same part, different state or colour:** folded against closed lens caps and covers (Scipio4T,
  Aero). I kept the old folded > closed order, since closed caps block the view.
- **Weight-only differences inherited from the old sheet**, with equal stats and 0.01–0.04 dw of
  real weight difference: Kazarov dovetail rails, Scipio5 against Scipio4B, PK-A and OKP-7
  against Rakurs, DeltaPoint against HELX, RS Regulate lower mounts, 1P78 dovetail mounts,
  OpTech KOSCH mounts, tailcaps, 6" against 7" heat shields, short against long Calsport/Veles
  rails (the long ones give more rail room).
- **Old penalties on alternatives that host the same rail:** the Strauss Mark 4 against the PRI
  carry-handle mount, the R870 top mounts, the Target Sports MNG against the Mosin trirail, the
  MFI against the B&T MP5 rail, and Resolute against the MI24C (handguard family).
- **Best in set on all three:** every 0-value mount in the big picatinny sets. These sets mix
  mounts and sights, a mount's cost lives in the sight it hosts, and no sight has positive
  reload or stability. This is structural, not something to fix.

## Open points I decided myself

- No height cost on tall mounts (reason above).
- The Orion NV scope alone is h −12, beyond the usual ±10, but −9 with its cup, which everyone
  fits.
- Compact sights lose EV (0.6 E) on purpose; the weapon-base calibration absorbs the average.

## Round 5: reload scope

Optics, mounts and sling hardware are not reload parts. The five that carried reload (two sling mounts, a swivel, the AUG sling mount, the charging-handle mount and the stockless AGR-870 cap override) have it moved into handling and stability (EV kept; `reload_scope.py`).
