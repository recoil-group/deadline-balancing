# Handguard family: re-stat notes

340 items. Rule: `rules/handguard.py`. Overrides: `overrides/handguard.csv` (2 rows).
EV (0.60 h + 0.40 r + 0.47 s) equals the old ergonomics for every item, give or take rounding.
No weight credit, following RULES.md section 3. No other columns were changed; the +0.03 deviation
on drop-in handguards stays as it is.

## Rules per sub-category

**Main handguards** (whole handguards, AK/SA58/AK-12 lowers, XM177 bottom half, SCAR extensions,
SCAR bottom rails, KF416, MP5, G3, SA58, Scalar):

- `stability = 0.6 x median E of the pool + 16 x (weight - median weight of the pool)`;
  `handling = (E - 0.47 s) / 0.6`; `reload = 0`. Both are floored at 0 for positive E (stability is
  capped at E / 0.47).
- I used weight as the reach measure. Inside a set it tracks length (r = 0.90 for length against
  weight across the AR and KF416 sets, where lengths can be parsed from names). A quad, RIS or RAS
  rail that is heavier at the same length leans stability, as the lead's rule asks. Names did not
  add anything that weight does not already show.
- The pool is every handguard-like part that competes with the item. `_alt` twins use their base
  item's pool, so identical AK lowers get identical values. The XM177 bottom half uses the M4 pool.
  Only-choice items with no pool (PSG1, Ardian, MCS REV21, Cerberus) get s = 0.6 E.
- Handguards do not touch reload. The weapon-base calibration absorbs the reload that the default
  split used to give them.
- Resulting spreads: M4 h 2..25 / s 3..8; AK h 1.5..22.5 / s 6.5..11; KF416 h 0..15.5 / s 3.5..6.5;
  SA58 h 2.5..19 / s 4.5..11 (the wood full-length at 0.5 dw is the most stable); MP5 h 8..17.5 /
  s 4.5..5.5; G3 h 0..7 / s 1.5..2.5; SCAR extensions h 1..6 / s 0..2.5.
- **Why the handling spread is wide:** old handguard ergonomics falls with length (M4: 14 at 4",
  5 at 18"). If the long one is also to be more stable, the handling gap has to be at least
  1.67 x the old ergonomics gap. That follows from the EV prices (one handling point is worth only
  0.6 old points) and does not depend on the constants I chose. The M4 handling gap is about 18
  points (about 90 ms of ADS), against 9 old ergonomics. Long handguards keep their old advantage
  in recoil and gain about 5 stability.
- The handguard with the best recoil in each set (M4 `sp18m`, SA58 wood full length, KF416 Vallais
  14.5", G3 PAC long RAS) has the top or near-top stability but the lowest handling. None of them
  wins every new stat.
- KALIS Scalar: the Nov 18 tuning is kept. EV order is unchanged (Gen III 5.5" 0.9 < 10" 2.0;
  Mk1/Mk5 2 < Mk3/Mk9/Mk11 3). The Gen III 16" shroud is filed under `barrel`. If the barrel owner
  puts it on the same reach rule, it comes out at about h 4 / s 3.5, which keeps it the most stable
  option of its set.

**Upper halves** (SA58 RSA tops, Target Sports tops): `0.7 / 0 / 1.25`. They add length and mass
over the barrel, not grip. The RSA tops are only-choice per lower and simply add to that lower.

**AK top covers:** a 0 stays 0. A +1 cover (Magtap MOE, Veles Leader, Veles LV Sport) counts as
grip texture, like a panel (h 1 / s 1). The T1 and 30 mm sight-mount covers (-3) are sight height:
`1.2 / 0 / 0.6`, giving h -3.5 / s -2 (slower on target, looser cheek weld). The Khyber "cheese
grater" (-1) is light but uncomfortable, so s -1.5 ("made of knives"). The Veles B-32 Klassika
(-3, 0.23 dw) is front bulk: h -4.5.

**Bullpup top rails and carry handles** (AUG A3 top rails, QBZ long-bow handles, ACP95): they compete
with sights and optics, so I gave them the sight/optic split `1.5 / 0 / 0.2`. A negative one is bulk
on handling only. The QBZ long-bow MLOK at E 11 becomes h 16.5 / s 2.

**Rail panels, M-LOK covers, rail covers** (first four count): grip texture. Stability is
`round_half(E)` and handling takes the rest of the value, so a larger panel is never worse than a
smaller one. Values: 0.25 gives 0 / 0.5, 0.5 gives 0.5 / 0.5, 1 gives 1 / 1, 1.5 gives 1.5 / 1.5,
1.75 gives 1.5 / 2, 2 gives 2 / 2, 2.25 gives 2 / 2.5. No reload. CGR panels stay cosmetic twins of
the 0.5 panels.

**Bare rail sections** (generic, DDG, Magtap 1.6, PAC M-LOK picatinny sections, `lm2`): h -0.5 /
s -0.5. That is a sharp edge under the hand plus a little bulk. Weight already scales with slot
count.

**Rails, rail mounts, side rails, gas tubes, retainers:** a 0 stays 0. Negative values are bulk or
a raised mount, all on handling (`1.5 x E`):

| Item | Handling |
|---|---|
| FIT M4 forward rail (-5) | -7.5 |
| Resolute MI-24C (-4) | -6 |
| MCS R700 long rail (-2) | -3 |
| IHS AUG side rails, UMP bottom rail, ACP95 side rail, HK upper rail, Spinner rail base | -1 to -1.5 |

The +1 TAS RS47 side rails count as grip texture (1 / 1). Both AK handguard retainers (+1, only
choice) are zeroed because a retainer has no physical effect; the base calibration absorbs the
value.

## Overrides (2)

- `kalis_scalar_mk5_handguard` h 2 / s 1.5: rounding erased its 0.01 dw of extra reach, which left
  the Mk3 strictly better. The Mk3 was strictly better in the old sheet too.
- `veles_b_11_lower_handguard` h 15 / s 8.5: rounding tied it with the lighter issue wooden AKS-74U
  lower, which then won every stat.

## Remaining dominations (110 pairs, 35 items), all explained

- **M-LOK picatinny rail sections:** identical -0.5 / -0.5, with weight rising with slot count. A
  longer section buys mounting room, which no stat column measures. This is the 0.25.3 design,
  where the cost moved into weight.
- **Zero-stat rails** (OMM boards, Scalar side and misc rails, Vallais accessory rails): length
  variants of a 0 part. Weight is the price of more slots.
- **Resolute MI-24C rail system:** dominated by the optic-family ResoluteInd Low Pro mount, as in
  the old sheet (-4 against -2). The MI-24C is a full-length scout rail system. Its value is
  utility, not stats.

## "Best in set on all three" left (all accepted)

- The largest rail panel or M-LOK cover in each rail family. Coverage is the rule: more stats for
  more weight.
- +1 top covers among 0-stat covers (Magtap MOE, Veles Leader and LV Sport). They pay with price,
  and the 0 covers carry their recoil.
- AUG SA XS top rail (E 5): it pays with +1/+2 recoil. AUG M1 rails: all negative, ties.
- QBZ long-bow MLOK handle: compared only with my family's items. The issue carry handle
  (`iron_sight` family, E 10) would be h 15 / s 2 under the same split.

## Coordination with other families

- `sanxian_qbz95_carry_handle` (iron_sight) and the AUG top-rail competitors filed as optics
  (Cerberus mount, A3SF scopes, IHS CQC top rail): I assumed the default sight/optic split
  `1.5 / 0 / 0.2`. If those owners change it, the QBZ and AUG top rails should follow.
- `kalis_scalar_gen3_16inch_mlok_barrel_shroud` (barrel): suggested h 4 / s 3.5 (see above).
- `hk_mp5k_polymer_handguard` (foregrip, misfiled; it is a handguard with no competitor): the
  handguard median split would give h 18 / s 9.

## Misfiled items

- `handguard_flip_up_sight` and its folded twin are iron sights (sight split, h 1.5 / s 0).
- `fit_m4_forward_picatinny_rail` competes with barrel-family gas-block mounts and a sling swivel.
- `resolute_ind_mi24c_mount` competes with optic-family scope mounts.
- `railscales_rsb_vg` (not in Studio) is a rail scale with a vertical grip, so it gets the
  foregrip split.
- `haga_defense_usc_extended_handguard` and `centrefire_628lmf_b_mp5_handguard` are not in Studio.
  They get the no-pool median split.
- `hart_xm177e1/e2_slim_plastic_handguard`: 0 weight and 0 stats. The stats sit on the bottom half,
  which is correct, but the 0 weight is odd (RULES_MINED 9.9).

## Open points I decided myself

- **Reload is 0 on every handguard.** The default split gave 0.1 E, which has no physical basis.
- **Stability magnitudes are modest** (M4: 3 to 8). Low-ergonomics long handguards already exceed
  1.5 x |E| in stability: the `sp18m` is E 5 and s 8, the KF416 Vallais 14.5" is E 2 and s 4.5.
  Raising `K_REACH` would break that bound further, so I left it at 16. The bound is the price of
  the direction the lead asked for.
- **Stability per dw is absolute,** not scaled per set. Sets whose weights barely differ (for
  example the AKS-74U lowers) correctly get almost no stability spread.

## Round 7: profiles and roles

Handling and stability now come from each part's row in `profiles/handguard.csv` (RULES.md section 15); the split rules, weight leans and overrides above are history for these two stats.

Handguards are `even`, with the mild lean only on the clearly longest (`handguard_long`, 18 rows) and shortest (`handguard_short`, 6) of a set. The role handguards are `even` plus their role, not a length lean on top (lead). Rail panels and covers are `zero` or `mount`. Spread against old ergonomics fell from 1.79× to 1.00×.

Profiles: even 208, zero 81, mount 20, handguard_long 18, handguard_short 6, handling 5, grip_angled 1, grip_vertical 1. Unidentified counterparts: 4.

Role parts:

- `kf_416_dmr_extra_long_handguard`: marksman, HK417/MR-style extra-long DMR quad rail for 416
- `kf_416c_handguard`: compact, HK416C handguard
- `mcs_rev21_gen2_15inch_r700_mlok_handguard`: marksman, MDT TAC21 Gen2 chassis 15in forend
- `quix_tacticals_ar15_4inch_ultralight_mlok_freefloat_hg`: compact, unidentified 4in ultralight free-float M-LOK AR handguard
