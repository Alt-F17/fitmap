"""Harvest Best Buy Canada customer reviews for phone accessories (public JSON API).

Writes data/reviews_bestbuy.json: one row per review with product name/brand/sku.
Resumable via data/bestbuy_cache/<sku>.json.
"""
import json
import pathlib
import re
import time
import urllib.parse

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "bestbuy_cache"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36", "Accept": "application/json"}
SEARCH = "https://www.bestbuy.ca/api/v2/json/search"
REVIEWS = "https://www.bestbuy.ca/api/reviews/v2/products/{sku}/reviews"
PAUSE_S = 1.2

QUERIES = [
    "tuff8", "axs armorglass", "axs case", "axs magsafe", "axs proshield",
    "screen protector iphone", "screen protector galaxy", "screen protector motorola",
    "screen protector tcl", "case iphone", "case galaxy", "case motorola", "case tcl",
    "case razr", "case galaxy z flip", "case galaxy z fold", "camera lens protector",
    "magsafe ring", "magnetic ring adapter", "privacy screen protector",
]
PHONE_WORDS = re.compile(r"iphone|galaxy|moto|razr|tcl|motorola|samsung|pixel", re.I)
ACCESSORY_WORDS = re.compile(r"case|protector|glass|lens|ring|magsafe|qi2|cover|folio|skin|"
                             r"wallet|grip", re.I)


def get_json(url, params):
    for attempt in range(5):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=45)
            if r.status_code == 200:
                return r.json()
            print(f"  {r.status_code} {url}", flush=True)
        except Exception as e:
            print(f"  error {e}", flush=True)
        time.sleep(10 * (attempt + 1))
    return None


def search_products(queries=QUERIES):
    products = {}
    for q in queries:
        for page in range(1, 11):
            d = get_json(SEARCH, {"query": q, "lang": "en-CA", "pageSize": 100, "page": page})
            time.sleep(PAUSE_S)
            if not d or not d.get("products"):
                break
            for p in d["products"]:
                name = p.get("name", "")
                if (p.get("customerRatingCount") or 0) > 0 and PHONE_WORDS.search(name) \
                        and ACCESSORY_WORDS.search(name):
                    products[p["sku"]] = {"sku": p["sku"], "name": name,
                                          "url": "https://www.bestbuy.ca" + (p.get("productUrl") or "")}
            if page >= (d.get("totalPages") or 1):
                break
        print(f"query '{q}': {len(products)} products with reviews so far", flush=True)
    return products


def fetch_reviews(sku):
    out = CACHE / f"{sku}.json"
    if out.exists():
        return json.loads(out.read_text())
    reviews, page = [], 1
    while True:
        d = get_json(REVIEWS.format(sku=sku), {"source": "all", "lang": "en-CA", "pageSize": 100,
                                               "page": page, "sortBy": "date"})
        time.sleep(PAUSE_S)
        if not d:
            return []  # not cached: retried next run
        reviews.extend(d.get("reviews") or [])
        if page >= (d.get("totalPages") or 1) or not d.get("reviews"):
            brand = d.get("brand", "")
            break
        page += 1
    data = {"brand": brand, "reviews": reviews}
    out.write_text(json.dumps(data, ensure_ascii=False))
    return data


def main(queries=None, out_name="reviews_bestbuy.json"):
    CACHE.mkdir(parents=True, exist_ok=True)
    products = search_products(queries or QUERIES)
    rows = []
    for i, (sku, p) in enumerate(sorted(products.items())):
        data = fetch_reviews(sku)
        if not data:
            continue
        for r in data["reviews"]:
            rows.append({"id": f"bb-{r['id']}", "sku": sku, "product": p["name"],
                         "brand": data["brand"], "url": p["url"], "rating": r.get("rating"),
                         "date": (r.get("submissionTime") or "")[:10], "title": r.get("title", ""),
                         "body": r.get("comment", ""),
                         "helpful": r.get("totalPositiveFeedbackCount") or 0})
        if i % 50 == 0:
            print(f"reviews: {i}/{len(products)} products, {len(rows)} reviews", flush=True)
    (ROOT / "data" / out_name).write_text(json.dumps(rows, ensure_ascii=False))
    print(f"BESTBUY DONE: {len(rows)} reviews from {len(products)} products", flush=True)


if __name__ == "__main__":
    import sys
    if "--pixel" in sys.argv:
        main(["case pixel", "screen protector pixel", "camera lens protector pixel",
              "magsafe case pixel", "tuff8 pixel", "axs pixel"], "reviews_bestbuy_pixel.json")
    else:
        main()
