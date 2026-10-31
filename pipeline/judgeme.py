"""Fetch all public Judge.me reviews for a Shopify store (TUFF8 uses Judge.me).

Usage: python3 judgeme.py <shop>.myshopify.com <brand> <store base url>
Writes data/reviews_<brand>.json
"""
import html
import json
import pathlib
import re
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://judge.me/reviews/all_reviews_js_based"
REV = re.compile(r"<div class='jdgm-rev jdgm-divider-top'(.*?)(?=<div class='jdgm-rev jdgm-divider-top'|\Z)",
                 re.S)


def text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment)).strip()


def parse(block, base):
    def grab(pattern):
        m = re.search(pattern, block, re.S)
        return m.group(1) if m else ""
    return {
        "id": grab(r"data-review-id='([^']+)'"),
        "rating": int(grab(r"data-score='(\d)'") or 0),
        "date": grab(r"data-content='([^']+)'")[:10],
        "product": text(grab(r"class='jdgm-rev__prod-link'>(.*?)</a>")),
        "url": base + grab(r"<a href='(/products/[^']+)'"),
        "title": text(grab(r"<b class='jdgm-rev__title'>(.*?)</b>")),
        "body": text(grab(r"<div class='jdgm-rev__body'>(.*?)</div>")),
        "helpful": int(grab(r"data-thumb-up-count='(\d+)'") or 0),
    }


def main(shop, brand, base):
    out, page = [], 1
    while True:
        r = requests.get(URL, params={"shop_domain": shop, "platform": "shopify", "page": page,
                                      "per_page": 100}, headers={"User-Agent": "Mozilla/5.0"},
                         timeout=60)
        r.raise_for_status()
        blocks = REV.findall(r.json()["html"])
        if not blocks:
            break
        out.extend(parse(b, base) for b in blocks)
        print(f"page {page}: {len(blocks)}", flush=True)
        page += 1
        time.sleep(1.5)
    path = ROOT / "data" / f"reviews_{brand}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=0))
    print(f"{len(out)} reviews -> {path}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
