# SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

# App
from db import Base

# Utils
from datetime import datetime


class ReceiptScan(Base):
    """Stores one uploaded receipt image and its OCR output."""
    __tablename__ = 'receipt_scans'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)   # nullable for unauthenticated use
    image_path = Column(String(255), nullable=False)                   # path to saved image file
    raw_ocr_text = Column(Text, nullable=True)                         # raw text returned by OCR
    status = Column(String(20), nullable=False, default='pending')     # pending | processed | error
    error_message = Column(String(500), nullable=True)                 # filled when status=error
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    # Relationships
    items = relationship('ReceiptItem', back_populates='scan', cascade='all, delete-orphan')


class ReceiptItem(Base):
    """One detected product line extracted from the receipt."""
    __tablename__ = 'receipt_items'

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey('receipt_scans.id'), nullable=False)
    raw_line = Column(String(500), nullable=False)        # original text line from OCR
    normalized_name = Column(String(500), nullable=True)  # after name normalization
    quantity = Column(Integer, nullable=True, default=1)
    price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    scan = relationship('ReceiptScan', back_populates='items')
    estimate = relationship('PackagingEstimate', back_populates='item', uselist=False, cascade='all, delete-orphan')


class PackagingEstimate(Base):
    """Plastic/packaging estimate for a single receipt item."""
    __tablename__ = 'packaging_estimates'

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('receipt_items.id'), nullable=False)
    packaging_type = Column(String(50), nullable=True)   # bottle, bag, container, carton, can, glass, unknown
    plastic_type = Column(String(20), nullable=True)     # PET, HDPE, PP, LDPE, PS, PVC, unknown
    weight_grams = Column(Float, nullable=True)
    recyclable = Column(Boolean, nullable=True)
    confidence = Column(Float, nullable=True)            # 0.0 – 1.0
    needs_review = Column(Boolean, default=False)
    # plastique | verre | carton | papier | metal | mixte | organique | aucun | inconnu
    waste_type = Column(String(20), nullable=True)
    source = Column(String(30), nullable=True)           # rule_based | local_db | unknown
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    item = relationship('ReceiptItem', back_populates='estimate')
