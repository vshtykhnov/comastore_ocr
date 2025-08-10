import json
import time
from pathlib import Path
from typing import Dict, List, Optional

import openai

from .config import (
    DATA_DIR,
    IMAGE_EXTENSIONS,
)
from .engines import get_engine, LabelEngine
from .common.validation import ALLOWED_PROMO_CODES


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _get_default_engine() -> LabelEngine:
    return get_engine("openai")


def generate_label_for_image(
    image_path: Path,
    max_retries: int = 5,
    engine: LabelEngine | None = None,
    forced_promo: str | None = None,
) -> Dict:
    label_engine = engine or _get_default_engine()
    for attempt in range(1, max_retries + 1):
        try:
            return label_engine.generate_label(image_path) if forced_promo is None else label_engine.generate_label(image_path, forced_promo=forced_promo)
        except openai.RateLimitError as e:  # type: ignore[attr-defined]
            retry_after = None
            if hasattr(e, "response") and getattr(e, "response") is not None:  # pragma: no cover
                retry_after = e.response.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else min(2.0 * attempt, 5.0)
            print(f"⏳ Rate limit (attempt {attempt}/{max_retries}). Waiting {wait}s …")
            time.sleep(wait)
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"⚠️  Unexpected error (attempt {attempt}/{max_retries}): {e}. Retrying shortly …")
            time.sleep(0.5 * attempt)


def iter_images_to_process(data_dir: Path) -> List[Path]:
    # Recursively walk to support dataset organized by promo subfolders
    images: List[Path] = []
    for p in sorted(data_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS and not p.with_suffix(".json").exists():
            images.append(p)
    return images


def _normalize_promo_name(name: str) -> Optional[str]:
    candidate = (name or "").strip().upper()
    if not candidate:
        return None
    if candidate == "DEALPCT":
        candidate = "DISC"
    return candidate if candidate in ALLOWED_PROMO_CODES else None


def infer_promo_from_parent(image_path: Path) -> Optional[str]:
    # Infer from immediate parent directory name
    parent = image_path.parent.name
    return _normalize_promo_name(parent)


def process_images_in_directory(data_dir: Path = DATA_DIR, engine_name: str = "openai") -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory {data_dir} not found")

    to_process = iter_images_to_process(data_dir)

    total = len(to_process)
    if total == 0:
        print("🎉 Все изображения уже обработаны — новых файлов нет.")
        return

    start_time = time.time()

    # Sequential processing only; waits occur only on 429 inside generate_label_for_image
    label_engine = get_engine(engine_name)
    for idx, image_path in enumerate(to_process, start=1):
        json_path = image_path.with_suffix(".json")

        progress_pct = round(idx / total * 100, 1)
        # Determine promo to use only from folder inference
        effective_promo = infer_promo_from_parent(image_path)
        promo_note = f" promo={effective_promo}" if effective_promo else ""
        print(f"[{idx}/{total} | {progress_pct}%] → Processing {image_path.name}{promo_note}…")
        try:
            label = generate_label_for_image(image_path, engine=label_engine, forced_promo=effective_promo)
        except Exception as e:  # noqa: BLE001
            print(f"⚠️  Error processing {image_path.name}: {e}")
            continue

        with json_path.open("w", encoding="utf-8") as handle:
            json.dump(label, handle, ensure_ascii=False, indent=2)
        print(f"💾 Saved {json_path.name}")

        elapsed = time.time() - start_time
        remaining_images = total - idx
        if remaining_images:
            eta_sec = (elapsed / idx) * remaining_images
            print(f"⌛ Estimated time remaining: {format_duration(eta_sec)}")

    

