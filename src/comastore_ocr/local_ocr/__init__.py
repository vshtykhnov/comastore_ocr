"""Local OCR module for ComaStore OCR."""

from .text_rule import TextRule
from .text_rules_engine import TextRulesEngine, DEFAULT_RULES
from .text_ocr import ocr_image_to_text

__all__ = [
    "TextRule",
    "TextRulesEngine",
    "DEFAULT_RULES",
    "ocr_image_to_text",
]


