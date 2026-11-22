"""Split rules: how an item's old `ergonomics` becomes handling, reload_time and stability.

Pricing currency (see ../RULES.md, "Value accounting"):

    EV = 0.60 * handling + 0.40 * reload_points + 0.47 * stability

Family rules split an item's value in old ergonomics points, reload included (`reload_points`, the
v4 0-100 reload stat). `restat` then hands the item to reload_scope.py (round 5), which sets the
sheet's `reload_time` (a fraction of the weapon's base reload time, contract v5) from its table of
reload parts, and gives a non-reload part's reload points back in handling and stability.

`time_of` converts points to reload_time (1.1 / (1.1 + 0.004 p) - 1, so 1% of reload time is about
2.75 points); `ev` takes reload_time and prices it through the exact inverse, `points_of`.

EV is measured in old ergonomics points. One old ergonomics point bought ADS, reload, draw/stow,
sprint-out and aim stamina. Draw/stow, sprint-out and aim stamina now belong to weapon weight, so
the part of an old point that new stats can carry is ADS (handling, ~45%) and reload (~30%).
Stability is new and priced at ~35%. Normalised so that h = r = E, s = 0 keeps EV = E.

A family's default split vector (a_h, a_r, a_s) has EV(vector) ~= 1, so the first pass neither
inflates nor deflates a part. Family modules (rules/<family>.py) refine this per item; overrides
(overrides/<family>.csv) handle the remaining exceptions with a note.
"""

import importlib
import math
import sys

W_H, W_R, W_S = 0.60, 0.40, 0.47

# family -> (a_h, a_r, a_s, weight_credit_per_dw, reason)
# The weight credit is 0 everywhere: RULES.md section 3 explains why. It is kept as a knob.
DEFAULT_VECTORS = {
    "magazine": (0.6, 1.5, 0.0, 0.0, "magazines mostly change reload; bulk under the gun slows ADS a little"),
    "mag_control": (0.4, 1.8, 0.0, 0.0, "releases, magwells, mag pulls, plates exist to speed the reload"),
    "stock": (0.8, 0.3, 0.9, 0.0, "shouldering speed and steadiness; little reload effect"),
    "pistol_grip": (1.0, 0.4, 0.5, 0.0, "grip angle and texture help getting on target; some control"),
    "foregrip": (0.8, 0.0, 1.1, 0.0, "front support mostly steadies the gun; also drives it onto target"),
    "handguard": (0.9, 0.1, 0.8, 0.0, "front-end bulk drives handling; length and mass drive steadiness"),
    "barrel": (1.0, 0.0, 0.85, 0.0, "length and front mass: handling and steadiness (length rule refines)"),
    "muzzle": (1.1, 0.0, 0.75, 0.0, "front mass and length; old penalty partly stood for weight"),
    "optic": (1.5, 0.0, 0.2, 0.0, "sight bulk and height affect getting on target; old penalty partly weight"),
    "iron_sight": (1.5, 0.0, 0.2, 0.0, "sight picture acquisition"),
    "receiver": (0.8, 0.6, 0.6, 0.0, "mixed: receiver features touch every axis"),
    "internals": (1.0, 0.8, 0.1, 0.0, "controls: selector/safety handling, catches/charging handles reload"),
    "tactical": (1.6, 0.0, 0.0, 0.0, "bulk on the front end affects handling only"),
    "bayonet": (0.8, 0.0, 1.0, 0.0, "front weight and length"),
    "misc": (0.8, 0.4, 0.7, 0.0, "unclassified small parts"),
    "ammo": (0.0, 0.0, 0.0, 0.0, "ammunition does not change handling, reload or sway (see rules/ammo.py)"),
}


RELOAD_STEP = 0.001  # reload_time rounding: 0.1% of time, finer than half a reload point anywhere


def time_of(points):
    """Reload points (v4) -> reload_time fraction (v5), rounded to RELOAD_STEP."""
    t = 1.1 / (1.1 + 0.004 * points) - 1
    t = round(t / RELOAD_STEP) * RELOAD_STEP
    return round(t, 3) + 0.0


def points_of(rt):
    """reload_time fraction -> the reload points it is worth (exact inverse of time_of, unrounded)."""
    return (1.1 / (1 + rt) - 1.1) / 0.004


def ev(h, rt, s):
    """Value in old ergonomics points; rt is reload_time (lower is better)."""
    return W_H * h + W_R * points_of(rt) + W_S * s


def round_half(x):
    """Round to the nearest 0.5, ties away from zero."""
    y = math.floor(abs(x) * 2 + 0.5) / 2
    return math.copysign(y, x) if y else 0.0


def reference_weight(item, ctx):
    """Median weight of the item's competing sets (itself included); its own weight if it has none."""
    if ctx is None:
        return item["weight"]
    cache = ctx.__dict__.setdefault("_ref_weight", {})
    if item["name"] not in cache:
        ws = [item["weight"]] + [c["weight"] for c in ctx.competitors(item)]
        ws.sort()
        cache[item["name"]] = ws[len(ws) // 2] if len(ws) % 2 else (ws[len(ws) // 2 - 1] + ws[len(ws) // 2]) / 2
    return cache[item["name"]]


def credit_for(item):
    """The configured weight credit for an item's family (0 everywhere in this pass)."""
    return DEFAULT_VECTORS.get(item["family"], DEFAULT_VECTORS["misc"])[3]


def adjusted_ergo(item, credit, ctx=None):
    """Take the weight double charge out of a negative ergonomics value.

    The old sheet charged extra weight relative to the alternatives with negative ergonomics.
    Weight now charges handling-type costs itself, so `credit` ergonomics per dw of weight above
    the competing set's median is given back. Only negative values move, and never past zero: a
    heavy part keeps whatever penalty its weight does not explain.
    """
    e = item["ergonomics"]
    if e >= 0 or credit <= 0:
        return e
    extra = max(0.0, item["weight"] - reference_weight(item, ctx))
    return min(0.0, e + credit * extra)


def default_split(item, ctx=None):
    a_h, a_r, a_s, credit, why = DEFAULT_VECTORS.get(item["family"], DEFAULT_VECTORS["misc"])
    e = adjusted_ergo(item, credit, ctx)
    note = f"default {item['family']} split ({a_h}/{a_r}/{a_s})"
    if abs(e - item["ergonomics"]) > 1e-9:
        note += f", weight credit {item['ergonomics']:+g}->{e:+.2f}"
    return {"handling": e * a_h, "reload_points": e * a_r, "stability": e * a_s, "_rule": note}


_modules = {}
_warned = set()


def _warn(key, msg):
    if key not in _warned:
        _warned.add(key)
        print(f"warning: {msg}", file=sys.stderr)


def family_module(fam):
    if fam not in _modules:
        try:
            _modules[fam] = importlib.import_module(f"rules.{fam}")
        except ModuleNotFoundError as e:
            if e.name != f"rules.{fam}":
                _warn(fam, f"rules/{fam}.py failed to import ({e}); using the default split")
            _modules[fam] = None
        except Exception as e:  # a family module being edited must not break everyone else
            _warn(fam, f"rules/{fam}.py failed to import ({e!r}); using the default split")
            _modules[fam] = None
    return _modules[fam]


def restat(item, ctx):
    """Return {handling, reload_time, stability, _rule, [other columns]} for one item."""
    import reload_scope

    out = _restat_points(item, ctx)
    note = reload_scope.apply(item, out, ctx)  # round 5: reload re-statted per kind of part (reload_scope.py)
    if note:
        out["_rule"] = (out.get("_rule") or "") + "; " + note
    return out


def _restat_points(item, ctx):
    base = default_split(item, ctx)
    mod = family_module(item["family"])
    if mod is not None and hasattr(mod, "restat"):
        try:
            out = mod.restat(item, ctx, dict(base))
        except Exception as e:
            _warn(item["family"] + ":run", f"rules/{item['family']}.py raised {e!r} on {item['name']}; using the default split")
            out = None
        if out is not None:
            for k in ("handling", "reload_points", "stability"):
                out.setdefault(k, base[k])
            out.setdefault("_rule", f"rules/{item['family']}.py")
            return out
    return base
