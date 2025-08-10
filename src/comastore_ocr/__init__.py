"""ComaStore OCR package.

Public API re-exports helpers for convenience.
"""

from .config import DATA_DIR
from .processing import process_images_in_directory
from .common import encode_image_to_data_uri, validate_label_object

__all__ = [
    "DATA_DIR",
    "process_images_in_directory",
    "encode_image_to_data_uri",
    "validate_label_object",
]


