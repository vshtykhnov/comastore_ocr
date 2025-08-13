from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass(frozen=True)
class Rule:
    name: str
    matcher: Callable[[str], bool]
    promo: str


def _contains_any(text: str, patterns: List[str]) -> bool:
    t = text.lower()
    return any(p in t for p in patterns)


def rule_bxyg(text: str) -> Optional[str]:
    # Keywords like "X+Y gratis" → BXYG
    if re.search(r"\b(\d+)\s*\+\s*(\d+)\s*gratis\b", text, flags=re.IGNORECASE):
        return "BXYG"
    if _contains_any(text, ["gratis przy zakupie", "gratis"]):
        return "BXYG"
    return None


# Removed separate DEALPCT; patterns moved into rule_disc


def rule_dealfix(text: str) -> Optional[str]:
    # "drugi za X zł" / "N-ty za X zł"
    if re.search(r"\b(drugi|\d+-?ty)\b\s*za\s*\d+[\,\.]?\d*\s*zł", text, flags=re.IGNORECASE):
        return "DEALFIX"
    return None


def rule_disc(text: str) -> Optional[str]:
    # Discount patterns (now include former DEALPCT conditions):
    # 1) "drugi … % taniej"
    if re.search(r"\bdrugi\b.*?\%\s*taniej", text, flags=re.IGNORECASE | re.DOTALL):
        return "DISC"
    # 2) "% taniej przy zakupie N"
    if re.search(r"\%\s*taniej\s*przy\s*zakupie\s*\d+", text, flags=re.IGNORECASE):
        return "DISC"
    # 3) TERAZ TANIEJ keyword
    if _contains_any(text, ["teraz taniej"]):
        return "DISC"
    # 4) Standalone "% taniej" without explicit purchase-condition keywords
    if re.search(r"\b\d+\s*%\s*taniej\b", text, flags=re.IGNORECASE) and not _contains_any(
        text, ["przy zakupie", "drugi", "n-ty"]
    ):
        return "DISC"
    return None


def rule_sup(text: str) -> Optional[str]:
    # SUPERCENA: allow regardless of presence of "pak/PAKU" or other qualifiers
    if _contains_any(text, ["supercena"]):
        return "SUP"
    return None


def rule_none(text: str) -> Optional[str]:
    if _contains_any(text, ["na stałe w ofercie"]):
        return "NONE"
    return None


DEFAULT_RULES: List[Callable[[str], Optional[str]]] = [
    rule_bxyg,
    rule_dealfix,
    rule_disc,
    rule_sup,
    rule_none,
]


