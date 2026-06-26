"""
receipt_parser.py
-----------------
Parses raw OCR text from a supermarket receipt and extracts structured product lines.

Strategy:
  1. Load non_product_patterns from data/product_knowledge_fr.json.
  2. Filter every line against those compiled regexes.
  3. A product line MUST end with a trailing price.
  4. Handle AVOCAT HASS-style split lines: name on one line, "N X price total" on next.
  5. Never treat weight/volume suffixes (190G, 2KG, 1.5L) as quantities.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# ── Load knowledge base ────────────────────────────────────────────────────
_KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "product_knowledge_fr.json"

def _load_kb() -> dict:
    try:
        return json.loads(_KB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"non_product_patterns": []}

_KB = _load_kb()

# Pre-compile noise patterns from JSON
_NOISE_RE: List[re.Pattern] = [
    re.compile(p) for p in _KB.get("non_product_patterns", [])
]

# ── Core regexes ──────────────────────────────────────────────────────────

# Trailing price at end of line: optional € symbol, digits, comma/dot, 2-3 decimals
_TRAILING_PRICE_RE = re.compile(r"[\€\$\£]?\s*(\d{1,6}[.,]\d{2,3})\s*€?\s*$")

# "N X unit_price€ line_total" continuation line, e.g. "2 X 0.99€ 1.98"
_MULTI_LINE_RE = re.compile(
    r"^\s*(\d{1,3})\s*[xX×]\s*(\d+[.,]\d{2,3})\s*€?\s+(\d+[.,]\d{2,3})\s*€?\s*$"
)

# Weight/volume suffix — these are package sizes, NOT quantities
_SIZE_SUFFIX_RE = re.compile(
    r"(?<!\d)(\d+(?:[.,]\d+)?)\s*(G|KG|L|LT|LTS|ML|CL)\b", re.IGNORECASE
)

# Explicit quantity prefix: "3 x product", "3x product"
_QTY_PREFIX_RE = re.compile(r"^\s*(\d{1,3})\s*[xX×]\s+(?=[A-Za-zÀ-ÿ])")

# Standalone leading quantity: "3 PRODUCT NAME ..."
_QTY_LEADING_RE = re.compile(r"^\s*(\d{1,3})\s+(?=[A-Za-zÀ-ÿ])")


# ── Public API ────────────────────────────────────────────────────────────

def parse_receipt(raw_text: str) -> List[Dict]:
    """
    Returns list of dicts for probable product lines:
    {
        raw_line:   str,
        name_part:  str,
        quantity:   int,
        unit_price: float | None,
        line_total: float | None,
        size:       str | None,   # e.g. "190g", "1.5L"
    }
    """
    lines = [ln.strip() for ln in raw_text.splitlines()]
    results: List[Dict] = []
    pending_name: Optional[str] = None   # line without trailing price
    pending_raw: Optional[str] = None

    for line in lines:
        if _is_noise(line):
            # Blank/noise lines don't flush a pending name — the continuation
            # may still appear on the very next non-noise line (AVOCAT HASS case).
            continue

        # Check for "N X price total" continuation line
        m_multi = _MULTI_LINE_RE.match(line)
        if m_multi:
            if pending_name:
                qty = int(m_multi.group(1))
                unit_price = _to_float(m_multi.group(2))
                line_total = _to_float(m_multi.group(3))
                combined_raw = f"{pending_raw}  |  {line}"
                results.append(_make_item(combined_raw, pending_name, qty, unit_price, line_total, None))
                pending_name = None
                pending_raw = None
            # Whether or not we had a pending_name, this line is consumed — skip.
            continue

        # If we had a pending name but this line is NOT a continuation, flush pending
        if pending_name:
            results.append(_make_item(pending_raw, pending_name, 1, None, None, None))
            pending_name = None
            pending_raw = None

        has_price = bool(_TRAILING_PRICE_RE.search(line))

        if not has_price:
            # Could be the first part of a split item (AVOCAT HASS pattern)
            # Only keep as pending if it looks like a product name (has letters, not too short)
            clean = line.strip(" .,;:-")
            if len(clean) >= 3 and re.search(r"[A-Za-zÀ-ÿ]{2,}", clean):
                pending_name = clean
                pending_raw = line
            continue

        # Normal single-line product
        size = _extract_size(line)
        qty = _extract_quantity(line, size)
        unit_price = _extract_trailing_price(line)
        name_part = _clean_name(line, size)

        if not name_part:
            continue

        results.append(_make_item(line, name_part, qty, unit_price, unit_price, size))

    # Flush any remaining pending
    if pending_name:
        results.append(_make_item(pending_raw, pending_name, 1, None, None, None))

    return results


# ── Helpers ───────────────────────────────────────────────────────────────

def _is_noise(line: str) -> bool:
    for pattern in _NOISE_RE:
        if pattern.search(line):
            return True
    return False


def _extract_size(line: str) -> Optional[str]:
    """Returns the first weight/volume token found (e.g. '190g', '1.5L'), or None."""
    m = _SIZE_SUFFIX_RE.search(line)
    if m:
        return f"{m.group(1)}{m.group(2).upper()}"
    return None


def _extract_quantity(line: str, size: Optional[str]) -> int:
    """Extracts the unit count from the line, ignoring weight/volume digits."""
    # Remove size token so its leading digits don't confuse quantity parsing
    line_no_size = _SIZE_SUFFIX_RE.sub("", line) if size else line

    m = _QTY_PREFIX_RE.match(line_no_size)
    if m:
        return int(m.group(1))
    m = _QTY_LEADING_RE.match(line_no_size)
    if m:
        val = int(m.group(1))
        if 2 <= val <= 99:   # sanity: 1 is already the default; don't misfire on lone digits
            return val
    return 1


def _extract_trailing_price(line: str) -> Optional[float]:
    m = _TRAILING_PRICE_RE.search(line)
    if m:
        return _to_float(m.group(1))
    return None


def _clean_name(line: str, size: Optional[str]) -> str:
    """Strip price, size tokens, and quantity prefixes from the product line."""
    cleaned = line
    # Remove trailing price
    cleaned = _TRAILING_PRICE_RE.sub("", cleaned)
    # Remove size tokens (e.g. "190G", "1.5L")
    cleaned = _SIZE_SUFFIX_RE.sub("", cleaned)
    # Remove explicit leading quantity prefix ("3 x " / "3x ")
    cleaned = _QTY_PREFIX_RE.sub("", cleaned)
    # Collapse multiple spaces
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = cleaned.strip(" .,;:-|/\\")
    return cleaned.strip()


def _make_item(
    raw_line: str,
    name_part: str,
    quantity: int,
    unit_price: Optional[float],
    line_total: Optional[float],
    size: Optional[str],
) -> Dict:
    return {
        "raw_line": raw_line,
        "name_part": name_part,
        "quantity": quantity,
        "unit_price": unit_price,
        "line_total": line_total,
        "size": size,
    }


def _to_float(s: str) -> Optional[float]:
    try:
        return float(s.replace(",", "."))
    except (ValueError, AttributeError):
        return None
