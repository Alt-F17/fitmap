# FitMap: phone accessory cross-compatibility, from real users

FitMap answers one question on the sales floor: **"Which accessories made for *other* phones fit
this customer's phone?"** For example: an A57 screen protector on an S25 FE, or a 17 Pro Max case on an
18 Pro Max (it fits, but the taller camera plateau sits less protected).

Every result comes from **user reports**: Reddit posts and comments, and Best Buy Canada and TUFF8
customer reviews. Manufacturer compatibility lists and "fits X / Y" packaging are deliberately **not**
used as evidence. Each result links to the quotes it's based on.

**Scope:** iPhone 15–18 (all variants), Google Pixel 8–11 (all except Fold), Samsung Galaxy S22–S26 / A-series 2022–2026,
Motorola moto g / edge 2023–2026, TCL 40 / 50 / 60 / NXTPAPER 70. Foldables and flip phones are out of scope.
**Brand lens:** AXS and TUFF8, plus all brands.

## Using it

- **Customer's phone:** type the phone (`s25fe`, `17 pro max`, `moto g 2025`, `A57`…) and you get
  accessories from other models that users say fit, grouped by type.
- **Accessory in hand:** pick the phone an accessory was made for and you get every other phone it
  reportedly fits. Useful for moving stock.
- **Grid:** a family × family heatmap per accessory type.
- **AXS / TUFF8 / All brands** switch at the top. **FR / EN** toggle. Works offline after the first visit.

Verdicts: ✓ fits · ! fits with a catch (camera cutout, corners, buttons…) · ✕ doesn't fit · ≈ mixed.
Confidence: *Strong* (3+ independent first-hand reports, no first-hand contradictions), *Likely*,
*Thin evidence*, *Conflicting*. "No reports" never means "doesn't fit".

## How the data is built

```
pipeline/devices.py   device catalog + aliases            -> data/devices.json
pipeline/harvest.py   Reddit via the Arctic Shift archive -> data/raw_v2, data/threads
pipeline/bestbuy.py   Best Buy Canada reviews             -> data/reviews_bestbuy.json
pipeline/judgeme.py   TUFF8 store reviews (Judge.me)      -> data/reviews_tuff8.json
pipeline/extract.py   prefilter + LLM claim extraction    -> data/claims.jsonl
pipeline/build.py     scoring + app bundle                -> app/data.json
```

`extract.py` runs Claude (headless `claude -p`, strict JSON schema). It rejects any claim whose quote
is not found **verbatim** in the source text, any claim about a phone outside the catalog, and any claim
that only repeats a retailer listing or packaging.

Store-tested results can be added to `data/store_tests.jsonl` (same fields as `claims.jsonl`,
`kind: "store_test"`). The app's "Report a fit" button produces that JSON line for the maintainer.

## Development

```
npm install
npm run serve      # http://localhost:4173
npm test           # Playwright e2e: phone + tablet, offline, axe accessibility
```

The app is static (`app/`): vanilla JS, no framework, no tracking, no backend.
