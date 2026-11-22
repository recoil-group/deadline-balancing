<!-- Round 7: the brief the 36 reviewers worked from, kept as written apart from two notes. -->

# Round 7 brief: classify every item for the new handling/stability split

You are one of about 36 reviewers. Each of you gets one chunk of the attachment balancing sheet
and decides, item by item, what each part really is and which profile it gets. A lead merges all
returns and computes the values; you do not compute or edit any values yourself.

## The game, in three lines

A tactical FPS. The old sheet had one stat, `ergonomics` (E), that bought ADS speed, reload, draw
and stamina at once. It is now split into **handling** (how fast and easy the gun is to bring up
and operate: ADS time, minor animations), **stability** (how still it sits once aimed: idle and
moving sway, breath-hold cost), and **reload_time** (only magazines, magazine controls and reload
hardware; already decided, leave it). Weight is untouched and already pays for draw, sprint-out,
aimed movement and arm fatigue; **nothing leans by weight**. On bolt and pump guns a few cycling
parts carry `fire_rate` (already decided).

## Read first

`SPLIT_PROPOSAL.md` (v3), the team's agreed split philosophy. In short:

1. **Even split is the default.** A part that is simply nicer is better at both stats.
2. **A whole family leans only where every member shares a strong reason** (the proposal's table).
3. **Role parts** get their own profile, item by item: a part built for a kind of gun is good for
   that kind of gun and pays for it in the other stat. Roles are the exception, not the rule:
   expect a handful per family, not a quarter of it.

## Your input

A CSV chunk (path in your task). One row per item: name, pretty name, family, Studio category and
class, weight (dw; 1 dw = 1.18 kg), old ergonomics, the competing set it sits in (items in the same
set compete for one slot), the set's default, the weapons it reaches, child slots it hosts, the
current round-6 values (for context only; they come from the method being replaced, which leaned by
weight and doubled the lean), and other columns (recoil, deviation, velocity, loudness, capacity,
price) for context.

## Profiles (pick exactly one per item)

`V` is the part's value in old ergonomics points (normally its old E). The lead computes:

| profile | meaning | handling, stability |
|---|---|---|
| `even` | default: nicer is better at both | h = s = 0.93 V |
| `handling` | the part's only effect is getting on target / operating (sights, mounts, compact optics, controls, barrel length, muzzle devices, lasers, lights, bayonets, stowed bipod legs) | h = V, s = 0 |
| `optic_compact` | red dots, holos, prisms, small fixed low power | h = V, s = 0 |
| `optic_scope` | large magnified scopes and LPVOs: mostly handling, small stability cost | h = V, s = 0.2 V |
| `mount` | optic mounts, rings, risers, adapters | h = V, s = 0 |
| `barrel` | barrels: length costs handling, stability neutral | h = V, s = 0 |
| `stock_precision` | precision / sniper / marksman stocks, adjustable-cheek fixed precision stocks | h = 0.5 V, s = 1.5 V |
| `stock_fixed` | fixed rifle stocks (A2-style, wood fixed, solid fixed) | h = 0.75 V, s = 1.17 V |
| `stock_adjustable` | ordinary collapsible / adjustable carbine stocks | h = s = 0.93 V |
| `stock_compact` | minimal, PDW, wire, folding-minimal, skeleton, braces | h = 1.15 V, s = 0.66 V |
| `stockless` | the "no stock" option: end plates, caps, QD swivels where a stock would go | the lead sets: handier than any stock on that gun, clearly unsteady |
| `buttpad` | recoil pads, butt plates, LOP spacers | s only (about 2.1 V) |
| `cheek_riser` | cheek risers / combs | h = 0.25 V, s = 1.8 V |
| `grip_vertical` | vertical foregrips, stubby verticals | h = 0.5 V, s = 1.5 V |
| `grip_angled` | angled foregrips, handstops, finger stops | h = 1.15 V, s = 0.66 V |
| `grip_pod` | bipod-foregrips, grip pods (deployable legs in a grip) | h = 0.5 V, s = 1.5 V |
| `handguard_long` | only the clearly longest handguard(s) of a set | h = 0.8 V, s = 1.1 V |
| `handguard_short` | only the clearly shortest handguard(s) of a set | h = 1.1 V, s = 0.72 V |
| `reload_only` | magwells, releases, mag assists, bolt catches, enhanced charging handles: their value is their reload | h = s = 0 |
| `magazine` | magazines, capacity extensions (rule already set: reload; large ones cost a little handling) | unchanged |
| `zero` | containers whose value sits on child parts, pure cosmetics, parts with no effect | h = s = 0 |

Family defaults (use them unless you have a reason): stocks by type; foregrips by shape; buttpads
`buttpad`; cheek risers `cheek_riser`; optics `optic_compact` / `optic_scope`; iron sights and
mounts `handling` / `mount`; selectors, safeties, standard charging handles, bolt handles
`handling`; barrels `barrel`; muzzle devices, bayonets, lasers, lights `handling`; pistol grips,
handguards, rail panels, receivers (uppers, lowers, slides, frames), triggers, trigger guards, gas
blocks, carriers, pump forends, ammunition `even`; magazines and magazine controls `magazine` /
`reload_only` as they are now. A misfiled item (an item in the wrong family) takes the profile of
what it really is; say so in flags.

## Roles (optional, on top of the profile)

- `marksman`: clearly more stability, a handling cost. Built for a rifle you set up and shoot from
  (precision chassis parts, heavy/bull/HBAR/match barrels, marksman uppers, very slim fully vertical
  chassis grips, thumbhole backstraps, match/precision triggers if they really are).
- `compact`: clearly more handling, a stability cost. Built for CQB/short guns (CQB uppers,
  PDW stocks, chopped/skeletonized grips, ultralight pencil barrels...).
- You may propose another role if a group of parts clearly deserves one; name it and describe it
  in `why`; the lead decides.

The lead applies a fixed, EV-neutral swing: handling −H and stability +1.28 H (marksman), or the
reverse (compact). H = 4 on major parts (stocks, barrels, handguards, upper receivers, chassis) and
2 on minor parts (the lead later set 3 and 1.5, RULES.md section 15); `role_strength` = `strong` asks for 1.5× and needs a reason. Do not give a role
just because a part is good; give it when the part is clearly designed for one kind of gun and
would be a poor choice on the other. Stock types already carry the stock trade; give a stock a role
only if it goes clearly beyond its type.

## Research

Most parts are renamed real products (brand names are altered: "Magtap" for a well-known polymer
accessory maker, "Hart" for a classic rifle maker, "Kalis" for a vector-style SMG maker, and so on).
For each item work out the real counterpart from the name, category, weight and what it mounts to,
and look it up when you are not sure what it is designed for. Load the search tool first with
ToolSearch (query `select:WebSearch`). **Search for the real product only. Never put the game's
name, the project, the team, the people or this task into a query.** Group searches: one search
often covers a product line. You need not search obvious items (a standard A2 stock, a generic
red dot). Where the counterpart cannot be identified, write `unidentified` and use the family
default.

## Output

Write a CSV to the output path in your task with exactly these columns, one row per input item, in
input order:

`name,profile,role,role_strength,counterpart,confidence,why,flags`

- `profile`: one of the table above.
- `role`: `marksman`, `compact`, another proposed role name, or empty.
- `role_strength`: empty or `strong`.
- `counterpart`: the real product, e.g. `Magpul PRS Gen3`, or `unidentified`, or `generic` for
  generic parts (a plain end plate).
- `confidence`: `high`, `medium`, `low` or `none`.
- `why`: one line, at most about 20 words: what the part is for and why this profile/role.
- `flags`: empty, or `;`-separated notes for the lead, each starting with one of:
  `reload:` (a part with a real reload reason that has none, or one that has reload and should not),
  `cycling:` (same for fire_rate on bolt/pump guns), `other:` (research suggests weight, recoil,
  deviation, velocity, damage, loudness or price is clearly wrong; say which and why),
  `misfiled:` (wrong family; give the real one), `special:` (anything else the lead must know, e.g.
  a part that only makes sense together with another, a stockless option, an only-choice part).

Quote fields with commas. Do not edit any file other than your output CSV. Do not touch git, the
game repository or Roblox Studio. When done, reply in at most 150 words: counts per profile, the
role parts, how many items you could not identify, and the most important flags.
