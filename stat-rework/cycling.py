"""Lead rule (round 6): cycling parts on manually cycled weapons carry fire_rate.

Bolt and pump cycling follows the completed fire rate (contract section 5), so the parts that are
the cycling interface say so directly in `fire_rate` (a fraction of base RPM), and nothing else
does. In scope: the pumps (Remington 870, MP-133; code bases 128 and 156 RPM) and the bolt
actions (Mosin, R700; base 50 RPM). The R700's bolt face, plug and firing pin are single-choice
parts, so it has nothing to choose and stays at its base.

The default part of each set is 0. Pumps get a few percent either way; bolts are more
conservative, because a faster bolt raises the shot cadence, which ergonomics never did (it was
capped by fire rate), so it is new power.

The value is redirected, not added: a part's fire_rate is priced at PRICE EV per 1% and that EV
is taken out of (or, for a slower part, given back to) its handling and stability, in the
proportions of value it has there. Price, in old ergonomics points per 1% of fire rate:

- pumps 1.5: before the rework one ergonomics point moved a pump by about 0.66% of its RPM (the
  R870 spanned 79-164 RPM over 0-100 ergonomics), so 1% of pump RPM is what 1.5 points of
  ergonomics bought in cycling;
- bolts 3.0, twice the pump price: on a bolt rifle the time to the next shot is the weapon's main
  limit, and no part could move it before.

Set ENABLED = False to switch the step off.
"""

ENABLED = True
PRICE = {"pump": 1.5, "bolt": 3.0}
BASE_RPM = {"Remington870": 128, "MP133": 156, "MosinNagant": 50, "Remington700": 50}

PARTS = {  # name: (fire_rate, action, reason)
    # Remington 870 pump forends (default: SpeedFeed)
    "r870_magtap_moe_handguard": (0.03, "pump", "contoured, ridged pump forend: a fast, sure stroke"),
    "pro_tactical_pr870_handguard": (-0.02, "pump", "railed pump forend: more mass to cycle, slower stroke, steadier"),
    # MP-133 pump forends (default: beechwood)
    "mp133_plastic_handguard": (0.02, "pump", "lighter synthetic pump forend: a quicker stroke"),
    # Mosin bolts (default: Mosin Default with its own handle) and bolt handles (on the infantry bolt)
    "resolute_bolt": (0.01, "bolt", "smoother aftermarket bolt: quicker to work"),
    "ivan_bolt_handle": (0.01, "bolt", "enlarged bolt knob: quicker to work"),
}


def ev(name):
    """The EV a part carries as fire_rate (0 for parts outside the step)."""
    if not ENABLED or name not in PARTS:
        return 0.0
    fr, action, _ = PARTS[name]
    return PRICE[action] * fr * 100


def apply(item, vals):
    """vals: handling, stability, reload_time (final). Sets vals["fire_rate"]; returns a note or ''."""
    from reload_scope import _move

    if not ENABLED or item["name"] not in PARTS:
        return ""
    fr, action, why = PARTS[item["name"]]
    _move(item, vals, -PRICE[action] * fr * 100)
    vals["fire_rate"] = f"{fr:g}"
    ev = PRICE[action] * fr * 100
    moved = f"{ev:.1f} EV taken from handling and stability" if ev > 0 else f"{-ev:.1f} EV given back to handling and stability"
    return f"cycling ({action}): fire_rate {fr * 100:+g}% ({why}), {moved}"
