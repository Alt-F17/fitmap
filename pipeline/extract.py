"""Turn harvested posts/reviews into structured, quote-verified fit claims.

1. collect: unify Reddit comments/posts/threads + retailer reviews into snippets
2. prefilter: keep snippets that mention an accessory and a cross-device signal
3. llm: batch snippets through headless `claude -p` with a strict JSON schema
4. verify: drop any claim whose quote is not verbatim in the snippet
Output: data/claims.jsonl (append-only, resumable by batch id)
"""
import concurrent.futures as cf
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DEVICES = json.loads((DATA / "devices.json").read_text())
DEVICE_IDS = {d["id"] for d in DEVICES}
BATCH_SIZE = 25
MAX_CHARS = 1400
WORKERS = 2  # theta has ~1.2 GB free; each CLI run is ~240 MB
MODEL = "sonnet"

CATEGORIES = ["screen_protector", "privacy_protector", "camera_lens_protector", "case",
              "folio_wallet_case", "magsafe_ring", "magnetic_accessory", "other"]
CAVEATS = ["camera_cutout_larger", "camera_exposed", "camera_lip_too_low", "button_misaligned",
           "port_misaligned", "speaker_misaligned", "corners_lift", "edges_dont_cover",
           "sensor_or_fingerprint_issue", "selfie_cam_cutout_off", "loose_fit", "tight_fit",
           "slider_or_key_hole_missing", "magnet_weak_or_offset", "case_conflicts_with_protector",
           "s_pen_or_stylus_issue", "hinge_issue", "other"]

ACCESSORY = re.compile(r"\b(case|cases|protector|protectors|tempered|glass|magsafe|qi2|ring|"
                       r"lens|cover|skin|film|folio|wallet|popsocket|bumper|étui|protecteur)\b",
                       re.I)
FIT = re.compile(r"\b(fit|fits|fitted|fitting|compatible|interchangeabl\w*|same (size|dimensions)|"
                 r"works? (on|with)|used? (an?|my|the)|cutout|lines? up|doesn'?t fit|too (big|small))\b",
                 re.I)
DEVICE_PATTERNS = [
    r"\biphone\s?1[5-8]\s?(pro\s?max|pro|plus|e)?\b", r"\b1[5-8]\s?(pro\s?max|pm|pro|plus)\b",
    r"\b1[67]e\b", r"\biphone\s?(air|duo|fold)\b",
    r"\bs2[2-6]\s?(\+|plus|ultra|fe|edge|u)?\b", r"\ba[1-5][3-7]\b",
    r"\b(z\s?)?(flip|fold)\s?[4-8]\s?(fe|ultra)?\b",
    r"\b(moto\s?)?g\s?(5g|power|stylus|play)?\s?(5g)?\s?\(?(20)?2[3-6]\)?",
    r"\b(g\s?)?(power|stylus|play)\s?(5g)?\s?\(?(20)?2[3-6]\b",
    r"\brazr\s?(\+|plus|ultra|fold)?\s?\(?(20)?2[3-6]?\)?", r"\brazr\s?[4-7]0\s?(ultra|plus)?\b",
    r"\bedge\s?\+?\s?(plus)?\s?\(?(20)?2[3-6]\)?", r"\bedge\s?[4-6]0\b",
    r"\b(tcl\s?)?[4-7]0\s?(xl|xe|se|le|pro|r|nxtpaper|ultra)\b", r"\bnxtpaper\s?[5-7]0\b",
]
DEVICE_RE = re.compile("|".join(f"(?:{p})" for p in DEVICE_PATTERNS), re.I)


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def mentions(text):
    return {norm(m.group(0)).replace("(", "").replace(")", "") for m in DEVICE_RE.finditer(text)}


# ---------- 1. collect ----------
def collect():
    snippets = {}

    def add(sid, kind, url, date, score, context, text):
        text = (text or "").strip()
        if len(text) < 25 or text in ("[deleted]", "[removed]"):
            return
        snippets[sid] = {"sid": sid, "kind": kind, "url": url, "date": date, "score": score,
                         "context": context, "text": text[:MAX_CHARS]}

    def date_of(ts):
        import datetime
        return datetime.datetime.fromtimestamp(int(ts), datetime.UTC).strftime("%Y-%m-%d")

    titles = {}
    post_files = [*(DATA / "raw_v2").glob("p_*.json"), *(DATA / "raw_pp").glob("s_*.json")]
    comment_files = [*(DATA / "raw_v2").glob("c_*.json"), *(DATA / "raw_pp").glob("c_*.json")]
    for f in post_files:
        for p in json.loads(f.read_text()):
            titles[p["id"]] = p.get("title", "")
            add(f"rp-{p['id']}", "reddit_post", f"https://www.reddit.com/comments/{p['id']}/",
                date_of(p["created_utc"]), p.get("score", 0), f"r/{p['subreddit']}",
                f"{p.get('title', '')}\n{p.get('selftext') or ''}")
    thread_comments = []
    for f in (DATA / "threads").glob("*.json"):
        t = json.loads(f.read_text())
        p = t["post"]
        titles[p["id"]] = p.get("title", "")
        thread_comments.extend(t["comments"])
        add(f"rp-{p['id']}", "reddit_post", f"https://www.reddit.com/comments/{p['id']}/",
            date_of(p["created_utc"]), p.get("score", 0), f"r/{p.get('subreddit', '')}",
            f"{p.get('title', '')}\n{p.get('selftext') or ''}")
    for f in (DATA / "ff").glob("results_*.jsonl"):
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "reddit.com" in r.get("url", "") and r.get("description"):
                sid = "rx-" + hashlib.sha1(r["url"].encode()).hexdigest()[:12]
                add(sid, "reddit_excerpt", r["url"], "", 0, f"reddit · {r.get('title', '')[:160]}",
                    r["description"])
    for f in comment_files:
        thread_comments.extend(json.loads(f.read_text()))
    for c in thread_comments:
        link = (c.get("link_id") or "")[3:]
        ctx = f"r/{c.get('subreddit', '')}"
        if titles.get(link):
            ctx += f" · thread: {titles[link][:160]}"
        add(f"rc-{c['id']}", "reddit_comment",
            f"https://www.reddit.com/comments/{link}/_/{c['id']}/", date_of(c["created_utc"]),
            c.get("score", 0), ctx, c.get("body"))
    for src in ("bestbuy", "tuff8"):
        path = DATA / f"reviews_{src}.json"
        if not path.exists():
            continue
        for r in json.loads(path.read_text()):
            brand = r.get("brand") or ("TUFF8" if src == "tuff8" else "")
            add(f"rv-{src}-{r['id']}", f"review_{src}", r["url"], r.get("date", ""),
                r.get("helpful", 0), f"{src} review of: {brand} {r['product']}".strip(),
                f"{r.get('title', '')}\n{r.get('body', '')}")
    return snippets


# ---------- 2. prefilter ----------
def keep(s):
    text, ctx = s["text"], s["context"]
    if not ACCESSORY.search(text) and not ACCESSORY.search(ctx):
        return False
    in_text = mentions(text)
    all_devices = in_text | mentions(ctx)
    if s["kind"].startswith("review"):
        # a review is only interesting if it names a phone other than the product's label
        return bool(in_text - mentions(ctx)) or bool(re.search(r"\b(magsafe|qi2|ring)\b", ctx, re.I)
                                                    and in_text)
    if re.search(r"\b(magsafe|qi2)\b", text, re.I) and re.search(r"\b(ring|sticker|plate)\b", text, re.I) \
            and all_devices:
        return True
    return bool(FIT.search(text)) and len(all_devices) >= 2 or len(in_text) >= 2 and bool(FIT.search(text))


# ---------- 3. llm ----------
CATALOG = "\n".join(f"{d['id']}: {d['name']}" for d in DEVICES)
SCHEMA = {
    "type": "object", "required": ["claims"],
    "properties": {"claims": {"type": "array", "items": {
        "type": "object",
        "required": ["sid", "accessory_for", "used_on", "category", "verdict", "evidence",
                     "caveats", "brand", "quote", "note_en", "note_fr"],
        "properties": {
            "sid": {"type": "string"},
            "accessory_for": {"type": "string", "description": "device id the accessory was MADE/labelled for, or 'universal'"},
            "used_on": {"type": "string", "description": "device id it was actually put on"},
            "category": {"type": "string", "enum": CATEGORIES},
            "verdict": {"type": "string", "enum": ["fits", "fits_with_caveat", "doesnt_fit"]},
            "evidence": {"type": "string", "enum": ["firsthand", "secondhand"]},
            "caveats": {"type": "array", "items": {"type": "string", "enum": CAVEATS}},
            "brand": {"type": "string", "description": "accessory brand as written (AXS, TUFF8, Spigen, ...) or 'unknown'"},
            "product": {"type": "string"},
            "quote": {"type": "string", "description": "verbatim substring of the snippet text, <=300 chars"},
            "note_en": {"type": "string", "description": "<=90 chars, practical note for a store rep"},
            "note_fr": {"type": "string", "description": "same note in Quebec French"},
        }}}},
}
PROMPT = """You extract phone-accessory cross-compatibility claims from user posts and reviews.

DEVICE CATALOG (use ONLY these ids):
{catalog}

For each snippet, output zero or more claims. A claim = a user reporting that an accessory made for
phone A was put on phone B (A != B), with a result. Rules:
- accessory_for = the phone the accessory was made/labelled for; used_on = the phone it was put on.
  Direction matters: "my S24 protector on my new S25" => accessory_for=s24, used_on=s25.
- Universal add-ons (MagSafe/Qi2 rings or stickers, magnetic wallets/mounts, grips) used on a phone:
  accessory_for="universal", used_on=<phone>; put placement tips in note_en/note_fr.
- Include negative results (doesnt_fit) and partial results (fits_with_caveat + caveat tags).
- evidence=firsthand only if the author did it themselves (or an in-store test); "should fit",
  "I heard", "people say" => secondhand. Skip pure questions with no answer.
- SKIP claims that only repeat a manufacturer/retailer listing or packaging ("box says fits S24/S25",
  "Amazon says compatible"). Only user experience counts.
- SKIP if either phone is not in the catalog or you cannot tell which model is meant (e.g. "my 15"
  without context). Use thread/subreddit/product context to resolve "my phone".
- quote MUST be copied exactly (verbatim, same characters) from the snippet text, max 300 chars.
- Same phone on both sides is NOT a claim (a case for the S25 fitting the S25 is not interesting).
Return {{"claims": []}} when nothing qualifies — most snippets have nothing.

SNIPPETS:
{snippets}"""


def run_batch(batch_id, batch):
    body = "\n\n".join(f"<snippet sid=\"{s['sid']}\" context=\"{s['context']}\">\n{s['text']}\n</snippet>"
                       for s in batch)
    prompt = PROMPT.format(catalog=CATALOG, snippets=body)
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["claude", "-p", "--model", MODEL, "--tools", "", "--strict-mcp-config",
                 "--setting-sources", "", "--no-session-persistence", "--output-format", "json",
                 "--json-schema", json.dumps(SCHEMA)],
                input=prompt, capture_output=True, text=True, timeout=600, cwd="/tmp")
            out = json.loads(r.stdout)
            if out.get("is_error"):
                raise RuntimeError(out.get("result", "")[:200])
            return out["structured_output"]["claims"]
        except Exception as e:
            print(f"  batch {batch_id} attempt {attempt}: {e}", flush=True)
    return None


# ---------- 4. verify ----------
def squash(s):
    return re.sub(r"[\W_]+", "", s.lower())


def verify(claim, snippet):
    if claim["accessory_for"] not in DEVICE_IDS | {"universal"} or claim["used_on"] not in DEVICE_IDS:
        return "unknown_device"
    if claim["accessory_for"] == claim["used_on"]:
        return "same_device"
    q = squash(claim["quote"])
    if len(q) < 12 or q not in squash(snippet["text"]):
        return "quote_not_found"
    return None


def main():
    snippets = collect()
    kept = [s for s in snippets.values() if keep(s)]
    kept.sort(key=lambda s: s["sid"])
    print(f"collected {len(snippets)} snippets, {len(kept)} pass prefilter", flush=True)
    if "--dry" in sys.argv:
        for s in kept[:15]:
            print("---", s["context"], "|", s["text"][:200].replace("\n", " "))
        return
    out_path = DATA / "claims.jsonl"
    done_path = DATA / "snippets_done.txt"
    done = set(done_path.read_text().split()) if done_path.exists() else set()
    todo = [s for s in kept if s["sid"] not in done]
    limit = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--limit=")), None)
    todo = todo[:limit] if limit else todo
    batches = [(f"b{i // BATCH_SIZE}", todo[i:i + BATCH_SIZE]) for i in range(0, len(todo), BATCH_SIZE)]
    print(f"{len(todo)} new snippets -> {len(batches)} batches", flush=True)
    stats = {"ok": 0}
    with cf.ThreadPoolExecutor(WORKERS) as pool, out_path.open("a") as out, done_path.open("a") as dn:
        futures = {pool.submit(run_batch, bid, b): (bid, b) for bid, b in batches}
        for n, fut in enumerate(cf.as_completed(futures), 1):
            bid, b = futures[fut]
            claims = fut.result()
            if claims is None:
                continue
            by_sid = {s["sid"]: s for s in b}
            for c in claims:
                s = by_sid.get(c.get("sid"))
                reason = "bad_sid" if s is None else verify(c, s)
                if reason:
                    stats[reason] = stats.get(reason, 0) + 1
                    continue
                c.update({k: s[k] for k in ("kind", "url", "date", "score", "context")})
                out.write(json.dumps(c, ensure_ascii=False) + "\n")
                stats["ok"] += 1
            out.flush()
            dn.write("".join(s["sid"] + "\n" for s in b))
            dn.flush()
            if n % 10 == 0:
                print(f"{n}/{len(batches)} batches · {stats}", flush=True)
    print(f"EXTRACT DONE {stats}", flush=True)


if __name__ == "__main__":
    main()
