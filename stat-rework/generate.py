"""Generate the reworked balancing.csv from the old sheet plus rule and override data.

    python stat-rework/generate.py --write         # write ../balancing.csv and review sheets
    python stat-rework/generate.py --preview stock # print one family's result, write nothing
    python stat-rework/generate.py --calibrate     # recompute weapon base values (see weapons.py)

Inputs (all in stat-rework/):
    data/source_balancing.csv   the old sheet (main at ec0e059), never edited
    data/raw/*.json             Studio dumps (tree, weapons, official setups)
    rules/__init__.py           pricing and default family splits
    rules/<family>.py           per-family rules
    overrides/<family>.csv      hand-tuned values, one note per row
    weapon_bases.csv            base handling / reload_speed / stability for weapon rows
"""

import argparse
import csv
import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import rules  # noqa: E402
from analysis import WEAPON_CLASSES, slot_groups  # noqa: E402
from families import family  # noqa: E402
from tree import NEW_COLUMNS, NEW_STATS, REPO, Tree, num, read_sheet  # noqa: E402

SOURCE = os.path.join(HERE, "data", "source_balancing.csv")
OUTPUT = os.path.join(REPO, "balancing.csv")
OTHER_COLUMNS = [c for c in NEW_COLUMNS[4:] if c not in NEW_STATS]


def fmt(x):
    if x is None:
        return ""
    x = rules.round_half(x) if isinstance(x, float) else x
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def load_overrides():
    out = {}
    for path in sorted(glob.glob(os.path.join(HERE, "overrides", "*.csv"))):
        src = os.path.basename(path)
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                file_rows = list(csv.DictReader(f))
        except Exception as e:
            print(f"warning: could not read overrides/{src}: {e!r}", file=sys.stderr)
            continue
        if True:
            for r in file_rows:
                n = (r.get("name") or "").strip()
                if not n or n.startswith("#"):
                    continue
                vals = {k: v.strip() for k, v in r.items() if k in NEW_COLUMNS[4:] and v is not None and v.strip() != ""}
                if n in out:
                    raise SystemExit(f"{n} overridden twice ({out[n]['_source']} and {src})")
                out[n] = {"values": vals, "note": (r.get("note") or "").strip(), "_source": src}
    return out


def load_weapon_bases():
    path = os.path.join(HERE, "weapon_bases.csv")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["name"]: r for r in csv.DictReader(f)}


class Context:
    def __init__(self):
        self.tree = Tree()
        self.meta, self.header, self.rows = read_sheet(SOURCE)
        self.groups, self.item_groups, self.item_weapons, self.parents = slot_groups(self.tree)
        self.items = {}
        for d in self.rows:
            if d["_is_class_row"] or not d.get("name"):
                continue
            a = self.tree.att.get(d["name"]) or {}
            it = {k: num(d.get(k)) for k in ("ergonomics", "weight", "horizontal_recoil", "vertical_recoil",
                                              "magazine_capacity", "barrel_deviation", "bullet_damage",
                                              "bullet_velocity", "buck_barrel_deviation", "fire_rate",
                                              "muzzle_loudness", "price")}
            it.update({
                "name": d["name"], "pretty": d.get("pretty_name", ""), "sheet_class": d["_class"],
                "raw": d, "studio": a, "category": (a.get("category") or ""),
                "attach_type": a.get("attach_type", []),
                "weapons": sorted(self.item_weapons.get(d["name"], ())),
                "groups": sorted(self.item_groups.get(d["name"], ())),
            })
            it["family"] = "weapon" if d["_class"] in WEAPON_CLASSES else family({"_class": d["_class"]}, a)
            self.items[d["name"]] = it

    def group_items(self, gid):
        return [self.items[n] for n in self.groups[gid]["items"] if n in self.items]

    def competitors(self, item):
        """Items sharing at least one competing set with `item` (excluding itself)."""
        seen = {}
        for g in item["groups"]:
            for n in self.groups[g]["items"]:
                if n != item["name"] and n in self.items:
                    seen[n] = self.items[n]
        return list(seen.values())


def generate(ctx=None, families=None):
    """Return (ctx, new_values, log). new_values: name -> dict of NEW_COLUMNS[4:] (floats or raw strings).

    Order: weapon bases and family rules, then the lead's lean pass (lean.py), then overrides.
    """
    import lean

    ctx = ctx or Context()
    overrides = load_overrides()
    bases = load_weapon_bases()
    out = {}
    rules_of = {}
    for n, it in ctx.items.items():
        if families and it["family"] not in families:
            continue
        raw = it["raw"]
        vals = {c: raw.get(c, "") for c in OTHER_COLUMNS}
        rule = ""
        if it["family"] == "weapon":
            b = bases.get(n)
            if b:
                for s in NEW_STATS:
                    vals[s] = float(b[s]) if b.get(s, "") != "" else None
                rule = "weapon base: " + (b.get("note") or "")
            else:
                e = raw.get("ergonomics", "")
                for s in NEW_STATS:
                    vals[s] = num(e) if e != "" else None
                rule = "weapon base: copied from ergonomics (no weapon_bases.csv row)"
        else:
            res = rules.restat(it, ctx)
            rule = res.pop("_rule", "")
            blank = raw.get("ergonomics", "") == ""
            for s in NEW_STATS:
                v = res.pop(s)
                vals[s] = None if (blank and abs(v) < 1e-9) else v
            for k, v in res.items():  # rule modules may also return other columns (with a reason in _rule)
                if k in OTHER_COLUMNS:
                    vals[k] = v
        out[n] = vals
        rules_of[n] = rule

    lean_input = {n: {"handling": v["handling"], "stability": v["stability"]} for n, v in out.items()
                  if ctx.items[n]["family"] != "weapon" and v["handling"] is not None and v["stability"] is not None}
    lean_notes = lean.steepen(ctx, lean_input)
    for n, note in lean_notes.items():
        out[n]["handling"] = lean_input[n]["handling"]
        out[n]["stability"] = lean_input[n]["stability"]
        rules_of[n] += "; " + note

    log = []
    for n, vals in out.items():
        raw = ctx.items[n]["raw"]
        rule = rules_of[n]
        o = overrides.get(n)
        note = ""
        if o:
            for k, v in o["values"].items():
                vals[k] = float(v) if k in NEW_STATS else v
            note = o["note"]
            rule = (rule + "; " if rule else "") + f"override ({o['_source']})"
        for k in OTHER_COLUMNS:
            if str(vals[k]) != str(raw.get(k, "")):
                log.append({"name": n, "column": k, "old": raw.get(k, ""), "new": vals[k], "why": note or rule})
        vals["_rule"] = rule
        vals["_note"] = note
    return ctx, out, log


def stats_table(ctx, out):
    """name -> numeric stats in the new layout (for simulation)."""
    st = {}
    for n, v in out.items():
        st[n] = {c: (num(v[c]) if not isinstance(v[c], float) else v[c]) if v[c] is not None else 0.0 for c in NEW_COLUMNS[4:]}
        st[n] = {c: rules.round_half(x) if c in NEW_STATS else x for c, x in st[n].items()}
    return st


def write_outputs(ctx, out, log):
    rows = []
    for d in ctx.rows:
        r = {"id": d.get("id", ""), "class": d.get("class", ""), "name": d.get("name", ""), "pretty_name": d.get("pretty_name", "")}
        if not d["_is_class_row"] and d.get("name"):
            v = out[d["name"]]
            for c in NEW_COLUMNS[4:]:
                r[c] = fmt(v[c]) if c in NEW_STATS else v[c]
        rows.append(r)
    with open(OUTPUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        meta = list(ctx.meta) + [""] * (len(NEW_COLUMNS) - len(ctx.meta))
        w.writerow(meta[: len(NEW_COLUMNS)])
        w.writerow(NEW_COLUMNS)
        for r in rows:
            w.writerow([r.get(c, "") for c in NEW_COLUMNS])
    write_review(ctx, out)
    with open(os.path.join(HERE, "review", "other_column_changes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "column", "old", "new", "why"])
        w.writeheader()
        for r in log:
            w.writerow(r)


def strength(ergo_or_ev, it):
    """The team's change-sheet strength score (RULES_MINED.md section 0), core terms."""
    return (ergo_or_ev - 20 * it["weight"] - 0.8 * it["horizontal_recoil"] - 0.6 * it["vertical_recoil"]
            - 10 * it["barrel_deviation"] + 10 * it["bullet_damage"] + 0.005 * it["bullet_velocity"]
            + 10 * it["fire_rate"] - 5 * it["muzzle_loudness"])


def review_rows(ctx, out, fam):
    """Rows for one family, grouped by competing set (an item appears once, under its first set)."""
    items = [it for it in ctx.items.values() if it["family"] == fam]
    by_group = defaultdict(list)
    for it in items:
        g = it["groups"][0] if it["groups"] else "(unreachable or not in Studio)"
        by_group[g].append(it)
    rows = []
    for g in sorted(by_group, key=lambda g: (-len(by_group[g]), g)):
        gi = ctx.groups.get(g, {})
        for it in sorted(by_group[g], key=lambda x: (x["weight"], x["name"])):
            v = out[it["name"]]
            h, r, s = (rules.round_half(v[k]) if v[k] is not None else 0.0 for k in NEW_STATS)
            rows.append({
                "set": g, "set_size": len(gi.get("items", [])), "only_choice": gi.get("only_choice", ""),
                "required": gi.get("required", ""), "name": it["name"], "pretty_name": it["pretty"],
                "category": it["category"], "old_ergo": fmt(it["ergonomics"]), "handling": fmt(h),
                "reload_speed": fmt(r), "stability": fmt(s), "ev": round(rules.ev(h, r, s), 1),
                "old_strength": round(strength(it["ergonomics"], it), 1),
                "new_strength": round(strength(rules.ev(h, r, s), it), 1),
                "weight": it["raw"].get("weight", ""), "h_recoil": v["horizontal_recoil"], "v_recoil": v["vertical_recoil"],
                "price": v["price"], "n_weapons": len(it["weapons"]), "rule": v["_rule"], "note": v["_note"],
            })
    return rows


def write_review(ctx, out):
    fams = sorted({it["family"] for it in ctx.items.values()})
    for fam in fams:
        rows = review_rows(ctx, out, fam)
        with open(os.path.join(HERE, "review", f"{fam}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", nargs="*", help="families to print; writes nothing")
    ap.add_argument("--calibrate", action="store_true", help="recompute weapon_bases.csv from anchors")
    ap.add_argument("--write", action="store_true", help="write ../balancing.csv and review/")
    a = ap.parse_args()
    if a.calibrate:
        import weapons
        weapons.calibrate()
        return
    ctx, out, log = generate()
    if a.preview is not None:
        fams = a.preview or sorted({it["family"] for it in ctx.items.values()})
        for fam in fams:
            rows = review_rows(ctx, out, fam)
            cur = None
            for r in rows:
                if r["set"] != cur:
                    cur = r["set"]
                    print(f"\n== {cur}  (size {r['set_size']}, required {r['required']}, only {r['only_choice']})")
                print(f"  {r['name'][:58]:58s} E{r['old_ergo']:>5s} -> h{r['handling']:>5s} r{r['reload_speed']:>5s} s{r['stability']:>5s} ev{r['ev']:6.1f} w{r['weight']:>5s} rec {r['h_recoil'] or 0}/{r['v_recoil'] or 0}  {r['note'][:60]}")
        return
    if not a.write:
        print("nothing written; pass --write to write ../balancing.csv and review/, or --preview FAMILY")
        return
    write_outputs(ctx, out, log)
    print(f"wrote {OUTPUT}; {len(out)} items; {len(log)} changes outside the three new columns")


if __name__ == "__main__":
    main()
