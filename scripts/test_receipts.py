"""
scripts/test_receipts.py
------------------------
Diagnostic script: runs the full receipt pipeline on every image found in
data/test_receipts/ and prints structured output + raw OCR text.

Usage (from project root, using the venv):
    venv/Scripts/python.exe -X utf8 scripts/test_receipts.py
"""

import json
import os
import sys
from pathlib import Path

# ── Ensure project root is on the path ────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── Configure Tesseract before importing services ──────────────────────────
try:
    from decouple import config as env_config
    TESSERACT_CMD = env_config("TESSERACT_CMD", default=None)
except Exception:
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

try:
    import pytesseract
    if TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    print(f"[OK] pytesseract {pytesseract.__version__} — tesseract_cmd: {pytesseract.pytesseract.tesseract_cmd}")
    try:
        ver = pytesseract.get_tesseract_version()
        langs = pytesseract.get_languages()
        print(f"[OK] Tesseract {ver} — languages: {langs}")
    except Exception as e:
        print(f"[WARN] Could not query Tesseract: {e}")
except ImportError:
    print("[ERR] pytesseract not installed — run: pip install pytesseract")
    sys.exit(1)

# ── Import pipeline services ───────────────────────────────────────────────
from services.receipt.image_processor import preprocess_image
from services.receipt.ocr_service import extract_text, is_ocr_available
from services.receipt.receipt_parser import parse_receipt
from services.receipt.name_normalizer import normalize
from services.receipt.packaging_estimator import estimate_packaging

# ── Paths ──────────────────────────────────────────────────────────────────
RECEIPTS_DIR = PROJECT_ROOT / "data" / "test_receipts"
RAW_OCR_DIR  = RECEIPTS_DIR / "raw_ocr"
RAW_OCR_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".webp"}


def run_pipeline(image_path: Path) -> dict:
    image_bytes = image_path.read_bytes()

    processed = preprocess_image(image_bytes)
    raw_text = extract_text(processed)

    ocr_out = RAW_OCR_DIR / (image_path.stem + ".txt")
    ocr_out.write_text(raw_text, encoding="utf-8")

    parsed_lines = parse_receipt(raw_text)

    items = []
    for line_data in parsed_lines:
        norm = normalize(line_data["name_part"])
        estimate = estimate_packaging(norm["normalized_name"], norm.get("brand"))
        items.append({
            "raw_line":       line_data["raw_line"],
            "name_part":      line_data["name_part"],
            "normalized_name": norm["normalized_name"],
            "brand":          norm.get("brand"),
            "tokens_expanded": norm.get("tokens_expanded", []),
            "quantity":       line_data["quantity"],
            "unit_price":     line_data.get("unit_price"),
            "line_total":     line_data.get("line_total"),
            "size":           line_data.get("size"),
            "packaging_type": estimate["packaging_type"],
            "plastic_type":   estimate["plastic_type"],
            "weight_grams":   estimate["weight_grams"],
            "recyclable":     estimate["recyclable"],
            "waste_type":     estimate["waste_type"],
            "confidence":     estimate["confidence"],
            "needs_review":   estimate["needs_review"],
        })

    return {
        "image":        image_path.name,
        "ocr_file":     str(ocr_out),
        "raw_text":     raw_text,
        "parsed_count": len(parsed_lines),
        "items":        items,
    }


def main():
    print(f"\nOCR available: {is_ocr_available()}")
    print(f"Receipts dir:  {RECEIPTS_DIR}\n")
    print("=" * 70)

    images = sorted(
        p for p in RECEIPTS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not images:
        print(f"[ERR] No images found in {RECEIPTS_DIR}")
        sys.exit(1)

    for img_path in images:
        print(f"\n{'=' * 70}")
        print(f"RECEIPT: {img_path.name}")
        print("=" * 70)

        try:
            result = run_pipeline(img_path)
        except Exception as exc:
            print(f"[ERR] Pipeline failed for {img_path.name}: {exc}")
            import traceback; traceback.print_exc()
            continue

        # ── Raw OCR text ──────────────────────────────────────────────────
        print(f"\n--- RAW OCR TEXT (saved to {result['ocr_file']}) ---")
        for i, line in enumerate(result["raw_text"].splitlines(), 1):
            print(f"  {i:3d}| {line}")

        # ── Parsed product lines ──────────────────────────────────────────
        print(f"\n--- PARSED LINES ({result['parsed_count']} total) ---")
        for item in result["items"]:
            print(f"  raw:        {item['raw_line']!r}")
            print(f"  name_part:  {item['name_part']!r}")
            print(f"  normalized: {item['normalized_name']!r}  (brand={item['brand']!r})")
            print(f"  qty={item['quantity']}  unit_price={item['unit_price']}  total={item['line_total']}  size={item['size']!r}")
            if item["tokens_expanded"]:
                print(f"  expanded:   {item['tokens_expanded']}")
            print()

        # ── Classification output ─────────────────────────────────────────
        print(f"--- CLASSIFICATION OUTPUT ---")
        header = f"  {'normalized_name':<35} {'waste_type':<12} {'plastic':<8} {'grams':>6} {'conf':>5} {'NR':>2}"
        print(header)
        print("  " + "-" * (len(header) - 2))
        for item in result["items"]:
            flag = "Y" if item["needs_review"] else "N"
            wtype = item["waste_type"] or "?"
            plastic = str(item["plastic_type"] or "-")
            grams = str(item["weight_grams"] or "-")
            print(
                f"  {item['normalized_name']:<35} {wtype:<12} {plastic:<8} {grams:>6} "
                f"{item['confidence']:>5.2f} {flag:>2}"
            )

        # ── Problems ──────────────────────────────────────────────────────
        print(f"\n--- PROBLEMS ---")
        problems = []
        for item in result["items"]:
            if item["waste_type"] in ("inconnu", None):
                problems.append(f"  UNKNOWN: {item['normalized_name']!r}")
            elif item["needs_review"]:
                problems.append(f"  LOW CONF ({item['confidence']:.2f}): {item['normalized_name']!r}")
        if problems:
            for p in problems:
                print(p)
        else:
            print("  (none)")

    print(f"\n{'=' * 70}")
    print("Done. Raw OCR files saved to:", RAW_OCR_DIR)


if __name__ == "__main__":
    main()
