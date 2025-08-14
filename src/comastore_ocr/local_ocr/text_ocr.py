from __future__ import annotations

import os
import pytesseract
from pathlib import Path
from PIL import Image, ImageOps

_tess_cmd = os.getenv("TESSERACT_CMD")
if _tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tess_cmd


def ocr_image_to_text(image_path: Path, lang: str = "pol") -> str:
    """Run Tesseract OCR on an image and return extracted text.

    - Uses Polish language by default (requires Tesseract + pol traineddata installed).
    - Applies light preprocessing for OCR robustness.
    """
    image = Image.open(image_path)
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=2)

    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(gray, lang=lang, config=config)
    return text.strip()


