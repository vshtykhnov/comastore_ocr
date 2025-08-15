"""Text classifier class for handling text classification using rules."""

from typing import List, Optional
from ..local_ocr.text_rules_engine import DEFAULT_RULES

class TextClassifier:
    """Handles text classification using rules."""
    
    def __init__(self, rules: List = None):
        self.rules = rules or DEFAULT_RULES
    
    def classify_text(self, text: str) -> Optional[str]:
        """Classify text using available rules."""
        for rule in self.rules:
            result = rule(text)
            if result:
                return result
        return None
