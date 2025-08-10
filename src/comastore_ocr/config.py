import os
from pathlib import Path


# Base directories
# PROJECT_ROOT should be the package root directory: comastore_ocr/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Prefer out/sorted if it exists; otherwise use train_data. Can be overridden via DATA_DIR env var.
_default_images_dir = PROJECT_ROOT / "out" / "sorted"
if not _default_images_dir.exists():
    _default_images_dir = PROJECT_ROOT / "train_data"
DATA_DIR = Path(os.getenv("DATA_DIR", _default_images_dir))


# Image formats supported
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


# OpenAI configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Response token cap. Our JSON is tiny; keep low for speed/cost
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "120"))


"""
No image preprocessing configuration – images are sent as-is.
"""



