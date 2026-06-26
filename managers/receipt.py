"""
managers/receipt.py
--------------------
Orchestrates the full receipt processing pipeline:
  1. Preprocess image
  2. Run OCR
  3. Parse receipt lines
  4. Normalize product names (returns dict with brand info)
  5. Estimate packaging (uses brand for better scoring)
  6. Persist to database (receipt_scans → receipt_items → packaging_estimates)
  7. Return structured response dict
"""

import os
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

# Models
from models.receipt import ReceiptScan, ReceiptItem, PackagingEstimate

# Services
from services.receipt.image_processor import preprocess_image
from services.receipt import ocr_service
from services.receipt.receipt_parser import parse_receipt
from services.receipt.name_normalizer import normalize
from services.receipt.packaging_estimator import estimate_packaging

# Upload directory (created at startup if missing)
UPLOAD_DIR = os.path.join("static", "uploads", "receipts")


class ReceiptManager:

    @staticmethod
    def ensure_upload_dir():
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    @staticmethod
    def save_image(image_bytes: bytes, original_filename: str) -> str:
        ReceiptManager.ensure_upload_dir()
        ext = os.path.splitext(original_filename)[-1].lower() or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        return file_path

    @staticmethod
    def process_receipt(
        db: Session,
        image_bytes: bytes,
        original_filename: str,
        user_id: Optional[int] = None,
    ) -> dict:
        """
        Full pipeline. Returns a dict matching ReceiptScanResponse schema.
        """

        image_path = ReceiptManager.save_image(image_bytes, original_filename)

        scan = ReceiptScan(
            user_id=user_id,
            image_path=image_path,
            status="pending",
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        try:
            processed_bytes = preprocess_image(image_bytes)
            raw_text = ocr_service.extract_text(processed_bytes)

            if not ocr_service.is_ocr_available():
                scan.raw_ocr_text = None
                scan.status = "processed"
                scan.error_message = ocr_service.OCR_UNAVAILABLE_MESSAGE
                db.commit()
                db.refresh(scan)
                return {
                    "scan_id": scan.id,
                    "status": "processed",
                    "raw_text": None,
                    "items": [],
                    "error": ocr_service.OCR_UNAVAILABLE_MESSAGE,
                }

            scan.raw_ocr_text = raw_text
            db.commit()

            parsed_lines = parse_receipt(raw_text)

            item_results = []
            for line_data in parsed_lines:
                norm = normalize(line_data["name_part"])
                estimate = estimate_packaging(norm["normalized_name"], norm.get("brand"))

                item = ReceiptItem(
                    scan_id=scan.id,
                    raw_line=line_data["raw_line"],
                    normalized_name=norm["normalized_name"],
                    quantity=line_data["quantity"],
                    price=line_data.get("line_total") or line_data.get("unit_price"),
                )
                db.add(item)
                db.flush()

                pkg = PackagingEstimate(
                    item_id=item.id,
                    packaging_type=estimate["packaging_type"],
                    plastic_type=estimate["plastic_type"],
                    weight_grams=estimate["weight_grams"],
                    recyclable=estimate["recyclable"],
                    confidence=estimate["confidence"],
                    needs_review=estimate["needs_review"],
                    waste_type=estimate["waste_type"],
                    source=estimate["source"],
                )
                db.add(pkg)

                item_results.append({
                    "raw_line": line_data["raw_line"],
                    "normalized_name": norm["normalized_name"],
                    "brand": norm.get("brand"),
                    "quantity": line_data["quantity"],
                    "unit_price": line_data.get("unit_price"),
                    "line_total": line_data.get("line_total"),
                    "size": line_data.get("size"),
                    "packaging_type": estimate["packaging_type"],
                    "plastic_type": estimate["plastic_type"],
                    "weight_grams": estimate["weight_grams"],
                    "recyclable": estimate["recyclable"],
                    "waste_type": estimate["waste_type"],
                    "confidence": estimate["confidence"],
                    "needs_review": estimate["needs_review"],
                })

            scan.status = "processed"
            db.commit()
            db.refresh(scan)

            return {
                "scan_id": scan.id,
                "status": "processed",
                "raw_text": raw_text,
                "items": item_results,
                "error": None,
            }

        except Exception as exc:
            db.rollback()
            try:
                scan.status = "error"
                scan.error_message = str(exc)[:500]
                db.commit()
            except Exception:
                pass
            raise exc
