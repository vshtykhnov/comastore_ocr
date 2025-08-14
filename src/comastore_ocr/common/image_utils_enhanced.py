"""Enhanced image utilities with better organization and error handling."""

from .image_processor_util import ImageProcessorUtil
from .image_encoder import ImageEncoder
from .image_validator import ImageValidator

# Backward compatibility functions
def encode_image_to_data_uri(file_path) -> str:
    """Legacy function for backward compatibility."""
    return ImageEncoder.encode_to_data_uri(file_path) or ""


# Utility functions
def get_supported_formats() -> set:
    """Get list of supported image formats."""
    return ImageProcessorUtil.SUPPORTED_FORMATS.copy()


def is_valid_image(file_path) -> bool:
    """Quick check if file is a valid image."""
    is_valid, _ = ImageValidator.validate_image_file(file_path)
    return is_valid
