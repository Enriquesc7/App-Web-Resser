# Project Context — App Web Resser

Web application focused on recycling and plastic packaging analysis. Users can scan product barcodes or supermarket receipts to estimate their plastic packaging consumption.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Frontend | HTML + CSS + vanilla JavaScript (no frameworks) |
| OCR | Tesseract 5.5.0 — `C:\Program Files\Tesseract-OCR\tesseract.exe` |
| Env vars | `.env` file |

**Constraints — do not change these:**
- Do not migrate to React, Vue or any frontend framework.
- Do not replace SQLAlchemy with another ORM.
- Pydantic version is **v1** (`pydantic==1.10.26`). Do not use v2 syntax.
- Preserve project structure unless a change is clearly necessary.

---

## Feature 1 — Barcode / product scanner (existing)

Allows users to scan a product barcode and get:
- Type of plastic in the packaging
- Approximate plastic weight
- Whether the packaging is recyclable
- Environmental guidance

This feature is complete. Do not modify it unless explicitly required.

---

## Feature 2 — Receipt scanner (implemented)

Users upload or photograph a supermarket receipt. The system extracts products and estimates the plastic packaging consumed.

### Pipeline (in order)

1. **Image preprocessing** — contrast, orientation, deskew, crop margins (`services/receipt/image_preprocessor.py`)
2. **OCR** — Tesseract with `fra` language; falls back to `eng` if French yield is poor (`services/receipt/ocr_engine.py`)
3. **Parsing** — `parse_receipt()` in `services/receipt/receipt_parser.py`
   - Reads lines one by one
   - Filters noise with `non_product_patterns` regex list from the knowledge base
   - Detects trailing price with `\d{1,6}[.,]\d{2,3}\s*$`
   - Lines with a price → flushed immediately as a product
   - Lines without a price → held as `pending_name` until the next line resolves them
   - Returns list of `{name_part, quantity, unit_price, line_total, size}`
4. **Normalization** — `normalize()` in `services/receipt/name_normalizer.py`
   - Detects brand via substring match against `brand_aliases` (longest key first)
   - Strips trailing punctuation from tokens before abbreviation lookup
   - Expands tokens using `abbreviation_expansions`
   - Returns `{normalized_name, brand, tokens_expanded}`
5. **Packaging estimation** — `estimate_packaging()` in `services/receipt/packaging_estimator.py`
   - Scores each category: +0.5 keyword match, +0.4 brand match, cap 0.95
   - `needs_review = True` when confidence < 0.65
   - Returns `{packaging_type, plastic_type, weight_grams, recyclable, waste_type, confidence, needs_review}`
6. **Persistence** — saves to `receipt_scans`, `receipt_items`, `packaging_estimates` tables
7. **Response** — structured JSON returned to frontend

### API endpoints

```
POST /receipt/upload           — upload image, run full pipeline, return results
GET  /receipt/scans            — last 20 scan summaries (must be defined BEFORE /{scan_id})
GET  /receipt/{scan_id}        — full detail for one scan
```

**Route order matters**: `/receipt/scans` must be registered before `/receipt/{scan_id}` in the router file, otherwise FastAPI will try to cast "scans" as an integer and return 422.

### Frontend

Single-page app at `/receipt` — three toggled views (upload → loading → results) with a persistent history section below.

- Template: `templates/users/receipt/receipt_upload.html`
- JS: `static/scripts/receipt_upload.js` — vanilla JS state machine, no jQuery
- CSS: classes appended at the end of `static/css/design_system.css`
- All UI text is in **French**

### Database models (`models/receipt.py`)

| Table | Purpose |
|-------|---------|
| `receipt_scans` | One row per uploaded image (image_path, raw_text, status, created_at) |
| `receipt_items` | One row per detected product line (name_part, normalized_name, quantity, price) |
| `packaging_estimates` | One row per item (packaging_type, plastic_type, weight_grams, recyclable, waste_type, confidence) |

---

## Knowledge base — `data/product_knowledge_fr.json`

Loaded **at import time** by both `name_normalizer.py` and `packaging_estimator.py`. A server restart is needed to pick up changes.

### Structure

```json
{
  "abbreviation_expansions": { "BLE": "Blé", "FARINE": "Farine", ... },
  "brand_aliases":           { "AUCHAN": "Auchan", "AUCHANE": "Auchan", ... },
  "categories": {
    "sauce_jar": {
      "keywords": ["pesto", "bocal", ...],
      "brands":   ["barilla", ...],
      "packaging_type": "bocal verre",
      "plastic_type": null,
      "plastic_grams": 0,
      "recyclable": true,
      "waste_type": "verre"
    },
    ...
  },
  "non_product_patterns": ["(?i)^Total\\b", "^\\d{14,}", ...]
}
```

### Scoring logic

- Each category is scored independently: keyword match → +0.5, brand match → +0.4
- Only one keyword hit per category is counted (first match wins)
- Brand match uses `if brand_lower in category_brands` (exact brand string, not substring)
- Highest-scoring category wins; ties go to the category defined first in the JSON
- Confidence cap: 0.95

### Waste types

| Value | Meaning |
|-------|---------|
| `plastique` | Plastic packaging |
| `verre` | Glass jar/bottle |
| `metal` | Metal can/tin |
| `carton` | Cardboard (Tetra Pak, egg box) |
| `papier` | Paper bag (flour, sugar) |
| `mixte` | Mixed (cardboard + plastic inner bag, e.g. cereals) |
| `aucun` | No packaging — loose produce sold by weight |
| `inconnu` | Unknown / confidence too low |

### Categories (17 total)

`sauce_jar`, `dairy_cheese_vacuum`, `dairy_fresh_pot`, `dairy_milk_carton`, `cereal_box`, `produce_loose`, `salad_bag`, `bakery_bag`, `meat_tray`, `pasta_bag`, `beverage_bottle`, `metal_can`, `paper_hygiene`, `egg_carton`, `flour_paper_bag`, `frozen_food`, `ice_cream`

### Brand detection notes

- Brand aliases use **substring match** (`if key in text_upper`), so OCR prefix artifacts are handled automatically: `SAUCHAN`, `TAUCHAN`, `FAUCHAN` all contain `AUCHAN` as substring → Auchan detected.
- Keys are sorted longest-first so `AUCHANE` (7 chars) is checked before `AUCHAN` (6 chars).
- Common OCR variants already in the file: `AUCHANE`, `SAUCHEN`, `BEGHIN SAŸ`, `FER.`, `>FER`.

### Abbreviation expansion notes

- Tokens have trailing punctuation stripped before lookup: `VERGEO.` → looks up `VERGEO` → expands to `Vergeoise`
- French connectors (`de`, `du`, `la`, etc.) are kept lowercase
- Numeric tokens (e.g. `1.5`, `500`) are passed through as-is

### non_product_patterns

Regex list applied to each raw line before it enters the parser. Matches → line is discarded. Patterns cover:
- Store headers and addresses
- Payment / card lines
- VAT / total lines
- Loyalty program sections (Waaon / Auchan)
- Date and time lines
- Short or all-numeric lines

---

## Design system

- Main file: `static/css/design_system.css` — loaded **last** in `base_user.html` so it wins cascade conflicts
- Phone-frame layout: `#container` max-width 430px, `#section` overflow-y auto
- CSS tokens: `--resser-*` (greens), `--neutral-*`, `--amber`, `--blue`, `--red`
- Do not add new JS libraries; use vanilla JS

---

## Test receipts

Located in `data/test_receipts/` (images) and `data/test_receipts/raw_ocr/` (pre-extracted text files).

| File | Store | Notes |
|------|-------|-------|
| Prueba_1 | E.Leclerc | 6 products, clean OCR, simple |
| Prueba_2 | E.Leclerc | 7 products, produce + meat + wrap |
| Prueba_3 | E.Leclerc | Same products as Prueba_2, different scan |
| Prueba_4 | Auchan | ~66 products, heavy OCR noise, loyalty section |

To run the pipeline in-process without the server (useful for testing knowledge base changes):

```python
import sys; sys.path.insert(0, '.')
from services.receipt.name_normalizer import normalize
from services.receipt.packaging_estimator import estimate_packaging
from services.receipt.receipt_parser import parse_receipt

raw = open('data/test_receipts/raw_ocr/Prueba_4.txt', encoding='utf-8').read()
for item in parse_receipt(raw):
    result = normalize(item['name_part'])
    est = estimate_packaging(result['normalized_name'], result['brand'])
    print(result['normalized_name'], est['waste_type'], est['confidence'])
```

**Note**: `importlib.reload()` on `name_normalizer` and `packaging_estimator` does reload the JSON within a running Python session, so you can test changes without restarting the server during development.

---

## Development rules

**Before coding:**
- Read relevant existing modules first.
- Do not modify existing functionality (barcode scanner, auth, admin) unless required.
- Avoid large rewrites; prefer targeted edits.
- Propose database table changes before creating them.

**Backend:**
- Use FastAPI routers.
- Use SQLAlchemy models.
- Pydantic v1 syntax only (`class Config: orm_mode = True`, not `model_config`).
- Keep OCR, parsing, normalization, and estimation as separate service modules.

**Database:**
- No destructive migrations.
- Prefer additive changes.

**Frontend:**
- Extend `base_user.html` via `{% extends %}`.
- Add CSS to `design_system.css` (at the end of the file).
- Vanilla JS only — no new libraries.
- All user-facing text in **French**.
- Test on mobile viewport (430px width).

---

## Pending / next steps

- [ ] Improve OCR quality for crumpled or low-contrast receipts
- [ ] Handle quantity > 1 in the parser (e.g. `3 × Pepsi 2L`)
- [ ] Add more supermarket chains (currently well-tested: E.Leclerc, Auchan)
- [ ] External product lookup via Open Food Facts when confidence is low
- [ ] Barcode integration in receipt flow
- [ ] Expand knowledge base with more product categories (household products, beverages with deposit, etc.)
