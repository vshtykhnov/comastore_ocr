from __future__ import annotations

from .base import LabelEngine
from .openai_engine import OpenAIEngine


def get_engine(name: str = "openai") -> LabelEngine:
    normalized = (name or "openai").strip().lower()
    if normalized in {"openai", "gpt", "gpt4o", "gpt-4o", "gpt-4o-mini"}:
        return OpenAIEngine()
    raise ValueError(f"Unknown engine '{name}'. Supported: openai")


__all__ = ["LabelEngine", "OpenAIEngine", "get_engine"]


