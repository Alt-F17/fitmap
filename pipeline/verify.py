"""Second-opinion check: does each claim's quote actually support it?

A fresh model call re-reads every claim against its verbatim quote (+ context) and answers
supported / wrong_direction / wrong_verdict / wrong_device / not_a_report. build.py drops anything
not "supported" (or, for wrong_verdict, applies the corrected verdict).
Output: data/verdicts.jsonl keyed by claim key. Resumable.
"""
import concurrent.futures as cf
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DEVICES = {d["id"]: d["name"] for d in json.loads((DATA / "devices.json").read_text())}
DEVICES["universal"] = "universal add-on (not model-specific)"
BATCH = 30
WORKERS = 2


def key(c):
    return f"{c['sid']}|{c['accessory_for']}|{c['used_on']}|{c['category']}"


SCHEMA = {"type": "object", "required": ["results"], "properties": {"results": {"type": "array", "items": {
    "type": "object", "required": ["k", "label"],
    "properties": {
        "k": {"type": "string"},
        "label": {"type": "string", "enum": ["supported", "wrong_direction", "wrong_verdict",
                                             "wrong_device", "not_a_report"]},
        "corrected_verdict": {"type": "string", "enum": ["fits", "fits_with_caveat", "doesnt_fit"]},
    }}}}}

PROMPT = """You are auditing extracted claims about phone accessories. For each claim, decide whether
the QUOTE (read with its CONTEXT) supports the claim exactly as stated:
"an accessory made for <MADE FOR> was put on <USED ON>; result = <VERDICT>".

Labels:
- supported: the quote reports this (first- or second-hand), right direction, right phones, right result.
- wrong_direction: the quote is about the reverse direction (accessory for USED ON put on MADE FOR).
- wrong_verdict: right phones/direction but the result is different; give corrected_verdict.
  (e.g. "doesn't fit unless you cut it" => fits_with_caveat at best, or doesnt_fit).
- wrong_device: the quote is about other phone models than the ones named.
- not_a_report: a question, a guess with no basis, a joke, a listing/packaging claim, or unrelated.
Be strict: if the quote alone doesn't establish it, it's not supported.

CLAIMS:
{claims}"""


def run(batch):
    lines = []
    for c in batch:
        lines.append(json.dumps({
            "k": key(c), "MADE FOR": DEVICES.get(c["accessory_for"], c["accessory_for"]),
            "USED ON": DEVICES.get(c["used_on"], c["used_on"]), "category": c["category"],
            "VERDICT": c["verdict"], "QUOTE": c["quote"], "CONTEXT": c["context"][:200]},
            ensure_ascii=False))
    prompt = PROMPT.format(claims="\n".join(lines))
    for _ in range(3):
        try:
            r = subprocess.run(
                ["claude", "-p", "--model", "sonnet", "--tools", "", "--strict-mcp-config",
                 "--setting-sources", "", "--no-session-persistence", "--output-format", "json",
                 "--json-schema", json.dumps(SCHEMA)],
                input=prompt, capture_output=True, text=True, timeout=600, cwd="/tmp")
            out = json.loads(r.stdout)
            if out.get("is_error"):
                raise RuntimeError(out.get("result", "")[:200])
            return out["structured_output"]["results"]
        except Exception as e:
            print(f"  retry: {e}", flush=True)
    return None


def main():
    claims = [json.loads(l) for l in (DATA / "claims.jsonl").read_text().splitlines()]
    out_path = DATA / "verdicts.jsonl"
    done = set()
    if out_path.exists():
        done = {json.loads(l)["k"] for l in out_path.read_text().splitlines()}
    todo, seen = [], set()
    for c in claims:
        k = key(c)
        if k not in done and k not in seen:
            seen.add(k)
            todo.append(c)
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    print(f"{len(todo)} claims to verify in {len(batches)} batches", flush=True)
    with cf.ThreadPoolExecutor(WORKERS) as pool, out_path.open("a") as out:
        for n, res in enumerate(pool.map(run, batches), 1):
            if res is None:
                continue
            valid = {key(c) for c in batches[n - 1]}
            for r in res:
                if r["k"] in valid:
                    out.write(json.dumps(r) + "\n")
            out.flush()
            if n % 5 == 0:
                print(f"{n}/{len(batches)}", flush=True)
    labels = {}
    for l in out_path.read_text().splitlines():
        lab = json.loads(l)["label"]
        labels[lab] = labels.get(lab, 0) + 1
    print("VERIFY DONE", labels, flush=True)


if __name__ == "__main__":
    main()
