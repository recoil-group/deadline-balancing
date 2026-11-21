# Re-statting rules

These are the rules the rebalance was built on. `RULES_MINED.md` records what the old sheet and its
history imply; this file records the decisions taken from it. Stat meanings and the worth of one
point come from the code contract (summarised in `../knowledge/stats.md`).

## 1. What the three stats own

| Stat | Owns | Physical drivers (better →) |
|---|---|---|
| `handling` | ADS in/out time, sight switch, fire-mode switch, mag check and other minor animations | light, short, slim front end; good grip angle; collapsed or short stock; low, small sights; nothing hanging off the front |
| `reload_speed` | reload animations only (tactical, empty, quick, per shell) | magazine design (low capacity, polymer, tapered, no drums), extended/ambi releases, flared magwells, mag pulls and assists, bolt catches and charging handles (empty reloads), receiver features that guide the magazine |
| `stability` | idle sway (hip and aimed), sway while moving, breath-hold cost; **50 = today's feel** | mass at the shoulder and hands, a firm stock and cheek weld, front support (foregrips, handstops, bipods); worse with long barrels and front-heavy ends, no stock, braces, folded stocks |
| weapon weight (not a column) | draw, stow, sprint-out, aimed move speed, aim stamina drain, turn lag (held gun) and travel speed (all carried guns) | already priced by the weight column |

Fire rate also drives bolt and pump cycling now. `fire_rate` on parts of manually cycled weapons is
left as it was; nothing new was added.

## 2. Value accounting

One old ergonomics point bought ADS, reload, draw/stow, sprint-out and aim stamina at once. The
last three now come from weight, so what a part's new stats can carry is the ADS and reload part
of its old value, plus the new stability axis:

```text
EV = 0.60 * handling + 0.40 * reload_speed + 0.47 * stability     (in old ergonomics points)
```

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
strength = EV(handling, reload_speed, stability) − 20·weight − 0.8·h_recoil − 0.6·v_recoil − …
```

## 4. Trade-offs inside competing sets

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

## 5. Magnitudes

- Per stat, stay roughly within ±1.5×|old ergonomics| of the part, or ±3 for parts that had 0 and
  gain a deliberate trade-off.
- Large single-part values: stocks up to about ±20, drums and very large magazines to −25 reload,
  barrels to about ±12 per stat. Everything else rarely beyond ±10.
- Values are in 0.5 steps.

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
the note; every such change is listed in `review/other_column_changes.csv`.

## 8. Weapon base values

```text
base = anchor + identity offset − median part contribution over the weapon's reference builds
```

- Anchor: today's median ergonomics of the weapon's reference builds (official gun-game setups
  and Studio presets, or the stock build when there are none) for handling and reload; 50 for
  stability. A typical build therefore feels as it does today.
- Identity offsets (`weapon_identity.csv`) are small, deliberate and roughly EV-neutral, each
  with a note.
- `python generate.py --calibrate` recomputes `weapon_bases.csv` from the current part rules.

## 9. Ammunition

See `rules/ammo.py`. Ammunition rows carried small ergonomics values (±1–4, tracers positive, hot
loads negative). Ammunition does not plausibly change ADS, reload or sway, so the default is zero
on all three new stats; the weapon base calibration absorbs the average.

## 10. Split rules per family

Condensed from `notes/<family>.md`, which give the full tables and reasons. `E` is the old
ergonomics; EV is kept equal to E unless stated.

- **Magazines**: measured from the set's default magazine (0 on all three; a non-zero default's
  constant moves into the weapon base). Larger than standard: reload 2.125·E, handling 0.25·E;
  past −15 only half the rest counts and reload never goes below −25; drums, quads and caskets never
  reload faster than the slowest stick they compete with. Smaller than standard: reload takes the
  first 6 points, then a third of the rest, capped at +12; handling 0.25·E capped at +2.5 (short mags
  lose about half their old value on purpose: their old bonus was capacity compensation, and +28
  reload on a 3-round mag would be absurd). Polymer/ribbed +0.5 reload, straight-wall −0.5;
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
- **Ammunition**: zero on all three (section 9). The cost to each round is in `notes/ammo.md`;
  subsonics (−3 old points) lose the most, shotgun slugs, birdshot and bean bags the most in
  absolute terms.
- **Tactical devices**: handling 1.6·E only.
- **Bayonets**: handling 0.8·A and stability 1.0·A of the whole assembly's value A (front mass
  and length make it sway more); grips and slings 0.
- **Misc**: each item re-statted by the family it really belongs to.

## 11. Lead decisions on cross-family items

- `agr_870_protection_cap` (filed as optic) is the stockless AGR-870 configuration: same split as
  the stockless shotgun grips.
- `launchtron_psrl_plastic_foregrip` was dominated in the old sheet and after the split; it is now
  a middle option between handstops and verticals (`overrides/lead.csv`).
- Items filed in the wrong family were re-statted by the rules of the family they really belong
  to, inside the owning family's module; `notes/*.md` list them.
