"""Common utilities for ComaStore OCR."""

from .helpers import (
    format_duration,
    calculate_eta,
    format_progress_message,
    ensure_directory_exists,
    is_image_file,
    has_json_pair,
    get_relative_path,
    group_files_by_directory,
    sort_files_by_directory_size,
    get_folder_statistics
)

from .image_processor_util import ImageProcessorUtil
from .image_encoder import ImageEncoder
from .image_validator import ImageValidator
from .image_utils_enhanced import (
    encode_image_to_data_uri,
    get_supported_formats,
    is_valid_image
)

from .validation import (
    ALLOWED_PROMO_CODES,
    CORE_PATTERNS,
    COND_PATTERN,
    NTH_PATTERN,
)

__all__ = [
    # Helpers
    "format_duration",
    "calculate_eta", 
    "format_progress_message",
    "ensure_directory_exists",
    "is_image_file",
    "has_json_pair",
    "get_relative_path",
    "group_files_by_directory",
    "sort_files_by_directory_size",
    "get_folder_statistics",
    
    # Image utilities
    "ImageProcessorUtil",
    "ImageEncoder",
    "ImageValidator", 
    "encode_image_to_data_uri",
    "get_supported_formats",
    "is_valid_image",
    
    # Validation
    "ALLOWED_PROMO_CODES",
    "CORE_PATTERNS",
    "COND_PATTERN", 
    "NTH_PATTERN",
]


