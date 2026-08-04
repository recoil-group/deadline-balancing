# Deadline stat reference

This document explains the stats relevant to balancing. See [balancing.md](balancing.md) for the general balancing goals.

## General stats: `balancing.csv`

`balancing.csv` contains the base stats for weapons and the general stats for attachments. A completed build starts with the weapon row and adds the stats of its attached parts.

Weight, ergonomics, recoil, capacity, deviation, and velocity are additive. Damage and fire rate are fractional modifiers. For example, `0.1` damage adds 10 percent of the weapon's base damage. Muzzle loudness is an additive adjustment to a multiplier that starts at `1`.

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
| `ergonomics` | higher | handling scale, normally 0 to 100 |
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

`weight` is measured in arbitrary Deadline weight units (`dw`). Total loadout weight affects movement speed and movement stamina. Weapon weight does not directly affect handling or recoil.

Use loaded real-world weight as the starting point. Magazine weight should include ammunition. The normal conversion is:

```text
0.024 dw = 1 oz
1 dw = 41.67 oz = 2.60 lb = 1.18 kg
```

Weight can deviate from this conversion for gameplay. Common exceptions include SMGs, suppressors, heavy optics, high-capacity magazines, tactical devices, and very small parts that need a meaningful tradeoff. When reliable weight data is unavailable, use the closest comparable item.

### Ergonomics

`ergonomics` controls weapon handling. Higher ergonomics improves aiming, switching, and reload behavior. It also slows aim-stamina drain and speeds recovery.

Each weapon maps ergonomics into its own handling ranges, so the same stat change can have different effects across weapons. These mappings normally use a 0 to 100 range.

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

### Muzzle loudness

`muzzle_loudness` is an additive adjustment to the gunshot loudness multiplier. The completed value starts at `1` and is clamped from `0.1` to `2`.

For example, a muzzle device with `-0.70` normally produces a completed multiplier of `0.30`. Sound assets and special muzzle behavior can make equal values sound different.

### Price

`price` is the attachment's cost in credits. Price affects accessibility but does not offset an item's combat strength.

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
