"""Validation rule class for representing validation rules."""

from dataclasses import dataclass
from typing import Callable, Optional, Dict


@dataclass(frozen=True)
class ValidationRule:
    """Represents a validation rule."""
    name: str
    validator: Callable
    description: str
    severity: str = "error"  # error, warning, info
