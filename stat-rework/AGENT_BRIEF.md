# Brief for category re-statters

You are re-statting one or more item families of Deadline's balancing sheet for a stat rework, as
part of a team led by the balancing lead. The lead sets the rules and reviews consistency across
families; you own the values in your families.

## Read first

1. `/Users/yifan/Documents/deadline-dev/deadline/.claude-scratch-stat-rework/PLAN.md` (sections 1, 2, 6, 7) and `CONTRACT.md` (all) — the design and what one point of each new stat is worth.
2. In the worktree `/Users/yifan/Documents/deadline-dev/deadline-balancing-stat-rework`:
   `knowledge/balancing.md`, `knowledge/stats.md` (old meanings), then `stat-rework/RULES.md`
   (**the lead's rules — follow them**) and `stat-rework/RULES_MINED.md` (what the old sheet and its
   history imply; use it to keep the unwritten rules going). `RULES_MINED.md` is being written by
   another agent while you start; if it does not exist yet, begin with the data and read it as soon
   as it appears, and in any case before you finish.

## The data you work from

- `stat-rework/data/items_index.csv`: one row per sheet item: `family`, Studio `category`, flags,
  `children_classes` (slots it hosts), the weapons that can reach it, its competing-set ids, and its
  old stats. Families are heuristic: if an item in your family is clearly something else, re-stat it
  by its real physics anyway and mention it in your notes.
- `stat-rework/data/competing_sets.json`: slot groups — which items compete for the same place, the
  host items (`parents`), whether the slot is `required` (has a default) and `only_choice`.
- `stat-rework/data/tree.json`: the reduced attachment tree (classes, items, their mount maps,
  weapons with their default builds, official setups).
- `stat-rework/review/<family>.csv`: the first pass for your family, grouped by competing set.

## What you write (only these files)

- `stat-rework/rules/<family>.py` for each of your families, exposing

  ```python
  def restat(item, ctx, base):
      """Return a dict with handling, reload_speed, stability and _rule (a short reason),
      or None to keep `base` (the default family split already computed for this item)."""
  ```

  `item` fields: `name`, `pretty`, `family`, `category` (Studio display category), `sheet_class`,
  `attach_type` (list), `studio` (the Studio record: `class`, `map`, `mountable_types`, flags),
  `weapons`, `groups`, and old stats as floats: `ergonomics`, `weight`, `horizontal_recoil`,
  `vertical_recoil`, `magazine_capacity`, `barrel_deviation`, `bullet_damage`, `bullet_velocity`,
  `fire_rate`, `muzzle_loudness`, `price`. `ctx.competitors(item)` gives the items sharing a
  competing set; `ctx.group_items(gid)`, `ctx.groups[gid]`, `ctx.items[name]`, `ctx.tree.att[name]`
  are also available. Use `rules.ev(h, r, s)` (and, if you need it, `rules.adjusted_ergo(item, rules.credit_for(item), ctx)`) from
  `stat-rework/rules/__init__.py`. Standard library only. Rules should be readable by a balancer:
  small tables and named functions, a docstring at the top stating the family's rules in plain
  words.
  A rule may also return other columns (e.g. `"vertical_recoil": "-3"`) only if the redistribution
  genuinely needs it, with the reason in `_rule`.
- `stat-rework/overrides/<family>.csv` with header `name,handling,reload_speed,stability,note`
  (you may add other sheet columns if truly needed). Use it for hand-tuned exceptions the rule does
  not cover; **every row needs a short note**. Empty cell = no override.
- `stat-rework/notes/<family>.md`: the split rules you applied, a few lines per sub-category, the
  magnitudes, anything you could not decide, and items that look misfiled.

Do not edit any other file. Do not run `generate.py --write` or `--calibrate`, do not commit, do not
touch the game repo or Studio. Other agents are editing other families at the same time.

## Tools (read-only, from the worktree root)

```bash
python3 stat-rework/generate.py --preview <family>         # your family, grouped by competing set
python3 stat-rework/check_family.py <family> [<family>...]  # EV drift, dominations, best-in-all-three, spreads
python3 stat-rework/simulate.py --weapon M4A1 AK_545       # builds for some weapons (prints only)
```

Weapon base values are calibrated by the lead after all families are done, so absolute build totals
in `simulate.py` will drift while you work; judge your changes by their differences between builds
and between competing options.

## What good looks like

- Every item in your families has a value that follows a physical rule you can state in one line.
- Inside each competing set, options differ in direction (trade-offs), nothing is strictly better
  than a not-more-expensive alternative unless they are visual variants, and nothing is best on all
  three new stats. Use `check_family.py` until dominations in your sets are rare and each one left is
  explained in your notes.
- EV of each item stays near its old ergonomics unless a note explains why.
- The old sheet's unwritten rules (CAG tilt, price trend, typical magnitudes) still hold.

Finish with a final message of at most 25 lines: the rules per sub-category, the number of
overrides, remaining dominations and why, open questions you decided yourself, and misfiled items.
Do not ask questions; make the reasonable call and record it in your notes.
