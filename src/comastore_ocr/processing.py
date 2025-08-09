import json
import time
from pathlib import Path
from typing import Dict, List

import openai

from .config import DATA_DIR, IMAGE_EXTENSIONS, REQUEST_PAUSE_SEC
from .image_utils import encode_image_to_data_uri
from .openai_utils import call_openai_with_json
from .prompts import PROMPT_TEXT
from .validation import validate_label_object


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _build_messages_for_image(image_path: Path) -> List[Dict]:
    data_uri = encode_image_to_data_uri(image_path)
    return [
        {"role": "system", "content": PROMPT_TEXT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract promotion details from this image."},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        },
    ]


def generate_label_for_image(image_path: Path, max_retries: int = 5) -> Dict:
    base_messages = _build_messages_for_image(image_path)

    for attempt in range(1, max_retries + 1):
        try:
            text_response = call_openai_with_json(base_messages, use_json_response_format=True)
            obj = json.loads(text_response)

            is_valid, err = validate_label_object(obj)
            if is_valid:
                return obj

            correction_messages = base_messages + [
                {
                    "role": "user",
                    "content": (
                        "Your previous JSON violated the schema (promo/promo_args/keys/types). "
                        "Return corrected JSON only. Do not add explanations."
                    ),
                }
            ]

            text_response = call_openai_with_json(correction_messages, use_json_response_format=True)
            obj = json.loads(text_response)
            is_valid, err = validate_label_object(obj)
            if is_valid:
                return obj
            else:
                raise ValueError(f"Schema validation failed: {err}")

        except openai.RateLimitError as e:  # type: ignore[attr-defined]
            retry_after = None
            if hasattr(e, "response") and getattr(e, "response") is not None:  # pragma: no cover
                retry_after = e.response.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else 5 * attempt
            print(f"⏳ Rate limit (attempt {attempt}/{max_retries}). Waiting {wait}s …")
            time.sleep(wait)
        except (json.JSONDecodeError, ValueError) as err:
            if attempt == max_retries:
                raise ValueError(f"Failed for {image_path.name}: {err}")
            print(
                f"⚠️  Validation/JSON error (attempt {attempt}/{max_retries}): {err}. Retrying in 3s …"
            )
            time.sleep(3)
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"⚠️  Unexpected error (attempt {attempt}/{max_retries}): {e}. Retrying in 5s …")
            time.sleep(5)

    raise RuntimeError(f"All {max_retries} attempts failed for {image_path.name}")


def iter_images_to_process(data_dir: Path) -> List[Path]:
    return [
        p
        for p in sorted(data_dir.iterdir())
        if p.suffix.lower() in IMAGE_EXTENSIONS and not p.with_suffix(".json").exists()
    ]


def process_images_in_directory(data_dir: Path = DATA_DIR) -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory {data_dir} not found")

    to_process = iter_images_to_process(data_dir)

    total = len(to_process)
    if total == 0:
        print("🎉 Все изображения уже обработаны — новых файлов нет.")
        return

    start_time = time.time()

    for idx, image_path in enumerate(to_process, start=1):
        json_path = image_path.with_suffix(".json")

        progress_pct = round(idx / total * 100, 1)
        print(f"[{idx}/{total} | {progress_pct}%] → Processing {image_path.name}…")
        try:
            label = generate_label_for_image(image_path)
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

        if idx < total and REQUEST_PAUSE_SEC > 0:
            print(f"⏸ Waiting {REQUEST_PAUSE_SEC}s before next request…")
            time.sleep(REQUEST_PAUSE_SEC)

    

