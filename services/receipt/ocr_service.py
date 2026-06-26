"""
ocr_service.py
--------------
Extracts raw text from a preprocessed image using Tesseract OCR.

Requires:
  - pytesseract  (pip install pytesseract)
  - Tesseract binary installed on the system (see setup notes below)
  - Pillow       (pip install Pillow)

Windows setup:
  1. Download and install Tesseract from:
     https://github.com/UB-Mannheim/tesseract/wiki
     (Use the installer: tesseract-ocr-w64-setup-*.exe)
  2. During installation, note the install path (default: C:\\Program Files\\Tesseract-OCR)
  3. Set TESSERACT_CMD in your .env file:
     TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
  4. If you also need Spanish/French receipt support, install the language packs
     during Tesseract setup and add lang='spa' or lang='fra' to the call below.

If Tesseract is not installed, the service returns a controlled error string
instead of crashing the app.
"""

import io
import logging

logger = logging.getLogger(__name__)

# python-decouple for optional TESSERACT_CMD path
try:
    from decouple import config as env_config
    TESSERACT_CMD = env_config("TESSERACT_CMD", default=None)
except Exception:
    TESSERACT_CMD = None

# Tesseract / pytesseract — optional dependency
try:
    import pytesseract
    from PIL import Image

    if TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


OCR_UNAVAILABLE_MESSAGE = (
    "OCR service is unavailable. "
    "Please install Tesseract and pytesseract to enable text extraction. "
    "See services/receipt/ocr_service.py for Windows setup instructions."
)

_OCR_CONFIG = "--psm 6"


def extract_text(image_bytes: bytes) -> str:
    """
    Accepts preprocessed image bytes and returns the extracted text string.

    Tries French OCR first (better for Leclerc/French supermarket receipts).
    Falls back to English if the French language pack is not installed.
    Returns OCR_UNAVAILABLE_MESSAGE if Tesseract is not installed at all.
    """
    if not TESSERACT_AVAILABLE:
        return OCR_UNAVAILABLE_MESSAGE

    try:
        image = Image.open(io.BytesIO(image_bytes))
        try:
            text = pytesseract.image_to_string(image, lang="fra", config=_OCR_CONFIG)
        except pytesseract.TesseractError:
            logger.warning("French Tesseract language pack not found — falling back to English")
            text = pytesseract.image_to_string(image, lang="eng", config=_OCR_CONFIG)
        return text.strip()
    except Exception as exc:
        return f"OCR error: {str(exc)}"


def is_ocr_available() -> bool:
    return TESSERACT_AVAILABLE
