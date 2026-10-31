"""Harvest Reddit posts/comments about accessory fit from the Arctic Shift archive.

Resumable: each (kind, subreddit, query) result is cached in data/raw/. Re-running skips
finished jobs. Stage 2 pulls every comment of threads whose title asks a fit question.
"""
import json
import pathlib
import re
import sys
import time

import requests

from devices import SUBREDDITS

API = "https://arctic-shift.photon-reddit.com/api"
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_v2"
THREADS = ROOT / "data" / "threads"
SINCE_TS = 1640995200  # 2022-01-01 UTC
PAGE_LIMIT = 100
MAX_PAGES = 8
PAUSE_S = 6
UA = {"User-Agent": "accessory-xref/0.1 (research; contact via github Alt-F17)"}

# Single words only: multi-word (AND) full-text queries time out on larger subreddits.
# The search is stemmed, so "fit" also matches fits/fitted/fitting.
COMMENT_QUERIES = ["fit", "compatible", "interchangeable", "dimensions"]
BRAND_QUERIES = ["tuff8", "axs", "armorglass"]
FR_QUERIES = ["étui", "protecteur"]
TITLE_QUERIES = ["fit", "compatible", "interchangeable"]

COMMENT_FIELDS = "id,body,subreddit,created_utc,score,link_id"
POST_FIELDS = "id,title,selftext,subreddit,created_utc,score,num_comments"

FIT_TITLE = re.compile(
    r"\b(fit|fits|fitting|compatible|compatibility|work with|works with|interchangeable|"
    r"same (size|dimensions)|use .* case|case .* on)\b", re.I)
ACCESSORY = re.compile(r"\b(case|cases|protector|glass|magsafe|qi2|ring|lens|cover|skin|film|"
                       r"étui|protecteur)\b", re.I)


class SlowQuery(Exception):
    """The archive's full-text search gave up (rare word in a big subreddit)."""


def get(path, params, tries=4):
    """Return a page of results, [] for a query the archive can't answer in time, None on failure."""
    delay, timeouts = 20, 0
    for _ in range(tries):
        try:
            r = requests.get(f"{API}/{path}", params=params, headers=UA, timeout=90)
            if r.status_code == 429:
                raise RuntimeError("429")
            d = r.json()
            err = d.get("error") or ""
            if "Timeout" in err:
                timeouts += 1
                if timeouts >= 2:
                    raise SlowQuery(err)
                time.sleep(30)
                continue
            if err:
                raise RuntimeError(err)
            return d.get("data") or []
        except SlowQuery:
            print(f"  skip slow query {path} {params.get('subreddit')} {params}", flush=True)
            return None  # not cached: a later pass retries it
        except Exception as e:  # network, rate limit: back off and retry
            print(f"  retry {path} {params.get('subreddit') or params.get('link_id')}: {e}",
                  flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 120)
    print(f"  GAVE UP {path} {params}", flush=True)
    return None


def harvest_query(kind, sub, query):
    safe = re.sub(r"[^a-z0-9]+", "_", f"{kind}_{sub}_{query}".lower())
    out = RAW / f"{safe}.json"
    if out.exists():
        return
    path, key, fields = (("comments/search", "body", COMMENT_FIELDS) if kind == "c"
                         else ("posts/search", "title", POST_FIELDS))
    items, before = [], None
    for _ in range(MAX_PAGES):
        params = {"subreddit": sub, key: query, "limit": PAGE_LIMIT, "fields": fields}
        if before:
            params["before"] = before
        page = get(path, params)
        time.sleep(PAUSE_S)
        if page is None:
            return  # leave uncached so a rerun retries it
        items.extend(page)
        if len(page) < PAGE_LIMIT or int(page[-1]["created_utc"]) < SINCE_TS:
            break
        before = int(page[-1]["created_utc"])
    out.write_text(json.dumps(items, ensure_ascii=False))
    print(f"{kind} r/{sub} '{query}': {len(items)}", flush=True)


# Huge subreddits: rare words time out there, so only the common queries run.
BIG_SUBS = {"iphone", "samsung", "samsunggalaxy", "motorola"}
CARRIER_SUBS = {"videotron", "telus", "bell", "Rogers"}


def harvest_sub(sub):
    if sub in BIG_SUBS:
        titles, queries = ["fit", "compatible"], ["fit"]
    else:
        titles, queries = TITLE_QUERIES, COMMENT_QUERIES + BRAND_QUERIES
    if sub in CARRIER_SUBS:
        queries = queries + FR_QUERIES
    for q in titles:
        harvest_query("p", sub, q)
    for q in queries:
        harvest_query("c", sub, q)


def stage1():
    from concurrent.futures import ThreadPoolExecutor
    subs = sorted({s for v in SUBREDDITS.values() for s in v})
    with ThreadPoolExecutor(1) as pool:
        list(pool.map(harvest_sub, subs))


def stage2():
    """Fetch full comment trees for fit-question threads."""
    THREADS.mkdir(exist_ok=True)
    seen = set()
    for f in sorted(RAW.glob("p_*.json")):
        for p in json.loads(f.read_text()):
            text = f"{p.get('title', '')} {p.get('selftext', '')[:400]}"
            if p["id"] in seen or not (FIT_TITLE.search(text) and ACCESSORY.search(text)):
                continue
            if (p.get("num_comments") or 0) == 0:
                continue
            seen.add(p["id"])
            out = THREADS / f"{p['id']}.json"
            if out.exists():
                continue
            data = get("comments/search", {"link_id": p["id"], "limit": 100,
                                           "fields": COMMENT_FIELDS})
            time.sleep(PAUSE_S)
            if data is not None:
                out.write_text(json.dumps({"post": p, "comments": data}, ensure_ascii=False))
    print(f"stage2: {len(seen)} fit-question threads", flush=True)


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    stages = sys.argv[1:] or ["1", "2"]
    if "1" in stages:
        stage1()
    if "2" in stages:
        stage2()
    print("HARVEST DONE", flush=True)
