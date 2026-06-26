# Pydantic
from pydantic import BaseModel
from typing import List, Optional


class PackagingEstimateSchema(BaseModel):
    packaging_type: Optional[str] = None    # e.g. "bocal", "sachet plastique"
    plastic_type: Optional[str] = None      # e.g. "PET", "HDPE", "PP"
    weight_grams: Optional[float] = None
    recyclable: Optional[bool] = None
    confidence: Optional[float] = None      # 0.0 – 1.0
    needs_review: bool = False
    # plastique | verre | carton | papier | metal | mixte | organique | aucun | inconnu
    waste_type: Optional[str] = None
    source: Optional[str] = None            # "rule_based" | "local_db" | "unknown"

    class Config:
        from_attributes = True


class ReceiptItemSchema(BaseModel):
    raw_line: str
    normalized_name: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[int] = 1
    unit_price: Optional[float] = None
    line_total: Optional[float] = None
    size: Optional[str] = None
    packaging_type: Optional[str] = None
    plastic_type: Optional[str] = None
    weight_grams: Optional[float] = None
    recyclable: Optional[bool] = None
    waste_type: Optional[str] = None
    confidence: Optional[float] = None
    needs_review: bool = False

    class Config:
        from_attributes = True


class ReceiptScanResponse(BaseModel):
    scan_id: int
    status: str                             # "processed" | "error"
    raw_text: Optional[str] = None
    items: List[ReceiptItemSchema] = []
    error: Optional[str] = None            # populated when status="error"
    image_url: Optional[str] = None        # URL to the uploaded receipt image

    class Config:
        from_attributes = True


class ReceiptScanSummary(BaseModel):
    scan_id: int
    created_at: Optional[str] = None
    item_count: int = 0
    total_plastic_grams: float = 0.0
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
