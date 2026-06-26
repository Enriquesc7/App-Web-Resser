"""
packaging_estimator.py
-----------------------
Category-based packaging and plastic type estimator.

Loads category rules from data/product_knowledge_fr.json.
Scoring:
  +0.5  if any category keyword appears in the normalized name
  +0.4  if the detected brand is in the category's brands list
  cap at 0.95

Best category wins. If max score < 0.4, returns waste_type="inconnu".
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

# ── Load knowledge base ────────────────────────────────────────────────────
_KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "product_knowledge_fr.json"

def _load_categories() -> Dict[str, dict]:
    try:
        kb = json.loads(_KB_PATH.read_text(encoding="utf-8"))
        return kb.get("categories", {})
    except Exception:
        return {}

_CATEGORIES = _load_categories()

_REVIEW_THRESHOLD = 0.65


# ── Public API ────────────────────────────────────────────────────────────

def estimate_packaging(normalized_name: str, brand: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns packaging estimate dict for a normalized product name.

    brand (optional): canonical brand string from name_normalizer.normalize().
    """
    name_lower = (normalized_name or "").lower()
    brand_lower = (brand or "").lower()

    best_category: Optional[str] = None
    best_score: float = 0.0

    for cat_name, cat in _CATEGORIES.items():
        score = 0.0

        # Keyword match
        for kw in cat.get("keywords", []):
            if kw.lower() in name_lower:
                score += 0.5
                break   # one keyword hit is enough

        # Brand match
        if brand_lower and any(b.lower() in brand_lower for b in cat.get("brands", [])):
            score += 0.4

        if score > best_score:
            best_score = score
            best_category = cat_name

    # Cap confidence
    confidence = min(best_score, 0.95)

    if best_category is None or confidence < 0.4:
        return _unknown(confidence)

    cat = _CATEGORIES[best_category]
    return {
        "packaging_type": cat.get("packaging_type", "inconnu"),
        "plastic_type": cat.get("plastic_type"),
        "weight_grams": float(cat.get("plastic_grams", 0)) or None,
        "recyclable": cat.get("recyclable"),
        "waste_type": cat.get("waste_type", "inconnu"),
        "confidence": confidence,
        "needs_review": confidence < _REVIEW_THRESHOLD,
        "source": "rule_based",
    }


def _unknown(confidence: float = 0.0) -> Dict[str, Any]:
    return {
        "packaging_type": "inconnu",
        "plastic_type": None,
        "weight_grams": None,
        "recyclable": None,
        "waste_type": "inconnu",
        "confidence": confidence,
        "needs_review": True,
        "source": "rule_based",
    }
