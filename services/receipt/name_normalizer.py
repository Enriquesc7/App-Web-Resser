"""
name_normalizer.py
------------------
Expands French supermarket receipt abbreviations into readable product names.

Loads abbreviation_expansions and brand_aliases from data/product_knowledge_fr.json
so the dictionary can be updated without changing any Python code.
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional

# ── Load knowledge base ────────────────────────────────────────────────────
_KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "product_knowledge_fr.json"

def _load_kb() -> dict:
    try:
        return json.loads(_KB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"abbreviation_expansions": {}, "brand_aliases": {}}

_KB = _load_kb()

# Upper-cased keys → expanded value
_ABBREVS: Dict[str, str] = {
    k.upper(): v for k, v in _KB.get("abbreviation_expansions", {}).items()
}

# Upper-cased keys → canonical brand name
_BRANDS: Dict[str, str] = {
    k.upper(): v for k, v in _KB.get("brand_aliases", {}).items()
}

# Sort brand keys longest-first so "OLD EL PASO" matches before "EL PASO"
_BRAND_KEYS = sorted(_BRANDS.keys(), key=len, reverse=True)

# Small French connectors that should NOT be title-cased
_CONNECTORS = {"de", "du", "des", "la", "le", "les", "et", "à", "au", "aux", "ou", "en", "un", "une"}


# ── Public API ────────────────────────────────────────────────────────────

def normalize_name(raw_name: str) -> str:
    """
    Thin wrapper for backwards-compatibility with managers/receipt.py.
    Returns the normalized_name string only.
    """
    result = normalize(raw_name)
    return result["normalized_name"]


def normalize(raw_name: str) -> Dict:
    """
    Full normalization. Returns:
    {
        original:         str,
        normalized_name:  str,
        brand:            str | None,
        tokens_expanded:  list[str],
    }
    """
    if not raw_name:
        return {"original": raw_name, "normalized_name": raw_name, "brand": None, "tokens_expanded": []}

    text = raw_name.strip()

    # 1. Strip leading noise characters
    text = re.sub(r"^[>|,\s]+", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # 2. Brand detection (case-insensitive, longest match first)
    detected_brand: Optional[str] = None
    text_upper = text.upper()
    for key in _BRAND_KEYS:
        if key in text_upper:
            detected_brand = _BRANDS[key]
            # Remove the brand token from the string (first occurrence)
            pat = re.compile(re.escape(key), re.IGNORECASE)
            text = pat.sub("", text, count=1).strip(" ,;-")
            text = re.sub(r"\s{2,}", " ", text).strip()
            text_upper = text.upper()
            break

    # 3. Split by spaces AND commas, expand each token
    raw_tokens = re.split(r"[\s,]+", text)
    expanded_tokens = []
    tokens_expanded_log = []

    for token in raw_tokens:
        if not token:
            continue
        token_up = token.upper()

        # Numeric values (sizes like "1.5", "190") — keep as-is
        if re.match(r"^\d+([.,]\d+)?$", token):
            expanded_tokens.append(token)
            continue

        # Strip trailing punctuation before abbreviation lookup
        # Handles OCR tokens like "VERGEO." "BACO." "THON." etc.
        token_clean = re.sub(r'[.,;:!?*]+$', '', token_up)

        if token_clean in _ABBREVS:
            expansion = _ABBREVS[token_clean]
            expanded_tokens.append(expansion)
            tokens_expanded_log.append(f"{token}→{expansion}")
        else:
            # Title-case, but keep connectors lower
            word_lower = token.lower()
            if word_lower in _CONNECTORS:
                expanded_tokens.append(word_lower)
            else:
                expanded_tokens.append(token.capitalize())

    normalized = " ".join(expanded_tokens).strip()

    # 4. Prepend the brand (if detected) at the front for readability
    if detected_brand:
        normalized = f"{detected_brand} {normalized}".strip()

    return {
        "original": raw_name,
        "normalized_name": normalized,
        "brand": detected_brand,
        "tokens_expanded": tokens_expanded_log,
    }
