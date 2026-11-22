"""Receiver family: uppers, lowers, full receivers, pistol slides and frames, dust covers,
trunnions, trigger housings, chassis, slide covers and slide catches/releases.

Rules, in plain words:

1. Each kind of part gets a split of its old ergonomics (table KIND_SPLIT):
   - upper receivers and full receivers: handling and stability (the receiver is the spine of the
     gun; it does not touch the magazine);
   - lower receivers: mostly reload (the magwell lives here; aftermarket lowers sell flared
     magwells and ambidextrous controls), some handling, a little stability;
   - pistol slides: mixed (lightening cuts help handling, serrations help racking on empty
     reloads, slide mass steadies the sight picture);
   - pistol frames: grip-like (stability first, then handling);
   - dust covers: handling and stability (a rigid railed cover is mass on top);
   - HK trigger housings carry the pistol grip: grip-like split;
   - the QBZ95 handguard/trigger housing is a handguard: handguard-like split;
   - bolt-action chassis that compete with stocks are stocks: stock-like split;
   - slide catches, stops and releases are reload controls: reload with a little handling;
   - optic plate covers and filler plates: zero (a plate changes nothing; it is the "no optic"
     option, so an optic "losing" to it is not a domination);
   - railed frame covers: small handling (a mounted rail is bulk);
   - castle nuts and endplates are stock-system parts: near zero.
2. Mass rule inside a competing set: of two like parts, the lighter one leans to handling and the
   heavier one to stability, value-neutrally (EV unchanged). A light part with a negative value
   ("made of knives", lightening cuts) takes its penalty on stability; a heavy part with a
   negative value takes it on handling (bulk).
3. Parts with no old value stay at zero; the default part of a slot is the zero reference.
"""

from rules import W_H, W_R, W_S

# kind -> (handling, reload_points, stability) as fractions of the old ergonomics, and the mass
# lean strength (fraction of the value moved from handling toward stability for the heaviest part).
KIND_SPLIT = {
    "upper": ((0.9, 0.0, 0.9), 0.5),
    "lower": ((0.5, 1.2, 0.3), 0.5),
    "slide": ((0.8, 0.6, 0.6), 0.5),
    "frame": ((0.7, 0.3, 0.9), 0.5),
    "dust_cover": ((0.9, 0.0, 0.9), 0.35),
    "grip_housing": ((1.0, 0.4, 0.5), 0.5),
    "handguard_housing": ((0.9, 0.1, 0.8), 0.5),
    "chassis": ((0.8, 0.3, 0.9), 0.4),
    "control": ((0.6, 1.4, 0.0), 0.0),
    "rail_cover": ((1.2, 0.0, 0.5), 0.0),
    "small": ((0.8, 0.6, 0.6), 0.0),
}

# Studio display category (lowercased) -> kind
CATEGORY_KIND = {
    "upper receiver": "upper",
    "receiver": "upper",
    "reinforcements": "upper",
    "lower receiver": "lower",
    "slide": "slide",
    "frame": "frame",
    "metal frame": "frame",
    "dust cover": "dust_cover",
    "housing": "grip_housing",
    "chassis": "chassis",
    "slide catch": "control",
    "slide stop": "control",
    "slide release": "control",
    "slide cover": "plate",
    "adapter": "plate",
    "frame cover": "rail_cover",
}

STOCK_SLOTS = ("slot:roosevelt_700_stock",)
STOCKLESS_ENDPLATES = {"thorsden_frs15_gen3_ar15_endplate"}


def kind_of(item):
    cat = (item["category"] or "").lower()
    name = item["name"]
    if any(g.startswith(STOCK_SLOTS) for g in item["groups"]):
        return "chassis"
    if "castlenut" in name or "endplate" in name:
        return "stock_system"
    if cat == "trigger housing":
        return "handguard_housing" if "handguard" in name else "small"
    return CATEGORY_KIND.get(cat, "small")


def mass_z(item, ctx):
    """Where the item's weight sits among its competitors: -1 lightest ... +1 heaviest (0 if alone)."""
    ws = [c["weight"] for c in ctx.competitors(item) if c["weight"] > 0]
    if not ws or item["weight"] <= 0:
        return 0.0
    ws = sorted(ws + [item["weight"]])
    mid = ws[len(ws) // 2] if len(ws) % 2 else (ws[len(ws) // 2 - 1] + ws[len(ws) // 2]) / 2
    half = (ws[-1] - ws[0]) / 2
    if half < 0.005:
        return 0.0
    return max(-1.0, min(1.0, (item["weight"] - mid) / half))


def split(e, vec, lean, z, axis="stability"):
    """Split old ergonomics `e` by `vec`, moving a share `lean * z` of it from handling to `axis`
    (stability or reload_points) without changing EV. Negative values lean the other way."""
    a_h, a_r, a_s = vec
    t = lean * z if e >= 0 else -lean * z
    if axis == "stability":
        t = max(-a_s * W_S / W_H, min(a_h, t))
        a_h, a_s = a_h - t, a_s + t * W_H / W_S
    else:
        t = max(-a_r * W_R / W_H, min(a_h, t))
        a_h, a_r = a_h - t, a_r + t * W_H / W_R
    return {"handling": e * a_h, "reload_points": e * a_r, "stability": e * a_s}


def restat(item, ctx, base):
    e = item["ergonomics"]
    kind = kind_of(item)
    if e == 0:
        return {"handling": 0.0, "reload_points": 0.0, "stability": 0.0, "_rule": f"receiver {kind}: no old value"}
    if kind == "plate":
        return {"handling": 0.0, "reload_points": 0.0, "stability": 0.0, "_rule": "optic plate cover: zero"}
    if kind == "stock_system":
        if item["name"] in STOCKLESS_ENDPLATES:
            return {"handling": 1.5, "reload_points": 0.0, "stability": 0.0,
                    "_rule": "stock-system part, stockless endplate: small handling; losing the stock already costs stability"}
        return {"handling": 0.0, "reload_points": 0.0, "stability": 0.0, "_rule": "stock-system part: near zero"}
    vec, lean = KIND_SPLIT[kind]
    z = mass_z(item, ctx) if lean else 0.0
    out = split(e, vec, lean, z)
    note = f"receiver {kind} {vec}"
    if lean and abs(z) > 0.05:
        note += f", mass lean z{z:+.2f}"
    out["_rule"] = note
    return out
