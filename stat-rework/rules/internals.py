"""Internals family: triggers, trigger guards, hammers, fire selectors, safeties, charging
handles, bolts and carriers, bolt catches and releases, gas blocks and pistons, springs, guide
rods, levers and other small action parts.

Each control is mapped to the animation it actually speeds up (table KIND_SPLIT):

- Fire selectors, safeties and decockers: handling only (fire-mode switch is a handling
  animation). An "enhanced safety" with a bolt hold-open notch also gets reload.
- Charging handles, bolt catches and releases, bolt-catch extensions, magazine catches, the
  Mosin bolt and bolt handle, and the R700 bottom metal: reload (empty reloads and manual
  loading), with a little handling.
- Triggers, trigger shoes and the trigger-blade safety: stability first. A lighter, crisper pull
  disturbs the sight picture less; a trigger does not speed up ADS. A small handling share is
  kept so the mass rule below can separate light from heavy triggers.
- Trigger guards: oversized guards make it quicker to get a gloved finger onto the trigger, so
  handling first, a little stability.
- Takedown levers: the OEM lever is a control (handling); aftermarket extended or ledge levers are
  thumb rests and add +1 stability on top of their old value as handling.
- Bolt carriers and gas blocks: only the few with an old value carry anything. A light carrier or
  a low-profile gas block leans to handling, a heavy or buffered one to stability.
- Auto sears: their penalty goes mostly to stability (full-auto conversion is hard to hold).
- Springs, guide rods, retainers, hammers, pins, extractors and other hidden parts stay at zero.

Mass rule inside a competing set (same as rules/receiver.py): the lighter of two like parts leans
to handling, the heavier to stability (or, for reload controls, to reload: a bigger latch is
quicker to grab; ambidextrous controls count as a third of the set's weight range heavier),
value-neutrally. No fire_rate is added anywhere.
"""

from rules.receiver import mass_z, split

KIND_SPLIT = {
    # kind: ((handling, reload, stability) fractions of old ergonomics, lean strength, lean axis)
    "selector": ((1.6, 0.0, 0.0), 0.0, "stability"),
    "enhanced_safety": ((0.8, 1.2, 0.0), 0.0, "stability"),
    "control": ((0.7, 1.3, 0.0), 0.2, "reload_speed"),
    "trigger": ((0.5, 0.0, 1.0), 0.4, "stability"),
    "trigger_guard": ((0.8, 0.0, 0.5), 0.4, "stability"),
    "case_deflector": ((0.8, 0.0, 0.9), 0.5, "stability"),
    "carrier": ((0.8, 0.0, 0.9), 0.5, "stability"),
    "gas": ((1.0, 0.0, 0.8), 0.5, "stability"),
    "auto_sear": ((0.5, 0.0, 1.5), 0.0, "stability"),
}

CATEGORY_KIND = {
    "fire selector": "selector",
    "safety": "selector",
    "switch": "selector",
    "decocking lever": "selector",
    "takedown safety lever": "selector",
    "charging handle": "control",
    "bolt catch": "control",
    "bolt release": "control",
    "magazine catch": "control",
    "extension": "control",
    "bolt handle": "control",
    "cocking tube": "control",
    "forward assist": "control",
    "trigger": "trigger",
    "trigger shoe": "trigger",
    "trigger bar": "trigger",
    "trigger safety": "trigger",
    "trigger guard": "trigger_guard",
    "case deflector": "case_deflector",
    "bolt carrier": "carrier",
    "bolt carrier group": "carrier",
    "bolt": "carrier",
    "gas block": "gas",
    "gasblock": "gas",
    "gas piston": "gas",
    "gas selector": "gas",
    "auto sear": "auto_sear",
}

AMBI_BONUS = 0.3
MANUAL_ACTION = {"MosinNagant", "Remington700"}
MAGWELL_SLOTS = ("slot:roosevelt_700_magwell",)


def is_aftermarket(item, ctx):
    """True when the item is not the default of any slot it competes in."""
    return all(ctx.groups[g].get("default") != item["name"] for g in item["groups"])


def kind_of(item, ctx):
    cat = (item["category"] or "").lower()
    if any(g.startswith(MAGWELL_SLOTS) for g in item["groups"]):
        return "control"  # R700 bottom metal filed as a trigger guard
    if cat == "takedown lever":
        return "thumb_rest" if is_aftermarket(item, ctx) else "selector"
    if cat == "bolt" and item["weapons"] and set(item["weapons"]) <= MANUAL_ACTION:
        return "control"  # a bolt-action bolt is worked during every reload
    if "enhanced_safety" in item["name"]:
        return "enhanced_safety"
    return CATEGORY_KIND.get(cat, "hidden")


def restat(item, ctx, base):
    e = item["ergonomics"]
    kind = kind_of(item, ctx)
    if kind == "thumb_rest":
        return {"handling": e, "reload_speed": 0.0, "stability": 1.0,
                "_rule": "takedown lever as thumb rest: +1 stability, old value as handling"}
    if kind == "hidden" and e != 0:
        return None  # not expected; keep the default family split
    if e == 0:
        return {"handling": 0.0, "reload_speed": 0.0, "stability": 0.0,
                "_rule": f"internals {kind}: no effect on handling, reload or sway"}
    vec, lean, axis = KIND_SPLIT[kind]
    z = mass_z(item, ctx) if lean else 0.0
    if kind == "control" and "ambi" in item["name"]:
        z = min(1.0, z + AMBI_BONUS)  # an ambidextrous latch counts as a bigger one
    out = split(e, vec, lean, z, axis)
    note = f"internals {kind} {vec}"
    if lean and abs(z) > 0.05:
        note += f", mass lean to {axis} z{z:+.2f}"
    out["_rule"] = note
    return out
