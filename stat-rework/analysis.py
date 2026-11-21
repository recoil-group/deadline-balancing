"""Competing sets, item index and reachability.

`python analysis.py` writes:
  data/items_index.csv     one row per sheet item: family, Studio category, flags, old stats,
                           weapons that can reach it, competing sets it belongs to
  data/competing_sets.json slot groups: which items compete for the same place
"""

import csv
import hashlib
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from families import family  # noqa: E402
from tree import HERE, REPO, Tree, read_sheet, sheet_stats  # noqa: E402

WEAPON_CLASSES = {"pistol", "rifle", "shotgun", "smg", "turret", "launcher", "placer", "throwable", "wearable"}


def slot_groups(t):
    """Walk every weapon's reachable slots. Group id = class|mount_type|candidate set.

    Rails host many items at once; their candidates are split by family, because a foregrip
    competes with other foregrips on the rail, not with optics.
    """
    groups = {}
    item_groups = defaultdict(set)
    item_weapons = defaultdict(set)
    parents = defaultdict(set)  # item -> items/weapons it mounts on

    for w in t.weapons:
        seen = set()
        stack = [(t.weapons[w]["map"], w, 0)]
        while stack:
            entries, parent, depth = stack.pop()
            if depth > 14:
                continue
            for e in entries:
                if not e.get("class"):
                    continue
                cands = t.candidates(e, w)
                if t.is_rail(e):
                    by_fam = defaultdict(list)
                    for c in cands:
                        by_fam[family({"_class": t.att[c]["class"]}, t.att[c])].append(c)
                    parts = [(f"rail:{e['class']}:{f}", sorted(v), False) for f, v in by_fam.items()]
                else:
                    mt = ",".join(e["mount_type"] or [])
                    parts = [(f"slot:{e['class']}|{mt}", sorted(cands), bool(e.get("default")))]
                for gid_base, cs, required in parts:
                    if not cs:
                        continue
                    gid = gid_base + "#" + hashlib.md5("|".join(cs).encode()).hexdigest()[:6]
                    g = groups.setdefault(gid, {"id": gid, "class": e["class"], "mount_type": e["mount_type"],
                                                "rail": t.is_rail(e), "required": required,
                                                "default": e.get("default"), "items": cs,
                                                "weapons": set(), "parents": set()})
                    g["weapons"].add(w)
                    g["parents"].add(parent)
                    if e.get("default"):
                        g["required"] = True
                    for c in cs:
                        item_groups[c].add(gid)
                        item_weapons[c].add(w)
                        parents[c].add(parent)
                for c in cands:
                    if c in seen:
                        continue
                    seen.add(c)
                    stack.append((t.att[c]["map"], c, depth + 1))
    for g in groups.values():
        g["weapons"] = sorted(g["weapons"])
        g["parents"] = sorted(g["parents"])
        g["only_choice"] = len(g["items"]) == 1
    return groups, item_groups, item_weapons, parents


def main():
    t = Tree()
    meta, header, rows = read_sheet(os.path.join(REPO, "balancing.csv"))
    st = sheet_stats(rows)
    groups, item_groups, item_weapons, parents = slot_groups(t)
    json.dump(sorted(groups.values(), key=lambda g: g["id"]), open(os.path.join(HERE, "data", "competing_sets.json"), "w"), indent=1)

    cols = ["name", "pretty_name", "sheet_class", "family", "studio_class", "category", "attach_type", "flags",
            "children_classes", "n_weapons", "weapons", "groups", "ergonomics", "weight", "horizontal_recoil",
            "vertical_recoil", "magazine_capacity", "barrel_deviation", "bullet_damage", "bullet_velocity",
            "fire_rate", "muzzle_loudness", "price"]
    with open(os.path.join(HERE, "data", "items_index.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(cols)
        for d in rows:
            if d["_is_class_row"] or not d.get("name"):
                continue
            n = d["name"]
            s = st[n]
            a = t.att.get(n) or {}
            fam = "weapon" if s["_class"] in WEAPON_CLASSES else family(s, a)
            flags = [k for k in ("is_muzzle_device", "is_rail_panel", "is_iron_sight", "has_property_patch") if a.get(k)]
            if not a and n not in t.weapons:
                flags.append("not_in_studio")
            wr.writerow([n, d.get("pretty_name"), s["_class"], fam, a.get("class", ""), a.get("category", ""),
                         "+".join(a.get("attach_type", [])), "+".join(flags),
                         "+".join(sorted({m["class"] for m in a.get("map", []) if m.get("class")})),
                         len(item_weapons.get(n, ())), "+".join(sorted(item_weapons.get(n, ()))),
                         "+".join(sorted(item_groups.get(n, ())))] +
                        [d.get(c, "") for c in cols[12:]])
    print("groups", len(groups), "only-choice", sum(g["only_choice"] for g in groups.values()))


if __name__ == "__main__":
    main()
