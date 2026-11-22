# Misc (77 rows: everything the family heuristic could not file)

## Rule (`rules/misc.py`)

Each misc item is given the family it physically is (`REAL_FAMILY`) and re-statted by that
family's own rules: `rules/<family>.py` when it exists, else that family's default split. Misc
values therefore follow the other families' final rules automatically. There is one hand-written
exception, the CQR spacers. Items with no old value stay empty.

| Physically | Items | Result today (other families' rules as of writing) |
|---|---|---|
| optic accessory, mount, drop-on rail | Kobra sunshade, Azimuth wrap, DeltaPoint cap, UMP top rail, Scout Scopes / SI AK drop-on rails, KOSCH slide cover plates, `um_3_wilson`, Paramount `_alt` rows, `stupid_camera` | sunshade h +1; rails −1 h; plates and covers 0; camera h −15 s −2 (unreachable joke) |
| iron sights and sight assemblies | G3 / MP5 sight assemblies, RPG-7 zeroing rail (and folded), Glock / ACOG / Hart / AKM sights (not in Studio) | +1 sights: h +1.5; assemblies 0 |
| handguard rails and hoods | Veles Leader / Sport extensions, MCS LSS NV hoods, MK10 adapters, `rail` | Leader insert h +1 s +1; MCS hoods h −3; MK10 h −1 |
| stock parts and pads | Veles PT parts, AICS cover, Hunter 700 LOP spacers, RPG-7 / PSRL shoulder pads | LOP spacers h +0.5 s +0.5 each; pads stay empty |
| grips | FIT palm shelf, Pachmayr Glock grips, RPG-7 rear grip | shelf h 3 r 1 s 1.5; RPG grip h 4 r 1.5 s 2 |
| magazines and mag parts | Nexa P226 +4 extension, KRISS MagEx2, P320-X mag funnel, Glock 20 release, Scalar mag-release cover | Nexa h −0.5 r −4.5; funnel r +2.5 |
| receivers and internals | Scalar ports, covers, guide shaft, CH support; UMP BCGs; 416 gas systems; G3 CH; P320 FCU; PM trigger connect | all 0 (all were 0) |
| tactical sub-part | RUSH legacy crane connector | 0 |
| none of these | AK cleaning rods, the cat (`maxwell_grip`) | 0 / empty |

**CQR spacers** (Hera CQR grip-stock, required, 15 mm default): a longer spacer moves the
shoulder contact back. The gun is steadier but longer to bring up, so stability rises with length
and handling drops a little. Before, the 45 mm was simply best.

| | old E | h | r | s | EV |
|---|---|---|---|---|---|
| 15 mm | +2 | 1.5 | 0.5 | 2 | 2.0 |
| 30 mm | +4 | 1.5 | 0.5 | 6 | 3.9 |
| 45 mm | +6 | 1 | 0.5 | 10 | 5.5 |

Stability 10 is above the "1.5 × old" guide (9). These are stock parts, where ±20 is allowed, and
EV stays within tolerance. The reload 0.5 follows the stock family's small reload share.

## Remaining dominations (accepted)

- `zvetech_kosch_slide_cover` over the reflex sights in the same cut. This is the "no optic" plate
  against optics, not like-for-like.
- MK10 small adapter over large (×3). The same −0.5 old ergo; the large adapter's value is the
  longer rail section, which no stat captures.
- `si_ak_drop_on_rail` over `scout_scopes_ak_drop_on_rail`. Same price and ergo; weight is the
  only difference and is already priced. Brand variants.

## Misfiled (heuristic family "misc"; all re-statted by their real family above)

- Real optics and optic parts: `um_3_wilson`, `paramount_arms_slx_1x_microprism_acss_g2_scope_alt`,
  `paramount_arms_slx_1.53inch_straight_spacer_alt`, `stupid_camera` (a camera on a rail, −10).
- Iron sights not in Studio: `akm_rear_sight_6p1_sb2_1`, `truglo_glock_tfx_fs`,
  `glock20_front_sight`, `glock17l_front_sight`,
  `virticon_glock_supp_height_front_sights_wh_sf`, `acog_fs`, `acog_rs`, `hart_rear_ironsight_600m`.
- A magazine: `9x19_kriss_magex2_vector` (+23 rounds, −8). Pistol grips:
  `pachmayr_tactical_glock_grip_glove`, `pachmayr_rubber_grip_for_g20`.
- The RPG-7 rear grip is a pistol grip, and the launchers' shoulder pads are stock parts. They are
  only-choice slots, so their values effectively belong to the launcher bases.
- `whitehouse_rush_qe_junction_box_legacy_crane_connector` is a tactical sub-part.

## Open

- Misc values depend on the other families' modules, so re-run `check_family.py misc` after they
  settle. A module that raises falls back to that family's default split, with a note in `_rule`.

## Round 5: reload scope

The MagEx2, the Nexa P226 extension and the P320 magazine funnel keep reload (they are magazine parts). The CQR spacers, palm shelf, Glock grip sleeves and RPG-7 rear grip have their reload moved into handling and stability, EV kept (`reload_scope.py`).
