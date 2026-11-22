# Deadline stat reference

This document explains the stats relevant to balancing. See [balancing.md](balancing.md) for the general balancing goals.

## General stats: `balancing.csv`

`balancing.csv` contains the base stats for weapons and the general stats for attachments. A completed build starts with the weapon row and adds the stats of its attached parts.

Weight, handling, stability, recoil, capacity, deviation, and velocity are additive. Damage, fire rate and reload time are fractional modifiers. For example, `0.1` damage adds 10 percent of the weapon's base damage. Muzzle loudness is an additive adjustment to a multiplier that starts at `1`.

An empty attachment stat contributes no change. In a change sheet, however, an empty cell can overwrite an existing value when ported.

Some attachment types also have behavior defined outside `balancing.csv`, including ammunition, optics, lasers, flashlights, and property patches.

### Stacking exceptions

- Only the final muzzle device contributes stats other than weight.
- Extra grips after the effective grip contribute weight only.
- Up to four rail panels contribute stats; additional panels contribute weight only.
- Up to two iron sights contribute stats; additional sights contribute weight only.

### Summary

| Stat | Better direction | Unit or meaning |
| --- | --- | --- |
| `weight` | lower | Deadline weight units |
| `handling` | higher | ADS and minor-animation scale, 0 to 100 |
| `reload_time` | lower | fraction of the weapon's base reload time; on the weapon row, the base factor |
| `stability` | higher | sway scale, 0 to 100, 50 is the old feel |
| `horizontal_recoil` | lower | recoil scale, normally 0 to 100 |
| `vertical_recoil` | lower | recoil scale, normally 0 to 100 |
| `magazine_capacity` | situational | rounds |
| `barrel_deviation` | lower | normal projectile dispersion |
| `buck_barrel_deviation` | lower | buckshot dispersion |
| `bullet_damage` | higher | modifier to ammunition damage |
| `bullet_velocity` | higher | studs per second |
| `fire_rate` | situational | modifier to base RPM |
| `muzzle_loudness` | lower | gunshot loudness multiplier |
| `price` | lower | credits |

### Weight

`weight` is measured in arbitrary Deadline weight units (`dw`). Total loadout weight affects movement speed and movement stamina. The weight of the **held** weapon also sets its mobility, which owns its draw and stow speed, sprint-out time, aimed movement speed, aim-stamina drain and turn lag. Weight does not affect recoil.

Use loaded real-world weight as the starting point. Magazine weight should include ammunition. The normal conversion is:

```text
0.024 dw = 1 oz
1 dw = 41.67 oz = 2.60 lb = 1.18 kg
```

Weight can deviate from this conversion for gameplay. Common exceptions include SMGs, suppressors, heavy optics, high-capacity magazines, tactical devices, and very small parts that need a meaningful tradeoff. When reliable weight data is unavailable, use the closest comparable item.

Held-weapon mobility, from the stat rework contract (tentative numbers):

```text
mobility = map_clamped(held weapon weight, 0.5 dw -> 100, 7.0 dw -> 0)   (about 15 points per dw)
```

| Outcome | mobility 0 -> 100 |
| --- | --- |
| Draw animation speed | the weapon's animation-speed range (typically 0.9x -> 1.3x) |
| Stow animation speed | the same, then x5 |
| Sprint-out / sprint-in | the weapon's range (typically 0.9 -> 0.6) |
| Aimed movement speed | today's aimed speed x 0.85 -> 1.15 |
| Arm stamina drain while aiming | 2/s x 1.5 -> 0.5 |
| Turn lag, hip / aimed | x 1.20 -> 0.85 / x 1.10 -> 0.925 |

One dw on the held weapon costs about 15 mobility: roughly 6% draw and stow speed, 4.6% aimed movement speed and 15% more aiming stamina drain, on top of about 3.3% travel speed. A part that was once given negative ergonomics only because it was heavy is now charged by its weight directly.

Total weight is `0.7 body + 5.0 placeholder kit + every carried firearm`, and travel speed is `base / (W / 20 + 1)`.

### Handling, reload time, and stability

These three replaced `ergonomics`, which bundled ADS, reload, draw, sprint-out, arm stamina and minor animations into one number. Handling and stability are summed over the weapon row and its parts and read clamped to 0 to 100. Reload time is a time modifier (below). The same stacking exceptions apply as for every non-weight stat.

ADS time uses **one range for every weapon**, so a handling point is worth the same on every gun. The launchers, whose old ADS range was slower, and the turret carry a converted base handling so their typical build aims as before. Sight switch speed and the minor animations still use each weapon's own range.

| Stat | Owns | One point is worth |
| --- | --- | --- |
| `handling` | ADS in and out (0.73 s at 0 to 0.22 s at 100, linear, every weapon), sight switch speed, fire-mode switch, magazine check and other minor animations | about 5 ms of ADS time |
| `reload_time` | all reload animations (tactical, empty, quick, per shell) and the server reload timers | see below; `-0.01` is 1% less reload time |
| `stability` | idle (breathing) sway at hip and aimed, sway while moving (walk bob and strafe sway), and the breath-hold cost; `1.4x` sway at 0, `1.0x` at 50, `0.6x` at 100 | 0.8% sway and 1% breath-hold cost |

#### Reload time

```text
reload duration = animation length x (1 + weapon row reload_time) x clamp(1 + sum of part reload_time, 0.6, 1.6)
```

- A **part's** `reload_time` is a fraction of the weapon's base reload time: `-0.05` is 5% less time, `0.10` is 10% more. Part values are summed (same stacking exceptions) and applied once, so a part has the same effect on every gun it fits. The sum is clamped to -40% .. +60%.
- The **weapon row's** `reload_time` is the weapon's base factor on its native animation length, calibrated so the weapon's typical build reloads as long as it did before the rework. It is not a modifier players see; it defines the weapon's base reload time.
- Only parts that change the reload action carry it, sized by kind:
  - Magazines and extensions by capacity against the slot's standard magazine: short −8%, reduced −4%, standard 0, extended +4%, long +8%, drums and quads +12% or +16%.
  - Magwells −3% (large funnels −5%), enhanced releases and pull aids −3%, bolt and slide catches −2%, enhanced charging handles −1.5% to −3.7% by size, Mosin bolt work −2%.
  - Stocks, grips, handguards, barrels, muzzles, optics, shotgun tube extensions and the rest hold `0`.
- The default magazine of each slot is `0`. Values are written to 0.001 (0.1% of time).
- Draw speed (mobility) and the minor animations (handling) are not affected.

Breath-hold drains the arm-stamina bar (60 for everyone) at `4.5/s` at 0 stability, `3.0/s` at 50 and `1.5/s` at 100, multiplied by `1 + 0.2 x seconds held`. Holding breath removes sway entirely and is impossible at an empty bar. Aiming drains the same bar at a rate set by mobility.

Stability replaced the game's hidden barrel-length scaling of moving sway: long barrels carry worse stability in the sheet instead.

For balancing, the rework prices the three against one old ergonomics point (see `stat-rework/RULES.md`):

```text
EV = 0.60 * handling + 0.40 * reload_points + 0.47 * stability     (in old ergonomics points)
reload_points = (1.1 / (1 + reload_time) - 1.1) / 0.004              (1% of reload time ~ 2.75 points)
```

A sheet that still has an `ergonomics` column and none of the three loads with handling and stability equal to its ergonomics and reloads exactly as it does today.

The stats panel shows the weapon's reload time in seconds for the standard (magazine not empty) reload, with no bar, and a part's reload time as a percentage ("Reload time -5%"), coloured lower-is-better. Multiplying the two gives the right answer.

### Recoil

`horizontal_recoil` and `vertical_recoil` control recoil direction. Lower is better.

```text
average_recoil = (horizontal_recoil + vertical_recoil) / 2
```

The ratio between horizontal and vertical recoil affects shot direction. More horizontal recoil relative to vertical recoil produces more sideways and diagonal movement. Horizontal recoil is usually more valuable to reduce because sideways movement is harder to compensate for.

Average recoil maps into weapon-specific traits that control camera movement, sway, roll, knockback, animation strength, direction continuity, and progressive recoil. Equal displayed stats can therefore feel different across weapons.

### Magazine capacity

`magazine_capacity` is the number of rounds held before reloading.

Some internal-magazine builds calculate capacity from magazine space and shell size instead of using the visible attachment value directly.

### Damage modifier

`bullet_damage` modifies the selected ammunition's damage curve:

```text
damage = ammunition damage at distance and body part * summed bullet_damage
```

The completed multiplier starts with the weapon value and adds attachment modifiers. Adding `0.10` therefore adds 10 percent of the ammunition curve's value at every distance and body part.

### Barrel deviation

`barrel_deviation` controls normal projectile dispersion. `buck_barrel_deviation` replaces it when the ammunition has `use_buck_deviation` enabled. Lower is more accurate.

The ammunition's `spread_multiplier` scales the maximum dispersion. Its `spread_factor` controls how shots are distributed inside that area.

### Velocity

`bullet_velocity` is projectile speed in studs per second. Higher velocity reduces travel time and projectile drop.

The selected ammunition determines how the completed weapon stat is used. Ammunition properties such as penetration can also derive their value from completed velocity.

Use real-world velocity as a reference, then evaluate it against the game's engagement distances.

### Fire rate

`fire_rate` is a fractional modifier to the weapon's base rounds per minute:

```text
completed RPM = base RPM * (1 + fire_rate)
```

For example, `0.05` increases RPM by 5 percent and `-0.05` reduces it by 5 percent. Property patches can replace RPM or fire modes instead of modifying them.

Completed RPM also sets bolt and pump cycling speed on manually cycled weapons, so a `fire_rate` value on a part of a bolt-action rifle or pump shotgun speeds up or slows down its cycling. Pump shotguns use code-supplied base RPMs chosen to match their old cycle speed.

### Muzzle loudness

`muzzle_loudness` is an additive adjustment to the gunshot loudness multiplier. The completed value starts at `1` and is clamped from `0.1` to `2`.

For example, a muzzle device with `-0.70` normally produces a completed multiplier of `0.30`. Sound assets and special muzzle behavior can make equal values sound different.

### Price

`price` is the attachment's cost in credits. Price affects accessibility but does not offset an item's combat strength.

Price is not a primary balancing knob and does not justify a large strength gap. More expensive attachments can trend slightly better to support progression, but a class should not spread widely on price alone.

## Ammunition stats: `calibers.csv`

`calibers.csv` defines ammunition behavior. The selected ammunition supplies the damage curve, spread behavior, velocity loss, penetration, suppression, and other projectile properties.

### Damage curves

The `damage_*` fields define damage by body part and distance. The completed weapon's `bullet_damage` multiplier is applied after evaluating this curve.

Players have 100 health. All body parts can be penetrated, so one projectile can cause multiple damage events. Evaluate the full curve when comparing different weapons or ammunition.

### Spread

`spread_multiplier` scales maximum projectile dispersion. `spread_factor` controls how shots are distributed inside that area. `use_buck_deviation` selects `buck_barrel_deviation` instead of normal `barrel_deviation`.

The editor displays both average and maximum deviation.

### Velocity loss

`velocity_drop` controls continuous velocity loss during flight. `velocity_loss_limb_pen`, `velocity_loss_ricochet`, and `velocity_loss_wallbang` are the fractions of velocity lost after each corresponding event.

### Penetration

`bullet_penetration_ability` controls how much material a projectile can penetrate. Material and impact conditions also affect the result.

Many ammunition entries derive penetration ability from the completed weapon's `bullet_velocity`, so velocity modifiers can change penetration indirectly.

### Suppression

`suppression` scales the effect applied when a projectile passes near another player. The effect becomes stronger as the projectile passes closer.

`suppression_type` selects the associated bullet-pass sound. Progression and game-level multipliers can modify the final suppression intensity.
