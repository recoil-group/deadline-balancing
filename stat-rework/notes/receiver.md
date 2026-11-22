# Receiver family: re-stat notes

Rules live in `rules/receiver.py`; 2 hand overrides in `overrides/receiver.csv`. Weight credit is 0
(RULES.md section 3). Default parts stay the zero reference; parts with old ergonomics 0 stay 0.

## Split rules (fractions of old ergonomics: handling / reload / stability)

| Kind | Split | Why |
|---|---|---|
| Upper receivers, full receivers (G3, AUG, R870, MP5, SCAR uppers), PSG1 reinforcements | 0.9 / 0 / 0.9 | the spine of the gun; nothing to do with the magazine |
| Lower receivers (AR, SCAR, AK, AK12/308, UMP, Scalar) | 0.5 / 1.2 / 0.3 | the magwell lives here; aftermarket lowers sell flared magwells and ambi controls |
| Pistol slides | 0.8 / 0.6 / 0.6 | lightening cuts (handling), serrations for racking on empty reloads (reload), slide mass (stability) |
| Pistol frames | 0.7 / 0.3 / 0.9 | grip-like: beavertails, checkering, rails steady the hold |
| Dust covers | 0.9 / 0 / 0.9 (lean 0.35) | slim stamped cover vs rigid railed cover |
| HK G3/MP5 trigger housings | 1.0 / 0.4 / 0.5 | they carry the pistol grip: grip-like split |
| QBZ95 handguard/trigger housing | 0.9 / 0.1 / 0.8 | it is a handguard |
| R700 chassis and the REV21 lower (compete with stocks) | 0.8 / 0.3 / 0.9 | stocks in all but name; same split as the stock family default |
| Slide catches, stops, releases | 0.6 / 1.4 / 0 | reload controls |
| Railed frame covers | 1.2 / 0 / 0.5 | small bulk penalty |
| Optic plate covers, filler plates | zero | a plate does nothing; it is the "no optic" option |
| Castle nuts, endplates (stock-system parts) | zero | per lead; `thorsden_frs15_gen3_ar15_endplate` (stockless) keeps +1.5 handling, the lost stock already costs stability and it keeps its +9/+9 recoil and +0.55 deviation |
| Trunnions, backplates, other small parts | 0.8 / 0.6 / 0.6 | default; all only-choice |

**Mass rule (lean 0.5 unless noted):** inside a competing set the lighter of two like parts leans to
handling, the heavier to stability, EV-neutral. `z` runs from −1 (lightest) to +1 (heaviest) over the
set's weight range; a share `0.5·z` of the value moves from handling to stability (scaled by
0.60/0.47 so EV is unchanged). Negative values lean the other way: a light part with a penalty takes
it on stability ("made of knives": EDC X9 custom-cut slide, TT33 pre-war slide, KOSCH Mk2 frame),
a heavy one takes it on handling (bulk: MP5SD upper, RMP3 receiver).

Results: P229 slides lean handling, P226 Elite/Mk25 slides stability; MC51K handling, PSG1 uppers
stability; plain AK covers handling, railed covers stability; Novacek/Ardian lowers reload plus
stability, Equinox lower reload plus handling. EV drift: none beyond tolerance.

## Overrides

- `hart_m16a2_carry_handle_upper_receiver` h2 / s9: the fixed carry handle is bulk on top (optics sit
  high), so it should not tie the flat-tops on handling.
- `kf_m27_iar_upper_receiver` h−2 / s+1: heavy IAR upper is slower but steadier than the 416D/A5
  uppers (otherwise the A5 was best on all three).

## Remaining dominations (all explained)

- **UMP lowers** (`*_012d_*` dominated by `01d`, `01`, `012`): the lowers differ in fire modes (0-1,
  0-1-2, with or without D = full auto), which no stat shows. Old sheet identical.
- **Scalar lowers** (9x19 and .40 over .45 ACP within each generation): calibre choice; .45 ACP's
  payoff is in its ammunition damage, not in the lower. Equal weights, so the mass rule cannot help.
- **`tt33_postwar_slide` > `tt33_mod_postwar_slide`**: the modified slide is the full-auto conversion
  (hidden fire mode). Old sheet identical.
- **`hart_m4a1_receiver_endplate` > `kf_416a5_sling_eyelet_endplate`**: both zero; the eyelet plate is
  a visual/sling variant 0.01 dw heavier (old sheet identical).
- **Plate covers > optics** in the DeltaPoint/DRD footprint slots: the optic's value is the sight
  itself; not a real domination.

## Best on all three (left, with reason)

`ptr_32_7.62x39_upper_receiver` (calibre conversion, $10000, 13.5/0/13.5; the largest values in the
family, kept because it is the old outlier, flag for the lead), `hk_psg1_metal_trigger_housing` and
`hk_mp5_sef_polymer_contoured_trigger_housing` (the alternatives are 0 or negative; they pay in
recoil and price), `r870_serbu_shorty_receiver` (pays +2/+2 recoil), AICS chassis frame (only best
among receiver-family items; the competing stocks are higher), `tt33_postwar_slide` (default 0 vs
hidden-benefit alternatives), KOSCH slide backplates (0, against auto sears whose payoff is fire
rate; see `notes/internals.md`).

## Misfiled / notes for other families

- R700 chassis (`precision_intercontinental_..._folding_chassis_frame`, `mcs_lss_gen2_carbine_chassis`,
  `mcs_rev21_gen2_r700_lower_receiver`) are stocks; statted with the stock default split so they line
  up with `magtap_hunter700_short_action` and the Rogue stock. The stock agent may want to check.
- Castle nuts and endplates are stock-system parts (kept, near zero).
- `hk_ump9_upper_receiver` (+7, −25/−23 recoil) is a calibre conversion; lightest, so 10 / 0 / 2.
- `glock20_*` and `glock17l_slide` are unreachable in the tree; Glock20 is not in `tree.json`, so
  `simulate.py --weapon Glock20` fails.

## Round 5: reload scope

Only the Novacek N4 Gen3 lowers (flared magwell, −3%) and the KOSCH ambidextrous slide catch (−2%) affect reload (RULES.md section 13). Every other receiver holds 0, with its old reload share moved into handling and stability (EV kept). That covers the ADAC-15, whose release and bolt catch are separate parts, the Scalar calibre lowers, the FANG-H AR lower, the R700 chassis (the R700 always takes detachable magazines), slides, frames, trunnions and trigger housings.

## Round 7: profiles and roles

Handling and stability now come from each part's row in `profiles/receiver.csv` (RULES.md section 15); the split rules, weight leans and overrides above are history for these two stats.

Receivers are `even`: nothing about an upper, lower, slide or frame favours one stat. The role uppers (Mk20, MK12, PSG1, M27 IAR marksman; MK18, MC51, MC51K strong, Serbu Shorty compact) carry the swing; the Mk20's old +5 only compensated its weight and now turns into stability. The AICS chassis frame is `even`, since its buttstocks are separate precision-stock parts (lead). The FRS-15 Gen3 end plate is a stockless option.

Profiles: even 189, zero 24, reload_only 7, handling 1, mount 1, stockless 1. Unidentified counterparts: 0.

Role parts:

- `aft_mk20_upper_receiver`: marksman, FN SCAR Mk20 SSR upper receiver
- `aft_mk20_upper_receiver_for_scar47`: marksman, FN SCAR 20S / Mk20 SSR upper
- `axtell_defense_mk12_upper_receiver`: marksman, Daniel Defense MK12 SPR upper
- `axtell_defense_mk18_upper_receiver`: compact, Daniel Defense MK18 upper receiver group
- `ferro_ordnance_mc51_upper_receiver`: compact, FR Ordnance MC51 (HK51-type short G3)
- `ferro_ordnance_mc51k_upper_receiver`: compact (strong), FR Ordnance MC51-style G3 with MP5K handguard
- `hk_psg1_metal_trigger_housing`: marksman, HK PSG1 trigger group housing
- `hk_psg1_upper_receiver`: marksman, HK PSG1 receiver
- `hk_psg1_upper_receiver_modified`: marksman, HK PSG1-pattern receiver (modified)
- `kf_m27_iar_upper_receiver`: marksman, HK M27 IAR upper
- `r870_serbu_shorty_receiver`: compact, Serbu Super-Shorty 870 receiver
