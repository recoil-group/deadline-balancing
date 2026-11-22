"""Tactical devices: lasers, flashlights, combo units, light heads/bodies/tailcaps.

Rules, in plain words (E = old ergonomics, no weight credit, RULES.md section 3):

1. A device bolted to the front end is bulk you swing onto target: handling = 1.6 * E, reload 0,
   stability 0 (EV kept: 1.6 * 0.60 = 0.96). Lights were 0 and stay 0; lasers and combo units
   (-0.5..-2) become -1..-3 handling. Their front mass already buys -1..-3 vertical recoil on
   the sheet, and a laser's real payoff (smaller hip free-aim) lives in lasers.csv.
2. Devices that are really another part are re-statted as that part: the LTsU laser grip of the
   Makarov replaces the pistol grip, so it takes the pistol-grip split (1.0 / 0.4 / 0.5).
3. Internal lasers (guide-rod lasers) and light sub-parts with no old value stay empty.

Light-vs-light ties (same 0, different weight) are left: the heavier lights are the brighter ones
in flashlights.csv. Hand exceptions are in overrides/tactical.csv.
"""

HANDLING_PER_E = 1.6

AS_PISTOL_GRIP = {"pm_laser_ltsu_pm_laser"}
PISTOL_GRIP_SPLIT = (1.0, 0.4, 0.5)


def restat(item, ctx, base):
    e = item["ergonomics"]
    if item["name"] in AS_PISTOL_GRIP:
        a_h, a_r, a_s = PISTOL_GRIP_SPLIT
        return {"handling": a_h * e, "reload_points": a_r * e, "stability": a_s * e,
                "_rule": "tactical: laser grip replaces the pistol grip, pistol-grip split 1.0/0.4/0.5"}
    return {"handling": HANDLING_PER_E * e, "reload_points": 0.0, "stability": 0.0,
            "_rule": f"tactical: front-end bulk, handling = {HANDLING_PER_E} * E"}
