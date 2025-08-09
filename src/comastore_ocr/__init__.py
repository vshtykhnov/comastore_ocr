"""ComaStore OCR package.

Public API re-exports helpers for convenience.
"""

from .config import DATA_DIR
from .convert import convert_json_dir_to_jsonl
from .processing import process_images_in_directory

__all__ = [
    "DATA_DIR",
    "convert_json_dir_to_jsonl",
    "process_images_in_directory",
]


