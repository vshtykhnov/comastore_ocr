"""Text rule class for representing text classification rules."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class TextRule:
    """Represents a text classification rule."""
    name: str
    matcher: Callable[[str], bool]
    promo: str
    description: str
    priority: int = 0
