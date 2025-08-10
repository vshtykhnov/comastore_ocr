"""ComaStore OCR package.

Public API re-exports helpers for convenience.
"""

from .config import DATA_DIR
from .processing import process_images_in_directory

__all__ = [
    "DATA_DIR",
    "process_images_in_directory",
]


