# Stat rework: tentative full rebalance

This folder turns the old `ergonomics` column into `handling`, `reload_time` and `stability`
for every weapon and attachment, following the stat rework contract
(`../../deadline/.claude-scratch-stat-rework/CONTRACT.md` on the author's machine; the stat meanings
are summarised in `../knowledge/stats.md`). The result is `../balancing.csv`.

It is a **first pass for the team to tune**, produced overnight by a balancing lead and eight
category agents, validated only by build simulation. Nothing here has been playtested.

## How to read the result

| File | What it is |
|---|---|
| `../balancing.csv` | The full sheet in the new column layout. Every non-split column is byte-identical to the old sheet unless listed in `review/other_column_changes.csv`. |
| `review/<family>.csv` | One sheet per family. Each item's old ergonomics next to its new three stats, grouped by competing set, with its EV, the team's strength score before and after, the rule that produced it, and its profile, role, real-world counterpart, confidence and one line of why. Start here. |
| `profiles/<family>.csv` | Round 7's source of truth for handling and stability: each part's profile, role and research (RULES.md section 15). Edit a row here to change how a part splits. |
| `review/research_flags.csv` | What the round-7 review found outside handling and stability: other-column values that look wrong, reload and cycling questions, misfiled parts. For the team; nothing in it was applied unless the notes say so. |
| `review/half_points.csv` | Every half point left after the round-8 whole-number rounding, with the part it is kept apart from (RULES.md section 16). |
| `review/spread.csv` | Per competing set, how far handling and stability spread against how far ergonomics did (`spread.py`). |
| `review/weapon.csv` | Weapon base rows. |
| `review/simulation_report.md` | Stock, reference (official setups and presets) and optimised builds for every weapon, plus the validation checks. |
| `review/other_column_changes.csv` | Every change outside the three new columns, with the reason (the five cycling parts' `fire_rate`, round 6). |
| `RULES.md` | The rules the rebalance follows: what each stat owns, value accounting, weight, trade-offs, magnitudes, weapon base values, ammunition. |
| `notes/<family>.md` | Each family's split rules, in a few lines per sub-category, and its open questions; the round-7 section at the end is how the family splits now. |
| `AGENT_BRIEF_R7.md` | The brief the round-7 reviewers classified every part from. |
| `RULES_MINED.md` | What the old sheet and its history imply (the "unwritten rules"). |
| `data/tree.json` | The attachment tree: classes, items, mount maps, weapons with default builds and presets, official setups. |
| `data/competing_sets.json` | Every slot group: which items compete for the same place, whether the slot is required and whether it is the only choice. |
| `data/items_index.csv` | One row per sheet item with its family, Studio category, flags, reachable weapons, competing sets and old stats. |

### Reading a value

- **EV** (`0.60·h + 0.40·r + 0.47·s`) is a part's value in old ergonomics points, with `r` the
  reload points its `reload_time` is worth (1% less time ≈ 2.75 points); it should sit near the old
  ergonomics. A big gap always has a note.
- **reload_time** is a fraction of the weapon's base reload time; lower is better. `-0.03` is 3%
  less time, which the review sheets also show as `reload_pct`. Part values are the earlier reload
  points converted (`RULES.md` section 2), so the default magazine of every set is 0. Reload is
  re-statted per kind of part (`reload_scope.py`, `RULES.md` section 13): magazines by capacity,
  magazine controls and reload hardware by kind; every other part holds 0, and the reload share it
  had was moved into its handling and stability.
- **Handling and stability** come from the part's profile (round 7): even by default, a family
  lean only where every member shares a reason (stocks by type, foregrips by shape, optics and
  other front-end parts handling only), and marksman or compact roles on the parts built for one
  kind of gun. Nothing leans by weight.
- Inside a competing set, look at the **direction** of each option (handling vs stability vs
  reload), not just the size.
- Weapon rows hold the platform: a typical build of each weapon lands at its old ergonomics for
  handling and at 50 stability (today's feel), before identity offsets. The ADS range is universal,
  so the launchers and turret carry converted handling anchors that keep today's ADS time. The
  weapon row's `reload_time` is the base factor on the native reload animation, calibrated so the
  typical build reloads exactly as long as today; `weapon_bases.csv` shows the working.

## How to regenerate

Python 3, standard library only. From the repository root:

```bash
python3 stat-rework/generate.py --write          # balancing.csv + review/
python3 stat-rework/simulate.py                  # review/simulation_report.md
python3 stat-rework/generate.py --preview stock  # print one family, write nothing
python3 stat-rework/check_family.py stock        # drift, dominations, spreads for one family
python3 stat-rework/simulate.py --weapon M4A1    # builds for one weapon, printed
python3 stat-rework/generate.py --calibrate      # recompute weapon_bases.csv (then --write again)
python3 stat-rework/spread.py                    # handling spread vs ergonomics spread per family
```

Pipeline:

1. `data/source_balancing.csv` (main at `ec0e059`) is the input and is never edited.
2. `rules/__init__.py` holds the pricing and the default split vector of each family.
3. `rules/<family>.py` refines the split per item from what the part physically is.
   `reload_scope.py` then sets every part's reload from its kind (magazines by capacity, controls
   and hardware by type) and gives other parts' old reload share back in handling and stability
   (one switch).
   `cycling.py` gives the cycling parts of bolt and pump guns `fire_rate`, paid for out of their
   handling and stability (one switch).
4. `profiles.py` then sets every part's handling and stability from its row in
   `profiles/<family>.csv` (profile, role, optional value or explicit values), and gives the
   stockless options their values once every stock is known. This replaces the family rules'
   handling and stability (the magazine rule still supplies a magazine's handling).
5. `lean.py` (the ×2 lean pass of earlier rounds) is switched off. `overrides/lead.csv` is empty;
   the round-6 overrides only compensated the weight leans and were removed.
6. `rounding.py` rounds every part's handling and stability to whole numbers, keeping a half point
   only where it keeps an order or a distinction inside a set (round 8).
7. `weapon_identity.csv` holds each weapon's anchor, identity offsets and the reference builds left
   out of calibration (`exclude_refs`); `--calibrate` turns them
   into `weapon_bases.csv`, which is what the weapon rows get.

To retune handling and stability: change a part's row in `profiles/` (or a profile's coefficients,
the role swing or the stockless margin in `profiles.py`), run `--write`, and check `simulate.py`
and `spread.py`. If parts change a lot, run `--calibrate` and `--write` again so weapon bases follow.

### Studio data

`data/raw/` (gitignored) holds full JSON dumps of `ServerStorage.attachment_data`, the weapons'
`defaults`, `presets` and `properties` stat markers, and `ServerStorage.resources.gun_game_setups`,
taken read-only from the Staging place on 2026-11-21. They are kept out of this public repository;
`data/tree.json` is the reduced version; the tools use it automatically when `data/raw/` is absent, with the same results. To refresh the dumps,
run `data/dump_studio.luau` in Edit mode (it only reads) and save its three strings as described
at the top of that file, then run `python3 stat-rework/tree.py` to rewrite `data/tree.json`.

### Old change sheets

`port.py` matches columns by name, so an old change sheet that still has `ergonomics` will port
everything except that column (it warns "Ignored columns: ergonomics"). Rewrite such sheets with the
three new columns. `diff.py` and `changelog.py` print `Ergonomics x -> Handling a / Reload Time b /
Stability c` when comparing an old sheet with a new one, and colour `reload_time` changes
lower-is-better.

## What to tune first

See the end of `review/simulation_report.md` and the balancing report for the current list. In
short: (1) the profile coefficients and the role list and strength (`profiles.py`, `profiles/`),
which now carry the "builds must choose" effect; (2) weapons whose parts can still reach the ceiling of all
three stats; (3) the reload tables in `reload_scope.py`; (4) ammunition (kept, one switch to zero);
(5) the EV weights themselves (`rules.W_H/W_R/W_S`) once the team has a feel for a stability point.
