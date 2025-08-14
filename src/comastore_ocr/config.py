import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Default directories
_default_images_dir = PROJECT_ROOT / "out" / "sorted"
if not _default_images_dir.exists():
    _default_images_dir = PROJECT_ROOT / "train_data"
DATA_DIR = Path(os.getenv("DATA_DIR", _default_images_dir))

# Default output directories
DEFAULT_SORTED_OUTPUT = PROJECT_ROOT / "out" / "sorted"

# Default engine
DEFAULT_ENGINE = "openai"

# Default language
DEFAULT_LANGUAGE = "pol"

# Image formats supported
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# OpenAI configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Response token cap. Our JSON is tiny; keep low for speed/cost
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "120"))



