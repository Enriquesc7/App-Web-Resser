"""
co2_estimator.py
-----------------
CO2-per-kg lookup by waste_type.

Loads factors from data/co2_factors_fr.json.
"""

import json
from pathlib import Path
from typing import Optional

# ── Load knowledge base ────────────────────────────────────────────────────
_KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "co2_factors_fr.json"


def _load_waste_types() -> dict:
    try:
        kb = json.loads(_KB_PATH.read_text(encoding="utf-8"))
        return kb.get("waste_types", {})
    except Exception:
        return {}


_WASTE_TYPES = _load_waste_types()


# ── Public API ────────────────────────────────────────────────────────────

def get_co2_factor(waste_type: str) -> Optional[float]:
    """Returns kgCO2e per kg of the given waste_type, or None if unknown/not classified."""
    entry = _WASTE_TYPES.get(waste_type)
    if not entry:
        return None
    return entry.get("co2_kg_per_kg")


def get_waste_label(waste_type: str) -> str:
    """Returns the French display label for the given waste_type."""
    entry = _WASTE_TYPES.get(waste_type)
    if not entry:
        return waste_type
    return entry.get("label", waste_type)
