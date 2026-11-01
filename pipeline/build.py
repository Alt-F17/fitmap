"""Aggregate verified claims into the app's data file (app/data.json).

Edge = (accessory made for A, used on B, category). Each edge is scored three times:
all brands, AXS-only, TUFF8-only. Evidence quotes are kept so reps can see the source.
"""
import datetime
import json
import math
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
APP = ROOT / "app"
TODAY = datetime.date.today()
VCODE = {"fits": "y", "fits_with_caveat": "c", "doesnt_fit": "n"}


def brand_bucket(claim):
    text = f"{claim.get('brand', '')} {claim.get('product', '')} {claim.get('context', '')}".lower()
    if re.search(r"\b(axs|axessorize|armorglass|proshield)\b", text):
        return "axs"
    if re.search(r"\btuff\s?8\b", text):
        return "tuff8"
    return "other"


def weight(c):
    w = 1.0 if c["evidence"] == "firsthand" else 0.35
    if c["kind"].startswith("review"):
        w += 0.15
    try:
        age_days = (TODAY - datetime.date.fromisoformat(c["date"])).days
    except ValueError:
        age_days = 9999
    if age_days > 540:
        w *= 0.75
    w += min(math.log2(max(c.get("score") or 0, 0) + 1), 4) * 0.05
    return w


def score(claims):
    """Return verdict/confidence for a set of claims on one edge, or None."""
    if not claims:
        return None
    pos = [c for c in claims if c["verdict"] != "doesnt_fit"]
    neg = [c for c in claims if c["verdict"] == "doesnt_fit"]
    wp, wn = sum(map(weight, pos)), sum(map(weight, neg))
    first_pos = len({c["url"] for c in pos if c["evidence"] == "firsthand"})
    first_neg = [c for c in neg if c["evidence"] == "firsthand"]
    if wp >= 0.5 and wn >= 0.5:
        verdict, conf = "mixed", "mixed"
    elif wn > wp:
        verdict = "doesnt_fit"
        conf = "strong" if len(first_neg) >= 2 else "likely"
    else:
        caveated = sum(weight(c) for c in pos if c["verdict"] == "fits_with_caveat")
        verdict = "fits_with_caveat" if caveated >= 0.4 * wp else "fits"
        conf = "strong" if first_pos >= 3 and wp >= 2.5 and not first_neg else "likely"
        if wp < 0.6:
            conf = "weak"
    caveats = defaultdict(float)
    for c in pos:
        for cv in c.get("caveats") or []:
            caveats[cv] += weight(c)
    top = [k for k, _ in sorted(caveats.items(), key=lambda kv: -kv[1])][:3]
    return {"v": verdict, "k": conf, "n": len(claims), "cv": top}


def main():
    devices = json.loads((DATA / "devices.json").read_text())
    in_scope = {d["id"] for d in devices} | {"universal"}
    audit = {}
    if (DATA / "verdicts.jsonl").exists():
        for line in (DATA / "verdicts.jsonl").read_text().splitlines():
            r = json.loads(line)
            audit[r["k"]] = r
    dropped = 0
    claims, seen = [], set()
    for line in (DATA / "claims.jsonl").read_text().splitlines():
        c = json.loads(line)
        if c["accessory_for"] not in in_scope or c["used_on"] not in in_scope:
            continue  # device removed from scope (e.g. foldables)
        a = audit.get(f"{c['sid']}|{c['accessory_for']}|{c['used_on']}|{c['category']}")
        if a and a["label"] == "wrong_verdict" and a.get("corrected_verdict"):
            c["verdict"] = a["corrected_verdict"]
        elif a and a["label"] != "supported":
            dropped += 1
            continue
        # the same post can arrive via several routes (archive, thread fetch, search excerpt):
        # count each distinct quote once per edge
        quote_key = re.sub(r"[\W_]+", "", c["quote"].lower())[:60]
        key = (c["accessory_for"], c["used_on"], c["category"], quote_key)
        if key in seen or (c["sid"], c["accessory_for"], c["used_on"], c["category"]) in seen:
            continue
        seen.add(key)
        seen.add((c["sid"], c["accessory_for"], c["used_on"], c["category"]))
        c["bucket"] = brand_bucket(c)
        claims.append(c)
    # Store-tested results entered by reps later go in data/store_tests.jsonl (same schema).
    tests = DATA / "store_tests.jsonl"
    if tests.exists():
        for line in tests.read_text().splitlines():
            c = json.loads(line)
            c["bucket"] = brand_bucket(c)
            claims.append(c)

    evidence, ev_index = [], {}
    groups = defaultdict(list)
    for c in claims:
        groups[(c["accessory_for"], c["used_on"], c["category"])].append(c)

    edges = []
    for (frm, to, cat), cs in groups.items():
        s = {"all": score(cs)}
        for b in ("axs", "tuff8"):
            sb = score([c for c in cs if c["bucket"] == b])
            if sb:
                s[b] = sb
        ev_ids = []
        top = s["all"]["v"]
        agrees = lambda c: (top == "doesnt_fit") == (c["verdict"] == "doesnt_fit")
        for c in sorted(cs, key=lambda c: (not agrees(c), c["verdict"] != top, -weight(c))):
            ev_key = (c["sid"], c["quote"])  # one post can yield several claims/quotes
            if ev_key not in ev_index:
                ev_index[ev_key] = len(evidence)
                evidence.append({
                    "q": c["quote"], "u": c["url"], "d": c["date"], "s": c["kind"],
                    "x": c["context"][:140], "b": c["bucket"],
                    "br": c.get("brand") if c.get("brand") not in (None, "", "unknown") else "",
                    "ne": c.get("note_en", ""), "nf": c.get("note_fr", ""),
                })
            ev_ids.append([ev_index[ev_key], VCODE[c["verdict"]], c["evidence"][0]])
        edges.append({"f": frm, "u": to, "c": cat, "s": s, "e": ev_ids})

    out = {
        "generated": TODAY.isoformat(),
        "devices": [{"id": d["id"], "b": d["brand"], "f": d["family"], "n": d["name"],
                     "y": d["year"], "a": d["aliases"]} for d in devices],
        "edges": edges,
        "ev": evidence,
        "stats": {"claims": len(claims), "edges": len(edges), "sources": len(evidence),
                  "audited": len(audit), "dropped_by_audit": dropped},
    }
    APP.mkdir(exist_ok=True)
    (APP / "data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(out["stats"], f"{(APP / 'data.json').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
