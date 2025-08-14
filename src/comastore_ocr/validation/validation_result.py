"""Validation result class for representing validation results."""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class ValidationResult:
    """Represents a validation result."""
    is_valid: bool
    message: str
    rule_name: str
    severity: str
    details: Optional[Dict] = None
