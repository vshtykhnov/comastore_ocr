"""ComaStore OCR package.

Enhanced package with improved structure and organization.
Public API re-exports helpers for convenience.
"""

# Core configuration
from .config import DATA_DIR, IMAGE_EXTENSIONS, PROJECT_ROOT, OPENAI_MODEL, OPENAI_MAX_TOKENS

# Processing modules
from .processing.directory_processor import process_images_in_directory, DirectoryProcessor
from .processing.image_processor import ImageProcessor
from .processing.promo_inferrer import PromoInferrer
from .processing.image_file_manager import ImageFileManager
from .processing.text_classifier import TextClassifier
from .processing.file_sorter import FileSorter
from .processing.file_filter import FileFilter

# Engine management
from .engines.factory import get_engine, register_engine, list_engines, test_engine
from .engines.base import LabelEngine
from .engines.openai_engine import OpenAIEngine

# Enhanced utilities
from .common.helpers import (
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

# Enhanced image utilities
from .common.image_processor_util import ImageProcessor as ImageProcessorUtil
from .common.image_encoder import ImageEncoder
from .common.image_validator import ImageValidator
from .common.image_utils_enhanced import (
    encode_image_to_data_uri,
    get_image_info,
    get_supported_formats,
    is_valid_image
)

# Enhanced validation
from .validation.validation_rule import ValidationRule
from .validation.validation_result import ValidationResult
from .validation.enhanced_validator import (
    LabelValidator,
    validate_label_object,
    validate_with_details,
    get_validator
)

# Text rules engine
from .local_ocr.text_rule import TextRule
from .local_ocr.text_rules_engine import TextRulesEngine, DEFAULT_RULES

# CLI
from .cli.command_handler import CommandHandler
from .cli.process_images_handler import ProcessImagesHandler
from .cli.sort_text_handler import SortTextHandler
from .cli.filter_sorted_handler import FilterSortedHandler
from .cli.list_engines_handler import ListEnginesHandler
from .cli.test_engine_handler import TestEngineHandler
from .cli.enhanced_cli import CLIApplication, main as cli_main

__all__ = [
    # Configuration
    "DATA_DIR",
    "IMAGE_EXTENSIONS", 
    "PROJECT_ROOT",
    "OPENAI_MODEL",
    "OPENAI_MAX_TOKENS",
    
    # Processing
    "process_images_in_directory",
    "DirectoryProcessor",
    "ImageProcessor",
    "PromoInferrer", 
    "ImageFileManager",
    "TextClassifier",
    "FileSorter",
    "FileFilter",
    
    # Engines
    "get_engine",
    "register_engine",
    "list_engines",
    "test_engine",
    "LabelEngine",
    "OpenAIEngine",
    
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
    "get_image_info",
    "get_supported_formats",
    "is_valid_image",
    
    # Validation
    "ValidationRule",
    "ValidationResult",
    "LabelValidator",
    "validate_label_object",
    "validate_with_details",
    "get_validator",
    
    # Text rules
    "TextRule",
    "TextRulesEngine",
    "DEFAULT_RULES",
    
    # CLI
    "CommandHandler",
    "ProcessImagesHandler",
    "SortTextHandler",
    "FilterSortedHandler",
    "ListEnginesHandler",
    "TestEngineHandler",
    "CLIApplication",
    "cli_main",
]

# Version information
__version__ = "2.0.0"
__author__ = "ComaStore Team"
__description__ = "Enhanced OCR system for ComaStore with improved architecture"


