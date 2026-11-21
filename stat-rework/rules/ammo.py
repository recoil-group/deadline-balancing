"""Ammunition (cartridges, shotgun shells, RPG warheads): zero on all three new stats.

Rule, in plain words: a round does not change how fast the gun comes up (handling), how fast a
magazine goes in (reload_speed) or how much the gun sways (stability), so every ammunition row
gets 0 / 0 / 0. Everything a round really does stays where it already is: recoil, deviation,
velocity, loudness and weight on the sheet; damage, penetration, suppression and tracer in
calibers.csv. Nothing is moved into recoil.

Why not keep the old ergonomics somewhere (see notes/ammo.md for the numbers):
- Old ammo ergo (-4..+3) was a scoring filler in the ammo "super" sheets ("tracer = most ergo,
  unless subsonic is there"; "tracer logic, we gotta undo this at some point"). It ran *with*
  recoil, not against it: soft rounds got less recoil *and* more ergo, harsh rounds got both
  penalties. It was a second reward for the same trait, not compensation for a separate drawback.
- Stability (the miner's alternative) would make subsonics and tracers reduce breathing sway,
  which no reader of the stat could predict. Handling and reload are worse fits still.
- Dropping it does not systematically worsen in-slot parity on the team's own strength score:
  across the 12 calibre super sheets the spread shrinks in 4, is unchanged in 3 and grows in 5
  (most in 9x18, 9mm, 7.62x54R). The loss per round is at most 3 old points (about 15 ms ADS).
- The default round of every calibre is 0 already; the 12g default (00 buck, -3) moves into the
  shotgun bases at calibration, so stock builds do not move.
"""


def restat(item, ctx, base):
    return {"handling": 0.0, "reload_speed": 0.0, "stability": 0.0,
            "_rule": f"ammo: 0/0/0, old ergo {item['ergonomics']:+g} dropped (rounds do not change ADS, reload or sway)"}
