"""Attachment tree model and build resolution for the stat rework.

Reads the Studio dumps in data/raw/ (see README for how they are produced) and
exposes the attachment tree, compatibility checks, build resolution and stat
summing with the game's stacking rules (count_stats.ts).

`python tree.py` writes the reduced, committed tree dump data/tree.json.
"""

import csv
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
REPO = os.path.dirname(HERE)

NEW_STATS = ["handling", "reload_speed", "stability"]
OLD_COLUMNS = [
    "id", "class", "name", "pretty_name", "ergonomics", "weight", "horizontal_recoil",
    "vertical_recoil", "magazine_capacity", "barrel_deviation", "bullet_damage", "bullet_velocity",
    "buck_barrel_deviation", "fire_rate", "muzzle_loudness", "price",
]
NEW_COLUMNS = [
    "id", "class", "name", "pretty_name", "handling", "reload_speed", "stability", "weight",
    "horizontal_recoil", "vertical_recoil", "magazine_capacity", "barrel_deviation", "bullet_damage",
    "bullet_velocity", "buck_barrel_deviation", "fire_rate", "muzzle_loudness", "price",
]
NUMERIC = [c for c in NEW_COLUMNS[4:] if c != "price"] + ["ergonomics", "price"]


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, dict):
        return [v[k] for k in sorted(v, key=lambda x: int(x) if str(x).isdigit() else 0)]
    return [v]


def num(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(v)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- sheet io

def read_sheet(path):
    """Return (meta_row, header, rows) where rows are dicts with an extra '_class' key."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    meta, header = rows[0], rows[1]
    out = []
    cls = None
    for r in rows[2:]:
        d = dict(zip(header, r + [""] * (len(header) - len(r))))
        if d.get("class"):
            cls = d["class"]
        d["_class"] = cls
        d["_is_class_row"] = bool(d.get("class")) and not d.get("name")
        out.append(d)
    return meta, header, out


def write_sheet(path, meta, header, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(meta + [""] * (len(header) - len(meta)) if len(meta) < len(header) else meta[: len(header)])
        w.writerow(header)
        for d in rows:
            w.writerow([d.get(c, "") for c in header])


def sheet_stats(rows):
    """name -> {stat: float} for item rows."""
    out = {}
    for d in rows:
        if d["_is_class_row"] or not d.get("name"):
            continue
        out[d["name"]] = {k: num(d.get(k)) for k in d if k not in ("id", "class", "name", "pretty_name", "_class", "_is_class_row")}
        out[d["name"]]["_class"] = d["_class"]
        out[d["name"]]["_pretty"] = d.get("pretty_name", "")
    return out


# ---------------------------------------------------------------- tree

class Tree:
    def __init__(self, raw=RAW):
        if not os.path.exists(os.path.join(raw, "attachment_data.json")):
            self._from_reduced(os.path.join(HERE, "data", "tree.json"))
            return
        A = json.load(open(os.path.join(raw, "attachment_data.json")))
        W = json.load(open(os.path.join(raw, "weapon_data.json")))
        G = json.load(open(os.path.join(raw, "gun_game_setups.json")))
        self.classes = {}
        self.att = {}
        for o in A:
            cd = o["class_def"] if isinstance(o["class_def"], dict) else {}
            cname = o["class"]
            members = []
            for it in o["items"]:
                name = it["__name"]
                disp = it.get("display") or {}
                at = it.get("attach_type")
                at = as_list(at) if at is not None else []
                self.att[name] = {
                    "name": name,
                    "class": cname,
                    "folder": o["path"].split(".")[-2],
                    "category": disp.get("category"),
                    "sort_category": disp.get("sort_category"),
                    "display_name": disp.get("name"),
                    "attach_type": at,
                    "is_muzzle_device": bool(it.get("is_muzzle_device")),
                    "is_rail_panel": bool(it.get("is_rail_panel")),
                    "is_iron_sight": bool(it.get("is_iron_sight")),
                    "mountable_types": sorted(k for k, v in (it.get("mountable_types") or {}).items() if v),
                    "has_mountable_types": "mountable_types" in it,
                    "map": [self._map_entry(m) for m in as_list(it.get("map"))],
                    "global_flags": sorted((it.get("global_flags") or {}).keys()),
                    "global_flag_values": {k: v for k, v in (it.get("global_flags") or {}).items()
                                           if k in ("mag_space", "mag_space_add", "shell_size") and isinstance(v, (int, float))},
                    "incompatible_attachments": as_list(it.get("incompatible_attachments")),
                    "incompatible_category": as_list(it.get("incompatible_category")),
                    "has_property_patch": any(c.startswith("property_patch") for c in it.get("__children", [])),
                    "has_runtime_properties": any(c.startswith("runtime_properties") for c in it.get("__children", [])),
                }
                members.append(name)
            self.classes[cname] = {
                "name": cname,
                "display": cd.get("name"),
                "is_rail": bool(cd.get("is_rail")),
                "is_single_mount_rail": bool(cd.get("is_single_mount_rail")),
                "is_magazine": bool(cd.get("isMagazine")),
                "folder": o["path"].split(".")[-2],
                "members": members,
            }
        self.weapons = {}
        for w in W:
            d = w["defaults"] if isinstance(w["defaults"], dict) else {}
            self.weapons[w["name"]] = {
                "name": w["name"],
                "category": w["category"],
                "map": [self._map_entry(m) for m in as_list(d.get("map"))],
                "default": (d.get("default") or {}).get("map", []),
                "presets": {k: ((v.get("preset") or v).get("map", []) if isinstance(v, dict) else []) for k, v in (w["presets"] if isinstance(w.get("presets"), dict) else {}).items()},
                "rpm": (w.get("firing") or {}).get("rpm"),
                "magazine_type": (w.get("generalData") or {}).get("magazine_type"),
                "markers": w.get("markers", []),
            }
        self.setups = []
        for g in G:
            d = g["data"]
            if not isinstance(d, dict):
                continue
            p = d.get("preset") or {}
            self.setups.append({"name": g["name"], "weapon": d.get("code"), "map": p.get("map", []) if isinstance(p, dict) else []})

    def _from_reduced(self, path):
        d = json.load(open(path))
        self.classes = d["classes"]
        self.att = {n: dict(a) for n, a in d["attachments"].items()}
        for a in self.att.values():
            a.setdefault("global_flag_values", {})
        self.weapons = {n: dict(w, markers=[]) for n, w in d["weapons"].items()}
        self.setups = d["official_setups"]

    @staticmethod
    def _map_entry(m):
        if not isinstance(m, dict):
            return {"class": None}
        mt = m.get("mount_type")
        return {
            "class": m.get("class"),
            "mount_type": as_list(mt) if mt is not None else None,
            "default": m.get("default"),
            "model_name": m.get("model_name"),
        }

    # -------------------------------------------------- compatibility

    @staticmethod
    def weapon_ok(a, weapon):
        wt = [t for t in a["mountable_types"] if t.startswith("WEAPON_")]
        return not wt or ("WEAPON_" + weapon) in wt

    @staticmethod
    def mount_ok(a, mount_type):
        if mount_type is None or not a["has_mountable_types"]:
            return True
        mts = set(a["mountable_types"])
        matched = False
        for v in mount_type:
            if v.startswith("!"):
                if v[1:] in mts:
                    return False
                matched = True
            elif v in mts:
                matched = True
        return matched

    def candidates(self, entry, weapon):
        c = self.classes.get(entry["class"])
        if not c:
            return []
        return [n for n in c["members"] if self.weapon_ok(self.att[n], weapon) and self.mount_ok(self.att[n], entry["mount_type"])]

    def is_rail(self, entry):
        c = self.classes.get(entry["class"])
        return bool(c and c["is_rail"])

    # -------------------------------------------------- build resolution

    def resolve(self, weapon, save_map):
        """Ordered list of (path, name) mounted by a save tree, following ItemBuild.tree_crawl."""
        out = []
        self._crawl(self.weapons[weapon]["map"], as_list(save_map), weapon, "", out, 0)
        return out

    def _crawl(self, entries, saves, weapon, path, out, depth):
        if depth > 30:
            return
        for i, entry in enumerate(entries):
            save = saves[i] if i < len(saves) and isinstance(saves[i], dict) else {}
            p = f"{path}/{i}:{entry['class']}"
            if self.is_rail(entry):
                for j, s in enumerate(as_list(save.get("attached"))):
                    if not isinstance(s, dict):
                        continue
                    n = s.get("name")
                    if n in (None, "", "nothing"):
                        continue
                    a = self.att.get(n)
                    if not a or a["class"] != entry["class"]:
                        continue
                    out.append((f"{p}[{j}]", n))
                    self._crawl(a["map"], as_list(s.get("attached")), weapon, f"{p}[{j}]", out, depth + 1)
                continue
            n = save.get("name")
            if n in ("", "nothing"):
                n = None
            a = self.att.get(n) if n else None
            if a and a["class"] != entry["class"]:
                a = None
            if a is None and entry.get("default"):
                a = self.att.get(entry["default"])
            if a is None:
                continue
            out.append((p, a["name"]))
            self._crawl(a["map"], as_list(save.get("attached")), weapon, p, out, depth + 1)

    def stock_build(self, weapon):
        return self.resolve(weapon, self.weapons[weapon]["default"])

    # -------------------------------------------------- stats

    def sum_stats(self, weapon, names, stats, keys):
        """Apply count_stats.ts stacking rules. `names` in mount order."""
        tot = {k: stats.get(weapon, {}).get(k, 0.0) for k in keys}
        grip = False
        panels = 0
        sights = 0
        last_muzzle = None
        for n in names:
            a = self.att.get(n, {})
            s = stats.get(n, {})
            is_grip = "grip" in a.get("attach_type", [])
            full = True
            if is_grip:
                full = not grip
                grip = True
            elif a.get("is_muzzle_device"):
                last_muzzle = n
                full = False
            elif a.get("is_rail_panel"):
                panels += 1
                full = panels <= 4
            elif a.get("is_iron_sight"):
                sights += 1
                full = sights <= 2
            for k in keys:
                if k == "weight" or full:
                    tot[k] += s.get(k, 0.0)
        if last_muzzle:
            s = stats.get(last_muzzle, {})
            for k in keys:
                if k != "weight":
                    tot[k] += s.get(k, 0.0)
        return tot

    # -------------------------------------------------- incompatibility rules

    def violations(self, weapon, names):
        """Item-level incompatibility rules a build breaks (check_compatibility.ts semantics).

        Covers each mounted item's `incompatible_attachments` patterns. Slot-level
        `incompatible_with_when_mounted` rules need mount positions and are not checked.
        """
        mounted = set(names)
        cats = set()
        for n in names:
            cats.update(self.att.get(n, {}).get("incompatible_category", []))

        def leaf(tok):
            tok = tok.strip()
            if tok.startswith("$"):
                if tok[1:2] == "!":  # the game compares a $! pattern against attachment names
                    return tok[2:] not in mounted
                return tok[1:] in cats
            if tok.startswith("!"):
                name = tok[1:]
                if name.startswith("WEAPON_"):
                    return name != "WEAPON_" + weapon
                return name not in mounted
            if tok.startswith("WEAPON_"):
                return tok == "WEAPON_" + weapon
            return tok in mounted

        out = []
        for n in names:
            for pat in self.att.get(n, {}).get("incompatible_attachments", []):
                if not isinstance(pat, str):
                    continue
                pat = pat.replace("\n", "")
                if all(any(leaf(t) for t in part.split("|")) for part in pat.split("&")):
                    out.append(f"{n}: {pat}")
        return out

    # -------------------------------------------------- reduced dump

    def reduced(self):
        return {
            "classes": self.classes,
            "attachments": {
                n: a for n, a in self.att.items()
            },
            "weapons": {n: {k: v for k, v in w.items() if k not in ("markers",)} | {"marker_stats": sorted({m["tied_to"] for m in w["markers"]})} for n, w in self.weapons.items()},
            "official_setups": self.setups,
        }


def weapon_slot_index(tree, weapon, max_depth=12):
    """Every slot reachable from a weapon: (path, entry, candidates, parent_item). Memo on item."""
    seen_items = set()
    slots = []

    def walk(entries, path, parent, depth):
        if depth > max_depth:
            return
        for i, e in enumerate(entries):
            if e["class"] is None:
                continue
            cands = tree.candidates(e, weapon)
            p = f"{path}/{i}:{e['class']}"
            slots.append({"path": p, "entry": e, "candidates": cands, "parent": parent, "rail": tree.is_rail(e)})
            for c in cands:
                key = (c, depth)
                if c in seen_items:
                    continue
                seen_items.add(c)
                walk(tree.att[c]["map"], p + ">" + c, c, depth + 1)

    walk(tree.weapons[weapon]["map"], "", weapon, 0)
    return slots


if __name__ == "__main__":
    t = Tree()
    json.dump(t.reduced(), open(os.path.join(HERE, "data", "tree.json"), "w"), indent=1, sort_keys=True)
    print("classes", len(t.classes), "attachments", len(t.att), "weapons", len(t.weapons), "setups", len(t.setups))
