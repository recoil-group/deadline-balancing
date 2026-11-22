# Re-statting rules

These are the rules the rebalance was built on. `RULES_MINED.md` records what the old sheet and its
history imply; this file records the decisions taken from it. Stat meanings and the worth of one
point come from the code contract (summarised in `../knowledge/stats.md`).

**Since round 7, handling and stability come from section 15**: every part has a profile and an
optional role in `profiles/<family>.csv`, and `profiles.py` computes the two stats from it. Reload
(section 13) and cycling fire rate (section 14) are unchanged. Sections 4, 5, 9, 10, 11 and 12
describe the earlier split (family rules with weight-in-set leans, then a ×2 lean pass) and are
kept as history; where they say how handling and stability are split, section 15 now decides.

## 1. What the three stats own

| Stat | Owns | Physical drivers (better →) |
|---|---|---|
| `handling` | ADS in/out time, sight switch, fire-mode switch, mag check and other minor animations | light, short, slim front end; good grip angle; collapsed or short stock; low, small sights; nothing hanging off the front |
| `reload_time` | reload animations only (tactical, empty, quick, per shell); a fraction of the weapon's base reload time, **lower is better** | only magazines and capacity extensions (by capacity against the standard magazine), magazine controls (releases, magwells, mag assists, pull plates) and reload hardware (flared-magwell lowers, bolt and slide catches, enhanced charging handles, Mosin bolt work, R700 bottom metal); values per kind in section 13. Everything else is 0 |
| `stability` | idle sway (hip and aimed), sway while moving, breath-hold cost; **50 = today's feel** | mass at the shoulder and hands, a firm stock and cheek weld, front support (foregrips, handstops, bipods); worse with long barrels and front-heavy ends, no stock, braces, folded stocks |
| weapon weight (not a column) | draw, stow, sprint-out, aimed move speed, aim stamina drain, turn lag (held gun) and travel speed (all carried guns) | already priced by the weight column |

Fire rate also drives bolt and pump cycling now. On the manually cycled weapons, the parts that are
the cycling interface carry `fire_rate` (section 14); nothing else on them does.

## 2. Value accounting

One old ergonomics point bought ADS, reload, draw/stow, sprint-out and aim stamina at once. The
last three now come from weight, so what a part's new stats can carry is the ADS and reload part
of its old value, plus the new stability axis:

```text
EV = 0.60 * handling + 0.40 * reload_points + 0.47 * stability     (in old ergonomics points)
reload_points = (1.1 / (1 + reload_time) - 1.1) / 0.004            (1% of reload time ~ 2.75 points)
```

Reload is priced in points of the earlier 0–100 reload stat (contract v4: 0.9× playback at 0 to
1.3× at 100, so a point was about 0.36% of reload time). The family rules (`rules/<family>.py`)
still split each item in those points, as `reload_points`; `rules.restat` converts the reload share
to the sheet's `reload_time` (contract v5):

```text
reload_time = 1.1 / (1.1 + 0.004 * reload_points) - 1      rounded to 0.001 (0.1% of time)
```

The conversion is applied to the sheet's half-point value, so every part carries over exactly what
it had; a shared magazine has one value on every gun it fits. Half a point is at least 0.16% of
time anywhere in the sheet's range, so rounding to 0.1% keeps every competing set's order.
Overrides are written directly in `reload_time`.

The weights are the share of an old point's usefulness each new point carries (ADS ≈ 45%,
reload ≈ 30%, stability priced at ≈ 35%), normalised so that `h = r = E, s = 0` has `EV = E`.

- **A part's EV should stay close to its old ergonomics** : within
  about ±25% or ±2 points, whichever is larger. Bigger moves need a reason in the note (a
  physical correction, the CAG tilt, fixing an old oddity, or a deliberate trade-off).
- A family's default split vector has EV ≈ 1, so the first pass neither inflates nor deflates.
- Typical builds therefore keep their old total value, and weapon-to-weapon balance survives.

## 3. Weight: no double charge to remove

The contract warns that a part given negative ergonomics only for being heavy would now be charged
twice. The history says this barely happens (`RULES_MINED.md` sections 0 and 3):

- The team's own value model has always priced weight separately:
  `strength = ergonomics − 20·weight − 0.8·h_recoil − 0.6·v_recoil − …`, and competing sets were
  tuned to equal strength at 20 per dw (barrels most precisely).
- Within sets, negative ergonomics tracks length (barrels, handguards), capacity (magazines, tube
  extensions) or class (magnified optics), not mass. With capacity held fixed, magazine weight has
  no negative effect on ergonomics.
- What one dw costs after the rework is about what it cost before. Travel speed per dw halves
  (6.5% → 3.3%, ≈ 10 points), and held-gun mobility adds ≈ 9: 15 mobility points per dw act on
  draw, stow, sprint-out and aim stamina at the rate one old ergonomics point did (≈ 25% of an old
  point's worth, so ≈ 4), plus aimed movement speed (≈ 4) and turn lag (≈ 1). Total ≈ 19–20.
- A part whose EV is conserved therefore keeps its place in its set, and a heavy part's
  draw/stamina penalty, which used to come from its ergonomics, now comes from its weight at a
  similar size.

So the weight credit is **0 in every family** (`rules.credit_for`, kept as a knob in
`DEFAULT_VECTORS`), weight values are unchanged, and the strength formula keeps its weight term:

```text
strength = EV(handling, reload_time, stability) − 20·weight − 0.8·h_recoil − 0.6·v_recoil − …
```

## 4. Trade-offs inside competing sets (history; round 7 replaces the lean, section 15)

The point of the split is that builds must choose. Inside each set of items that compete for the
same place:

- Options should differ in **direction**, not just size: the light/short/compact option leans to
  handling, the heavy/long/supported option to stability, the magazine-friendly option to reload.
- No option should be better than another on all of handling, reload, stability, recoil and
  weight unless it is cheaper or the two are visual variants of the same part. No part should be
  best in its set on all three new stats.
- Keep the old EV ordering inside a set unless it is physically wrong.
- CAG principle: cooler, more modern or higher-end options may sit slightly above a plain
  equivalent (about +1 to +2 EV), as the old sheet does.

## 5. Magnitudes (history for handling and stability; section 15)

- Per stat, stay roughly within ±1.5×|old ergonomics| of the part, or ±3 for parts that had 0 and
  gain a deliberate trade-off.
- Large single-part values: stocks up to about ±20, barrels to about ±12 per stat. Everything else
  rarely beyond ±10. Reload: −8% (short magazines) to +16% (large drums), hardware −1.5% to −5%
  (section 13).
- Handling and stability are whole numbers since round 8, with a half point only where it keeps an
  order or a distinction inside a set (section 16); reload_time comes from the section 13 tables.

## 6. Structure of the tree

- **Only-choice parts** (a required slot with one candidate) can keep whatever the default split
  gives; their value effectively belongs to the weapon base. Zero is fine.
- **Grips**: only the first grip counts; extra grips count weight only.
- **Rail panels**: the first four count. Small handling and stability.
- **Iron sights**: the first two count.
- **Muzzle devices**: only the last counts (weight always counts).
- **Assemblies**: a part that hosts other slots (handguards with rails, uppers with barrels) is
  judged on its own stats; its children are re-statted separately.

## 7. Other columns

Recoil, deviation, velocity, damage, loudness, capacity, fire rate and price are left alone. A rule
or override may change one only where the redistribution genuinely needs it, with the reason in
the note; every such change is listed in `review/other_column_changes.csv`. The only ones are the
five cycling parts' `fire_rate` (section 14).

## 8. Weapon base values

```text
handling, stability:  base = anchor + identity offset − median part contribution over the reference builds
reload_time:          1 + base = (1 + identity offset) / median over reference builds of
                                 (today's playback × clamp(1 + part sum, 0.6, 1.6))
```

- Anchor: today's median ergonomics of the weapon's reference builds (official gun-game setups
  and Studio presets, or the stock build when there are none) for handling; 50 for stability. A
  typical build therefore feels as it does today.
- Reload (contract v5): the weapon row is the base factor on the weapon's native animation length,
  `duration = length × (1 + weapon row) × clamp(1 + sum of parts, 0.6, 1.6)`. Today's playback of
  each reference build comes from its old ergonomics on the place's own reload range (stored in
  `data/tree.json`), so the median reference build reloads exactly as long as today (to the 0.1%
  rounding of the base). There are no reload anchors in points any more.
- Identity offsets (`weapon_identity.csv`) are small, deliberate and roughly EV-neutral, each
  with a note. `offset_rt` is a fraction of reload time (bullpups +0.022, which is the −6 reload
  points of before).
- Range conversion (contract v4): ADS (0.8 → 0.25) uses one range on every weapon. Where a
  weapon's place range differed, its handling anchor is converted so the typical build keeps
  today's ADS time exactly (`weapons.convert`). This is not an identity offset. It moves the
  launchers' handling anchors (RPG-7 9.6, PSRL 4.2) and the turret's (23.7).
- `python generate.py --calibrate` recomputes `weapon_bases.csv` from the current part rules.

## 9. Ammunition (round 7: an even split, h = s = 0.935 E; section 15)

Ammunition rows carried small ergonomics values (−4 to +3, more on shotgun specials) that track soft
versus harsh shooting: tracers and subsonics positive with less recoil, hot, +P and AP loads
negative with more recoil. The team's ammo change sheets score them, so each calibre's parity and
the shotgun specials' compensation are built on them.

This pass keeps that value: handling = E, stability = 0.85·E, reload 0, so EV = E. Soft-shooting
loads are easier to bring up and hold steady, harsh loads the opposite. `rules/ammo.py` has
`MODE = "keep"`; setting it to `"zero"` drops ammunition to 0/0/0 in one edit, which is
the physically tidier choice argued in `notes/ammo.md` (with the per-round cost of doing so). The
aim of this pass is the stat split, not an ammunition rebalance, so the team decides that later.

## 10. Split rules per family (history for handling and stability; section 15)

Condensed from `notes/<family>.md`, which give the full tables and reasons. `E` is the old
ergonomics; EV is kept equal to E unless stated. Reload amounts here and in the notes are in reload
points, which `rules.restat` converts to `reload_time` (section 2): +2.5 points is about −0.9% of
reload time, −25 points is +10%. Reload shares given here are not the final reload: section 13 re-stats the
reload of every part, and moves the share of parts with no reload reason into handling and
stability.

- **Magazines**: measured from the set's default magazine (0 on all three; a non-zero default's
  constant moves into the weapon base). Larger than standard: reload 2.125·E, handling 0.25·E;
  past −15 only half the rest counts and reload never goes below −25; drums, quads and caskets never
  reload faster than the slowest stick they compete with. Smaller than standard: reload takes the
  first 6 points, then a third of the rest, capped at +12; handling takes enough of the rest that the
  mag keeps two thirds of its old value (less bulk on the gun). The last third was pure capacity
  compensation and is dropped; +28 reload on a 3-round mag would be absurd. Polymer/ribbed +0.5 reload, straight-wall −0.5;
  translucent equals opaque. Stability 0. Shotgun tubes (R870, MP133): reload 1.5·E, handling 0.5·E
  from the stock cap, since reload points already scale every shell.
- **Mag controls**: releases, paddles, magwells, mag assists, loop plates: reload 2.5·E only.
  Capacity extensions are treated as a longer magazine.
- **Stocks**: a lean from type (precision +1, fixed +0.5, adjustable 0, folding −0.5,
  minimal/PDW −1) plus weight against the set (±0.5 per ±0.1 dw); reload 0.25·E, handling
  (0.83 − 0.25·lean)·E capped at 22, stability the rest. Braces and tailhooks: handling 1.3·E,
  stability −0.1·E (gives up ~15% EV on purpose). No stock: handling 18, stability −6 to −14. Pads:
  stability only. Cheek rests and spacers: stability, −E/3 handling for bulk. Tubes, adapters: zero.
  Whole gun bodies (Mosin, AUG Para, R700 stocks) from a table.
- **Pistol grips**: standard 1.0/0.4/0.5 per E; steep CQB grips 1.25/0.4/0.15; support grips (palm
  swell, beavertail, rubber, heavy) 0.75/0.4/0.85; P226 magwell grip 0.3/1.5/0.3; stockless
  shotgun grips 1.45/0.35/−0.3.
- **Foregrips** (only the first grip counts): handstops and index panels h 1.25·E, s 0.5·E;
  angled h 1.0·E, s 0.85·E; stubby h 0.8·E, s 1.1·E; full verticals h 0.75·E − 1.5, s 1.2·E + 2;
  grip-pod and bipod legs h −5.5/−7.5, s +7; reload 0.
- **Handguards**: stability = 0.6 × the set's median E + 16 per dw above or below the set's median
  weight (weight stands in for length; r = 0.90 in the AR and KF416 sets); handling the rest;
  reload 0. AK top covers: 0 stays 0; sight-height covers h −3.5 / s −2. Rail panels and covers:
  small handling and stability, a bigger panel never worse. Bare rail sections h −0.5 / s −0.5.
- **Barrels**: stability −1 per inch against the weapon's standard barrel (the sheet's zero),
  capped at ±8 and at the barrel's old ergonomics gap; heavy/HBAR/bull +1.5 stability, fluted −0.5;
  handling takes the rest. Velocity, recoil, deviation and damage untouched, so long barrels keep
  winning there.
- **Muzzle devices**: stability takes a share of E and handling the rest: suppressors 0.3 (a −5
  can becomes h −7 / s −1.5), brakes, flash hiders and protectors 0.5, adapters 1.0, barrel
  extensions −1 stability per inch.
- **Optics**: compact sights (E ≥ −2) handling = E; magnified or bulky sights handling 1.5·E,
  stability 0.2·E; mounts and risers handling = E (mostly 0, as in 0.25.4); caps, covers and eye
  cups split like the sight they fit. No height cost on tall mounts (it would turn co-witness
  choices into traps).
- **Iron sights**: handling 1.5 per old point; fixed tall sights that compete with folding ones,
  and carry handles, 1.0.
- **Receivers**: uppers handling and stability; lowers mostly reload (magwell, ambi controls);
  slides mixed; frames grip-like; dust covers handling and stability. A mass rule inside sets moves
  value without changing EV: the lighter part leans handling, the heavier stability.
- **Internals**: selectors and safeties handling; charging handles, bolt catches/releases, Mosin
  bolt and R700 bottom metal reload; triggers stability (a lighter, steadier pull; about 0.77 of
  their old EV); takedown levers +1 stability; springs, rods, hammers, pins zero.
- **Ammunition**: handling E, stability 0.85·E, reload 0 (section 9; one switch to zero).
- **Tactical devices**: handling 1.6·E only.
- **Bayonets**: handling 0.8·A and stability 1.0·A of the whole assembly's value A (front mass
  and length make it sway more); grips and slings 0. (History: since round 7 a bayonet is
  handling only, h = A, the assembly's old net on the blade; round 8 restored that net.)
- **Misc**: each item re-statted by the family it really belongs to.

## 11. Lead decisions on cross-family items (history; the round-6 overrides are gone, section 15)

- `agr_870_protection_cap` (filed as optic) is the stockless AGR-870 configuration: same split as
  the stockless shotgun grips.
- `launchtron_psrl_plastic_foregrip` was dominated in the old sheet and after the split; it is now
  a middle option between handstops and verticals (`overrides/lead.csv`).
- Items filed in the wrong family were re-statted by the rules of the family they really belong
  to, inside the owning family's module; `notes/*.md` list them.

## 12. Steepened lean in the choice slots (switched off in round 7)

Typical builds sit at today's feel, but many weapons have enough positive parts that one build can
sit near the ceiling of all three stats. Effects read handling and stability clamped to 0–100, so
the check that builds must choose is judged against `min(max, 100)` for those two, and for reload
against the fastest parts sum the weapon's legal builds reach (and the −40% clamp), in points at
2.75 per 1% of time (`simulate.py`, "choice margin").

`lean.py` steepens, EV-neutrally, the handling-versus-stability lean of stocks, handguards, pistol
grips and foregrips: inside each item's main competing set, its handling share of value is spread
away from the set's median share by a factor of 2, clamped so the other stat goes at most a quarter
of the value negative, and no stat beyond ±25 (stocks, handguards), ±15 (pistol grips) or ±12
(foregrips) unless the item already was. Reload time, zero-value parts, penalty parts, full gun bodies
and overrides are untouched. Result in the AR stock set: minimal stocks (Viper, MOA SL-K, XM177)
about h 25 / s 0–3, carbine stocks h 13–15 / s 12–15, the PRS Gen3 h 7.5 / s 25.

Barrels and muzzle devices are not steepened: length moves handling and stability the same way and
their trade is recoil and velocity. Factor 2 is where it stops making sense: at 2.5 and 3 the
check gains one weapon each while the number of parts pushed to the share limit grows from 15 to
37. Setting the factors to 1 switches the pass off.

## 13. Reload is re-statted per kind of part (round 5)

`reload_scope.py`, applied in `rules.restat` and to override values. A part either has a real
reason to change the reload or holds 0. A part with a reason gets a value sized by how much it
changes the reload action, the same for every comparable part; values are written as fractions of
the weapon's base reload time. There is no significance threshold: every value comes from the
kind of part.

**Magazines and capacity extensions**, by capacity against the slot's standard magazine
(`c = capacity / standard`; an extension counts as base + added rounds over the base). A longer
magazine is harder to index and seat, a shorter one quicker, and drums, quads and caskets are slow
to seat whatever their length:

| Kind | c | reload_time |
|---|---|---|
| short stick | ≤ 0.4 | −8% |
| reduced stick | < 0.85 | −4% |
| standard (material, colour, curve variants) | < 1.15 | 0 |
| extended stick | < 1.7 | +4% |
| long stick | ≥ 1.7 | +8% |
| drum, quad or casket | < 2.5 | +12% |
| drum, quad or casket | ≥ 2.5 | +16% |

The old material rule (±0.5 point for polymer, ribbed or straight-wall magazines) disappears:
same-capacity magazines drop their old reload difference.

**Magazine controls and reload hardware:**

| Kind | reload_time |
|---|---|
| large competition magwell funnel (Rhino R-23) | −5% |
| flared magwell or funnel, as a part or on the lower (Novacek N4 Gen3), and the R700 Badger bottom metal | −3% |
| enhanced magazine release or catch (extended, ambidextrous, oversized) | −3% |
| magazine pull or seating aid (mag assists, loop and bumper bottom plates) | −3% |
| large add-on release paddle | −2% |
| enhanced bolt catch, bolt release or slide catch (empty reloads) | −2% |
| enhanced charging handle | −(1% + 0.25% per 0.01 dw), to the whole percent, or the half percent where two handles of one set at least 0.5% apart would round alike (round 8): −1.5% (0.02 dw) to −4% (0.11 dw side charger) |
| standard releases, plates, magwells, charging handles and bolts | 0 |

A charging handle's latch size is what changes how fast it is grabbed, and the part's weight
measures it; scaling with weight also keeps a heavier handle from being a strictly worse twin of
a lighter one.

**No reason, so 0:**
- Shotgun tube extensions and caps: each shell loads the same way, and more shells take longer
  by themselves.
- Magazine sleeves, couplers and adapters.
- Lowers other than the flared-magwell Novacek. Their controls are separate parts: the ADAC-15's
  release and bolt catch, the Scalar lowers, the FANG-H AR lower, and the standard AR, HK, UMP
  and AK lowers.
- R700 chassis: the R700 always takes detachable magazines.
- Slides, frames, trunnions, trigger housings and the AK enhanced safety.
- Every part of every other family.

**What happens to the old value:**
- **The value moves** (`MOVE_VALUE`, one switch). A part that holds 0 for lack of a reason, but
  had a reload share as part of its value, gets that value (`0.40·points`) back in handling and
  stability, in the proportions of value it already has there, so its EV stays where it was. This
  covers stocks at 0.25·E, pistol grips at 0.4·E, tube extensions, receivers and standard
  charging handles. A part with no handling or stability value takes its family's default
  proportions. With `MOVE_VALUE = False` these parts simply lose the share.
- **Standard-capacity magazines drop their old difference**, as above.
- **Parts with a reason take the table value, and their EV follows it.** The carried-over values
  were too small to matter (most were under 1%), and this step sizes them on purpose: magwells and
  releases gain about 1–4 EV, and light drums that the old sheet under-charged lose several.
- The lean pass (section 12) runs after this step and keeps EV.

## 14. Cycling parts carry fire rate (round 6)

`cycling.py`, applied in `rules.restat` after the reload step. Bolt and pump cycling follows the
completed fire rate, so on the manually cycled weapons the parts that are the cycling interface
carry `fire_rate` (a fraction of base RPM), and nothing else does. Semi-automatic and automatic
weapons are untouched.

| Weapon (base RPM) | Part | fire_rate | Reason |
|---|---|---|---|
| Remington 870 (128) | SpeedFeed forend (default) | 0 | |
| | Magtap MOE forend | +3% | contoured, ridged forend: a fast, sure stroke |
| | P.R.O Tactical PR870 forend | −2% | railed forend: more mass to cycle; it is the steady option |
| MP-133 (156) | beechwood forend (default) | 0 | |
| | plastic forend | +2% | lighter synthetic forend: a quicker stroke |
| Mosin (50) | Mosin Default bolt (default), infantry bolt and handle | 0 | |
| | Resolute bolt | +1% | smoother aftermarket bolt |
| | Crazy Ivan bolt knob (on the infantry bolt) | +1% | enlarged knob |
| R700 (50) | — | — | bolt face, plug and firing pin are single-choice parts |

- **Ranges.** Pumps: a few percent either way (R870 125–132 RPM, MP-133 156–159). Bolts: at most
  +1% (Mosin 50–50.5 RPM), because a faster bolt raises the shot cadence, which ergonomics never
  did, so it is new power. Receivers, stocks, grips, barrels, optics and the rest get nothing.
  The R870 Tampa Shorty receiver changes the tube, not the pump stroke.
- **Moved from reload.** The Resolute bolt and Crazy Ivan knob carried reload in round 5. Their
  reason is really cycling, so their reload is 0 and their value is redirected (below).
- **Price, in old ergonomics points per 1% of fire rate:**
  - Pumps 1.5. Before the rework one ergonomics point moved a pump by about 0.66% of its RPM
    (the R870 spanned 79–164 RPM over 0–100 ergonomics), so 1% of pump RPM is what 1.5 points
    bought in cycling.
  - Bolts 3.0, twice the pump price. On a bolt rifle the time to the next shot is the weapon's
    main limit, and no part could move it before.
- **Redirected, not added.** The EV a part carries as fire_rate (`PRICE × percent`) is taken out
  of its handling and stability, in the proportions of value it has there; a slower part (the
  PR870) gets it back. The lean pass then runs as usual. The review sheets' EV includes the
  fire-rate value, so the five parts' EV stays at their old ergonomics.
- `ENABLED = False` switches the step off.

## 15. Handling and stability by profile (round 7)

The split follows `SPLIT_PROPOSAL.md` v3, agreed with the team: **even is the default** (a part
that is simply nicer is better at both), **a whole family leans only where every member shares a
strong reason**, and **role parts** get their own profile item by item. Nothing leans by weight
any more: the weight-in-set leans of the family rules and the ×2 lean pass (`lean.py`, now off)
are gone, and so are the round-6 hand overrides that compensated for them.

**Data.** `profiles/<family>.csv` has one row per part: `profile`, `role`, `role_strength`, an
optional `value` (V, when the old ergonomics is a known anomaly), optional explicit `handling` and
`stability`, and the review: the real-world `counterpart`, `confidence`, one line of `why`, and
`flags`. 36 reviewers wrote the rows family by family (`AGENT_BRIEF_R7.md`); rows the lead changed
say "(lead)" in `why`. The review sheets carry these columns, and `review/research_flags.csv`
collects what the review found outside handling and stability.

**Value.** V is the part's old ergonomics, less what it already carries as reload (reload hardware
outside the magazine families) or as cycling fire rate. The profile splits it:

| Profile | Handling | Stability | Used for |
|---|---|---|---|
| `even` | 0.935 V | 0.935 V | the default: pistol grips, handguards, rail panels, receivers, triggers, gas blocks, pump forends, ammunition, adjustable stocks |
| `handling`, `optic_compact`, `mount`, `barrel` | V | 0 | sights, mounts, compact optics (3× and under), controls, barrel length, muzzle devices, lasers, lights, bayonets |
| `optic_scope` | V | 0.2 min(V, 0) | magnified optics above 3× and LPVOs: a small stability tax on magnification, never a bonus (round 8) |
| `stock_precision`, `grip_vertical`, `grip_pod` | 0.5 V | 1.49 V | precision stocks, vertical foregrips, bipod grips |
| `stock_fixed` | 0.75 V | 1.17 V | fixed rifle stocks |
| `stock_compact`, `grip_angled` | 1.15 V | 0.66 V | minimal, PDW, wire stocks and braces; angled grips and handstops |
| `handguard_long` / `handguard_short` | 0.8 V / 1.1 V | 1.11 V / 0.72 V | only the clearly longest and shortest handguard of a set |
| `cheek_riser` | 0.25 V | 1.81 V | cheek risers |
| `buttpad` | 0 | 2.13 V | pads, butt plates, length-of-pull spacers |
| `stockless` | handiest stock on its weapons + 2 | what is left of V, between −12 and −4 | the "no stock" options |
| `magazine` | the magazine rule's handling, never a bonus; 0 at the standard capacity; a drum no handier than the least handy stick (round 8) | 0 | magazines and capacity extensions; shotgun tubes 0.5 per old point |
| `reload_only`, `zero` | 0 | 0 | magwells, releases, assists, bolt catches, enhanced charging handles; containers and cosmetics |

- Every profile keeps EV, except the handling-only ones: they keep **h = V**, today's ADS effect,
  rather than the 1.67 V that EV-neutrality would give, since the reload and draw that their old
  ergonomics also bought were never physical for a sight, a muzzle device or a barrel. Their EV is
  0.6 V; most are penalties, so they cost a little less EV than before, and builds aim as today.
- A penalty (V < 0) on a stability-leaning profile goes to handling (a heavy precision stock or a
  bulky vertical grip is slow to bring up, not unsteady), but since round 8 the part still steadies:
  stability max(2, −V), handling the rest, EV 0.6 V. On a handling-leaning profile it splits evenly.
- Stocks lean by type; a stock gets a role on top only where its type cannot express it (a
  precision stock worth E 1, a stock with a negative value).

**Roles** are an EV-neutral swing on top of the profile: **marksman** handling −H, stability
+1.28 H; **compact** the reverse. **H = 3 on major parts** (stocks, barrels, handguards, receivers,
and since round 8 any part on a barrel, stock or handguard profile filed in another family)
and **1.5 on the rest**, 1.5× for `strong`. At 4/2 a fully kitted marksman G3 sat 26 handling
below today; at 3/1.5 it sits 24 below with stability 90, which is the steer the role is meant to
give. A role part's EV is unchanged by the swing; where its old ergonomics only compensated its
weight (the Mk20 upper), the role now turns that value into stability.

**Stockless** options are the handiest choice on their weapon and clearly unsteady: handling 2
above the handiest stock that weapon can mount, stability from what is left of V, kept between
−12 and −4. This fixes the earlier bug where the lean pass's clamp left them less handy than a
stocked build.

**Open questions recorded with their defaults** (SPLIT_PROPOSAL): large scopes keep the small
stability cost; ammunition splits evenly (`rules/ammo.py`'s zero switch no longer applies, set
ammunition rows to `zero` instead); handguards are even with the mild long/short lean; barrels are
"length costs handling", with heavy, bull and match barrels as marksman parts.

## 16. Whole numbers and the sense check (round 8)

**Whole numbers** (`rounding.py`, the last step of the generator). Every part's handling and
stability are rounded to whole points: of the whole pairs around the part's two values, the one
with the lowest cost wins, where cost is how far the part's value moves (EV) plus 0.5 EV per point
the furthest-moved stat travels. The value stays close without pushing one stat far from its own
number, and nothing is always rounded up or down. An even part gets the same integer for both.

A half point stays only where whole numbers would misstate a competing set. Among like-for-like
parts of a set (the same hosted child slots, as in the domination check; on a rail also the same
family and profile):

- no reversal: a part ahead of another on a stat before rounding is not behind it after;
- no new difference: parts equal on a stat stay equal on it;
- no new tie: parts that differed at half points do not become identical in all three stats.

A part in conflict first tries its other whole pair if that keeps its value within 0.55 EV; else it
keeps the nearest half-point pair that resolves the conflict. `review/half_points.csv` lists every
remaining half value and the part it is kept apart from; the rule column says the same.

- **Weapon base rows** are whole numbers (`weapons.py`); they compete with nothing.
- **Part reload_time** comes from the section 13 tables, which are whole percents except the
  enhanced charging handles: those are rounded to the whole percent, or to the half percent where
  two handles of one set at least 0.5% apart would round alike. Weapon base factors stay at 0.1%.

**Calibration** (`weapon_identity.csv`, `exclude_refs`): a reference build that turns the gun into
another class is left out of the median that sets the weapon base, so the base lands on one kind of
gun: the Remington 870's stockless Tampa shorty, the SCAR-H's Mk20 SSR and the AK-12's two RPK-16
builds. The simulation still reports them.

**Sense check.** 35 reviewers asked of every part and every set whether a balancer who knows the
parts would say the number makes sense. The fixes are in `profiles/<family>.csv`, each with
"Round 8:" and its reason in `why`; the class-wide ones are rules:

- stability-leaning parts with a negative value still steady (section 15);
- `optic_scope` stability never positive;
- standard-capacity magazines have handling 0, like their reload (the old differences were
  material noise); a drum is no handier than the least handy stick it competes with;
- misfiled barrels, stocks and handguards take the major role swing;
- the review note (`rule`) names only what sets the values: the reload kind, the cycling price, the
  profile, the rounding; the earlier family-rule notes are gone;
- the two KOSCH .40 +10 extensions count against the slot's standard 15-round magazine (+4%, not +8%).

Judgment calls were left as they are and are listed in the balancing report.

