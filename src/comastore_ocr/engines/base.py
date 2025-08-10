from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional


class LabelEngine(ABC):
    """Abstract interface for engines that produce label JSON from images."""

    @abstractmethod
    def build_messages(self, image_path: Path, forced_promo: Optional[str] = None) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def generate_label(self, image_path: Path, forced_promo: Optional[str] = None) -> Dict:
        raise NotImplementedError


