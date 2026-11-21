"""Slot family for every sheet item. The split rules key on these."""
import re

# ordered (family, regex on lowercased display category or class name)
RULES = [
    ("ammo", r"ammunition|^ammo_"),
    ("magazine", r"^magazine$|^drum|^mag$|magazine \(|^magazine_|_mag$"),
    ("mag_control", r"mag(azine)? ?release|magwell|mag well|mag ?assist|mag ?pull|magazine ?extension|bottom ?plate|mag ?plate|mag ?sleeve|magazine eject|mag cap|shell carrier|shell feeder|feeder"),
    ("muzzle", r"suppressor|muzzle|flash ?hider|compensator|thread|brake|silencer|booster|choke|barrel extension|end cap"),
    ("barrel", r"^barrel|barrel$|warhead"),
    ("stock", r"stock|butt ?pad|buttpad|cheek|buffer|castle ?nut|end ?plate|endplate|recoil pad|brace|stock pad|hinge|tailhook"),
    ("pistol_grip", r"pistol grip|^grip$|grip core|grip module|backstrap|grip wrap|grip panel|palm rest|grip plate|^grips$"),
    ("foregrip", r"foregrip|vertical grip|angled grip|bipod|handstop|hand stop|grip pod|hand ?guard grip|barricade"),
    ("handguard", r"handguard|hand guard|rail panel|mlok|m-lok|rail cover|top cover|upper handguard|lower handguard|^rail|side rail|picatinny rail|rail mount|bottom rail|shroud|gas tube|gastube|accessory rail|keymod"),
    ("internals_spring", r"spring|firing pin|guide rod"),
    ("optic", r"optic|scope|sight mount|riser|eye ?cup|holo|reflex|red dot|magnifier|^sight$|prism|dovetail|\\bring|mount$|footprint|cap$|caps$|lens|^mount|adapter plate|offset"),
    ("iron_sight", r"front sight|rear sight|battle sight|aperture|iron|sight post|sight base|sight block|sight hood|carry handle"),
    ("tactical", r"laser|flashlight|light|illuminator|peq|weapon light|tailcap|pressure"),
    ("bayonet", r"bayonet|knife|blade"),
    ("receiver", r"receiver|dust cover|slide|frame|trunnion|lower|upper|housing|chassis|body"),
    ("internals", r"bolt|trigger|hammer|selector|safety|charging handle|cocking|gas ?block|gasblock|piston|spring|guide rod|sear|catch|lever|ejector|extractor|plunger|pin|lug|regulator|takedown|firing|tube|retainer|connector|function|controls|deflector"),
]


def family(item, tree_att=None):
    """item: sheet stats dict (has _class); tree_att: Studio attachment record or None."""
    cat = ((tree_att or {}).get("category") or "").lower().strip()
    at = (tree_att or {}).get("attach_type") or []
    cls = (item.get("_class") or "").lower()
    if "ammo" in at or cls.startswith("ammo_"):
        return "ammo"
    if (tree_att or {}).get("is_muzzle_device"):
        return "muzzle"
    if "magazine" in at:
        return "magazine"
    if (tree_att or {}).get("is_rail_panel"):
        return "handguard"
    if (tree_att or {}).get("is_iron_sight"):
        return "iron_sight"
    if "bipod" in at or "grip" in at:
        return "foregrip"
    if ("optic" in at or "magnifier" in at) and not re.search(r"slide|receiver|spring|pin", cat):
        return "optic"
    if "laser" in at or "flashlight" in at:
        return "tactical"
    if "barrel" in at:
        return "barrel"
    if "bayonet" in at:
        return "bayonet"
    for fam, rx in RULES:
        if cat and re.search(rx, cat):
            return "internals" if fam == "internals_spring" else fam
    for fam, rx in RULES:
        if re.search(rx, cls):
            return "internals" if fam == "internals_spring" else fam
    return "misc"
