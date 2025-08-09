import os
from pathlib import Path


# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "train_data"))


# Image formats supported
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


# OpenAI configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_RPM = int(os.getenv("OPENAI_MAX_RPM", "500"))

if "REQUEST_PAUSE_SEC" in os.environ:
    REQUEST_PAUSE_SEC = float(os.getenv("REQUEST_PAUSE_SEC", "0"))
else:
    REQUEST_PAUSE_SEC = (60.0 / OPENAI_MAX_RPM) * 1.05



