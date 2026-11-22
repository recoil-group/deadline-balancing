"""Magazine controls and magazine add-ons: almost purely reload.

Rules, in plain words (E = old ergonomics, no weight credit):

1. Releases, paddles, buttons, magwells and funnels, mag assists/pulls, loop and bumper bottom
   plates: they exist to make the reload quicker. reload = 2.5 * E, handling and stability 0
   (EV kept exactly). Standard parts at 0 stay 0. Their small recoil values are left alone.
2. Capacity extensions and base pads that add rounds: like a longer magazine. Relative to the
   set's default plate, reload = 2.125 * E_rel and handling = 0.25 * E_rel (`magazine.box_split`).
3. P320 grip sleeves fill the gap between the grip and an extended magazine: a full grip for the
   hand and a guide for the insert, so half handling and half reload (h 0.8 * E, r 1.3 * E).
4. Shotgun tube extensions (MP133, like the R870 ones in the magazine family) use
   `magazine.tube_split`: relative to the default cap, reload 1.5 * E_rel, handling 0.5 * E_rel.
5. Shell carriers, feeders, release springs: 0 (all are 0 today).
6. Stability is 0 throughout.
"""

from rules.magazine import box_split, is_tube, set_default, tube_split

QOL_RELOAD_PER_E = 2.5
SLEEVE_HANDLING_PER_E, SLEEVE_RELOAD_PER_E = 0.8, 1.3


def restat(item, ctx, base):
    e = item["ergonomics"]
    cat = item["category"].lower()
    if is_tube(item):
        return tube_split(item, ctx)
    if item["magazine_capacity"] or "coupler" in cat:
        d = set_default(item, ctx)
        e_rel = e - (d["ergonomics"] if d and d["name"] != item["name"] else 0.0)
        h, r = box_split(e_rel)
        return {"handling": h, "reload_points": r, "stability": 0.0,
                "_rule": f"capacity extension: E{e_rel:+g}, like a longer mag (r 2.125x, h 0.25x)"}
    if "sleeve" in cat:
        return {"handling": SLEEVE_HANDLING_PER_E * e, "reload_points": SLEEVE_RELOAD_PER_E * e, "stability": 0.0,
                "_rule": "grip sleeve: half handling (full grip), half reload (guides the insert)"}
    return {"handling": 0.0, "reload_points": QOL_RELOAD_PER_E * e, "stability": 0.0,
            "_rule": "reload part: all value in reload (2.5x)" if e else "standard part: 0"}
