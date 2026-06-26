"""
image_processor.py
------------------
Preprocesses a receipt image to improve OCR accuracy.
Operations: EXIF-based auto-rotation, grayscale conversion, contrast enhancement,
and optional downscaling for large images.

Requires: Pillow (pip install Pillow)
"""

import io
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageEnhance, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def preprocess_image(image_bytes: bytes) -> bytes:
    """
    Accepts raw image bytes and returns preprocessed image bytes (JPEG).
    If Pillow is not installed, returns the original bytes unchanged.
    """
    if not PIL_AVAILABLE:
        return image_bytes

    image = Image.open(io.BytesIO(image_bytes))

    # --- Auto-rotate based on EXIF orientation ---
    image = _fix_exif_rotation(image)

    # --- Convert to grayscale ---
    image = image.convert("L")

    # --- Boost contrast ---
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # --- Downscale very large images (keeps OCR fast) ---
    max_dimension = 2000
    if max(image.size) > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    # --- Serialize back to bytes ---
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=85)
    return output.getvalue()


def _fix_exif_rotation(image: "Image.Image") -> "Image.Image":
    """Rotates image to correct orientation according to EXIF data."""
    try:
        exif = image._getexif()
        if exif is None:
            return image

        orientation_key = next(
            (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
        )
        if orientation_key is None or orientation_key not in exif:
            return image

        orientation = exif[orientation_key]
        rotation_map = {3: 180, 6: 270, 8: 90}
        degrees = rotation_map.get(orientation)
        if degrees:
            image = image.rotate(degrees, expand=True)
    except Exception:
        # EXIF parsing can fail for many image types — silently skip
        pass
    return image
