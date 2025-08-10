from __future__ import annotations

from pathlib import Path
import os
from typing import Optional

from PIL import Image, ImageOps
import pytesseract

# Allow overriding Tesseract binary location via env var
_tess_cmd = os.getenv("TESSERACT_CMD")
if _tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tess_cmd


def ocr_image_to_text(image_path: Path, lang: str = "pol") -> str:
    """Run Tesseract OCR on an image and return extracted text.

    - Uses Polish language by default (requires Tesseract + pol traineddata installed).
    - Applies light preprocessing for OCR robustness.
    """
    image = Image.open(image_path)
    # Convert to grayscale and autocontrast to improve OCR quality
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=2)

    # Use Tesseract with a readable PSM for poster-like images
    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(gray, lang=lang, config=config)
    return text.strip()


