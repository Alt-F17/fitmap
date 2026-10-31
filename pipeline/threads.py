"""Fetch full Reddit threads for post links found by web search (data/ff/results_*.jsonl).

Lookups by id are cheap on the Arctic Shift archive (no full-text scan), so this is fast.
Writes data/threads/<post id>.json in the same shape harvest.py uses.
"""
import json
import pathlib
import re
import time

from harvest import COMMENT_FIELDS, POST_FIELDS, get

ROOT = pathlib.Path(__file__).resolve().parent.parent
THREADS = ROOT / "data" / "threads"
POST_ID = re.compile(r"reddit\.com/r/[^/]+/comments/([a-z0-9]+)", re.I)


def post_ids():
    ids = {}
    for f in (ROOT / "data" / "ff").glob("results_*.jsonl"):
        for line in f.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            m = POST_ID.search(row.get("url", ""))
            if m:
                ids.setdefault(m.group(1).lower(), row)
    return ids


def main():
    THREADS.mkdir(parents=True, exist_ok=True)
    ids = [i for i in post_ids() if not (THREADS / f"{i}.json").exists()]
    print(f"{len(ids)} new threads to fetch", flush=True)
    posts = {}
    for i in range(0, len(ids), 50):
        batch = get("posts/ids", {"ids": ",".join(ids[i:i + 50]), "fields": POST_FIELDS}) or []
        posts.update({p["id"]: p for p in batch})
        time.sleep(2)
    for n, pid in enumerate(ids, 1):
        post = posts.get(pid)
        if not post:
            continue
        comments = get("comments/search", {"link_id": pid, "limit": 100, "fields": COMMENT_FIELDS})
        time.sleep(2)
        if comments is None:
            continue
        (THREADS / f"{pid}.json").write_text(json.dumps({"post": post, "comments": comments},
                                                        ensure_ascii=False))
        if n % 50 == 0:
            print(f"{n}/{len(ids)}", flush=True)
    print("THREADS DONE", flush=True)


if __name__ == "__main__":
    main()
