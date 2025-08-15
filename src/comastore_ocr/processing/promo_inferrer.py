"""Promo inferrer class for handling promotion code inference from directory names."""

from pathlib import Path
from typing import Optional

from ..common.validation import ALLOWED_PROMO_CODES

class PromoInferrer:
    """Handles promotion code inference from directory names."""
    
    @staticmethod
    def normalize_promo_name(name: str) -> Optional[str]:
        """Normalize and validate promotion name."""
        candidate = (name or "").strip().upper()
        if not candidate:
            return None
        return candidate if candidate in ALLOWED_PROMO_CODES else None
    
    @staticmethod
    def infer_promo_from_parent(image_path: Path) -> Optional[str]:
        """Infer promotion code from parent directory name."""
        parent = image_path.parent.name
        return PromoInferrer.normalize_promo_name(parent)
