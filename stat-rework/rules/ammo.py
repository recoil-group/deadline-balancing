"""Ammunition (cartridges, shotgun shells, RPG warheads).

MODE = "keep" (the lead's decision for this pass, after the orchestrator's review): each round keeps
its old value as handling = E, stability = 0.85 * E, reload 0, so EV = E. Soft-shooting loads are
easier to bring up and hold steady, harsh loads the opposite. The aim of this pass is the stat split,
not an ammunition rebalance: the team's ammo change sheets score ergonomics and built each calibre's
parity on it, and zeroing would take 7-13 points of compensation off slugs, birdshot and bean bags.

MODE = "zero" is the alternative, one edit away: every ammunition row gets 0 / 0 / 0, because a
round does not change how fast the gun comes up, how fast a magazine goes in or how much the gun
sways. The case for it, from the agent who re-statted this family (numbers in notes/ammo.md):
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



MODE = "keep"            # "keep" or "zero"
KEEP_HANDLING, KEEP_STABILITY = 1.0, 0.85


def restat(item, ctx, base):
    e = item["ergonomics"]
    if MODE == "zero":
        return {"handling": 0.0, "reload_speed": 0.0, "stability": 0.0,
                "_rule": f"ammo (zero mode): old ergo {e:+g} dropped"}
    return {"handling": KEEP_HANDLING * e, "reload_speed": 0.0, "stability": KEEP_STABILITY * e,
            "_rule": f"ammo (keep mode): handling 1.0 x E, stability 0.85 x E, EV kept (soft loads come up and hold steadier)"}
