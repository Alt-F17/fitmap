"""Harvest Reddit via PullPush: sitewide phrase search, one set of fit queries per device.

Faster and more targeted than per-subreddit word search. Output mirrors harvest.py:
data/raw_pp/<kind>_<slug>.json and data/threads/<post id>.json (fit-question threads).
"""
import json
import pathlib
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from harvest import ACCESSORY, FIT_TITLE

API = "https://api.pullpush.io/reddit/search"
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_pp"
THREADS = ROOT / "data" / "threads"
DEVICES = json.loads((ROOT / "data" / "devices.json").read_text())
SINCE_TS = 1640995200  # 2022-01-01
PAGE = 100
MAX_PAGES = 3
PAUSE_S = 1.2
UA = {"User-Agent": "accessory-xref/0.1 (research; github Alt-F17)"}

TEMPLATES = ['"{p}" case fit', '"{p}" case fits', '"{p}" protector fit', '"{p}" protector fits',
             '"{p}" compatible', '"{p}" magsafe ring', '"{p}" lens protector', '"{p}" same size']
BRAND_QUERIES = ["tuff8", "tuff 8 case", "axs case", "axs protector", "armorglass", "axessorize",
                 "axs proshield"]
GENERIC = {"g 2025", "g 2026", "40 r 5g", "40r", "60r", "50 le", "50 pro", "70 pro", "60 se",
           "40 se", "50 se", "17e", "16e"}


def phrases(d):
    """Up to 3 search phrases people actually type for this device."""
    cands = []
    for a in d["aliases"]:
        a = a.replace("galaxy ", "").replace("motorola ", "")
        if any(ch in a for ch in "()/+") or a in GENERIC or len(a) < 3 \
                or (len(a) <= 3 and not re.fullmatch(r"[sa]\d\d", a)):
            continue
        cands.append(a)
    # prefer spaced, specific forms ("s25 fe", "17 pro max", "moto g 2025")
    cands = sorted(set(cands), key=lambda a: (-a.count(" "), -len(a)))
    if d["brand"] == "TCL":
        cands = [c if c.startswith(("tcl", "nxtpaper")) else f"tcl {c}" for c in cands]
    if d["id"] in ("ip16e", "ip17e"):
        cands = [f"iphone {d['id'][2:]}"]
    return list(dict.fromkeys(cands))[:2]


def get(kind, params):
    for attempt in range(5):
        try:
            r = requests.get(f"{API}/{kind}/", params=params, headers=UA, timeout=60)
            if r.status_code == 200:
                return r.json().get("data") or []
            print(f"  {r.status_code} {params.get('q')}", flush=True)
        except Exception as e:
            print(f"  error {e}", flush=True)
        time.sleep(5 * (attempt + 1) ** 2)
    return None


def run_query(kind, q):
    slug = re.sub(r"[^a-z0-9]+", "_", f"{kind[0]}_{q}".lower()).strip("_")
    out = RAW / f"{slug}.json"
    if out.exists():
        return 0
    items, before = [], None
    for _ in range(MAX_PAGES):
        params = {"q": q, "size": PAGE, "after": SINCE_TS}
        if before:
            params["before"] = before
        page = get(kind, params)
        time.sleep(PAUSE_S)
        if page is None:
            return 0
        items.extend(page)
        if len(page) < PAGE:
            break
        before = int(min(p["created_utc"] for p in page))
    keep = ("id", "body", "title", "selftext", "subreddit", "created_utc", "score", "link_id",
            "num_comments")
    out.write_text(json.dumps([{k: p.get(k) for k in keep if k in p} for p in items],
                              ensure_ascii=False))
    return len(items)


def stage1():
    queries = list(BRAND_QUERIES)
    for d in DEVICES:
        for p in phrases(d):
            queries += [t.format(p=p) for t in TEMPLATES]
    print(f"{len(queries)} queries", flush=True)
    jobs = [(k, q) for q in queries for k in ("submission", "comment")]

    def work(job):
        n = run_query(*job)
        return job, n

    total = 0
    with ThreadPoolExecutor(2) as pool:
        for i, (job, n) in enumerate(pool.map(work, jobs), 1):
            total += n
            if i % 50 == 0:
                print(f"{i}/{len(jobs)} jobs, {total} items", flush=True)


def stage2():
    THREADS.mkdir(exist_ok=True)
    posts = {}
    for f in RAW.glob("s_*.json"):
        for p in json.loads(f.read_text()):
            posts[p["id"]] = p
    picked = [p for p in posts.values()
              if (p.get("num_comments") or 0) > 0
              and FIT_TITLE.search(f"{p.get('title', '')} {(p.get('selftext') or '')[:400]}")
              and ACCESSORY.search(f"{p.get('title', '')} {(p.get('selftext') or '')[:400]}")]
    print(f"stage2: {len(picked)} fit-question threads", flush=True)

    def fetch(p):
        out = THREADS / f"{p['id']}.json"
        if out.exists():
            return
        data = get("comment", {"link_id": p["id"], "size": 100})
        time.sleep(PAUSE_S)
        if data is not None:
            out.write_text(json.dumps({"post": p, "comments": data}, ensure_ascii=False))

    with ThreadPoolExecutor(2) as pool:
        list(pool.map(fetch, picked))


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    if "--show" in sys.argv:
        for d in DEVICES:
            print(d["id"], phrases(d))
        sys.exit()
    stages = [a for a in sys.argv[1:] if not a.startswith("-")] or ["1", "2"]
    if "1" in stages:
        stage1()
    if "2" in stages:
        stage2()
    print("PULLPUSH DONE", flush=True)
