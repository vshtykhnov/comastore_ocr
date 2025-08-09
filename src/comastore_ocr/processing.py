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


def _format_value_for_log(value: object) -> str:
    if isinstance(value, str):
        # collapse whitespaces and quote
        s = " ".join(value.split())
        return f'"{s}"'
    return str(value)


def _summarize_changes(old: Dict, new: Dict) -> str:
    keys = ["name", "price", "promo", "promo_args"]
    parts: list[str] = []
    for k in keys:
        old_v = old.get(k)
        new_v = new.get(k)
        if old_v != new_v:
            parts.append(f"{k}: {_format_value_for_log(old_v)} -> {_format_value_for_log(new_v)}")
    return "; ".join(parts) if parts else "no field changes"


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

        # Business rule: do not save labels when promo == NONE
        if label.get("promo") == "NONE":
            print(f"🚫 Skipped saving for {image_path.name} (promo == NONE)")
        else:
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


def _build_messages_for_validation(image_path: Path, existing_json_text: str) -> List[Dict]:
    data_uri = encode_image_to_data_uri(image_path)
    instruction = (
        "You will receive an image and a candidate JSON produced by previous OCR. "
        "Return ONLY valid JSON per the schema from the system prompt. "
        "If the candidate JSON is already fully correct for THIS image and schema, return it unchanged. "
        "Otherwise, return corrected JSON."
    )
    return [
        {"role": "system", "content": PROMPT_TEXT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": instruction},
                {"type": "image_url", "image_url": {"url": data_uri}},
                {"type": "text", "text": f"Candidate JSON:\n{existing_json_text}"},
            ],
        },
    ]


def validate_and_fix_label_for_image(image_path: Path, existing_label: Dict, max_retries: int = 5) -> Dict | None:
    """Validate existing label against the image; return corrected label or None for promo==NONE.

    If the model judges that there is no promotion (promo == "NONE"), caller may interpret
    that as a signal to remove the JSON file (business rule).
    """
    import json as _json

    existing_text = _json.dumps(existing_label, ensure_ascii=False)
    base_messages = _build_messages_for_validation(image_path, existing_text)

    for attempt in range(1, max_retries + 1):
        try:
            text_response = call_openai_with_json(base_messages, use_json_response_format=True)
            obj = _json.loads(text_response)
            is_valid, err = validate_label_object(obj)
            if is_valid:
                return obj if obj.get("promo") != "NONE" else None

            correction_messages = base_messages + [
                {
                    "role": "user",
                    "content": (
                        "Your previous JSON violated the schema. Return corrected JSON only."
                    ),
                }
            ]
            text_response = call_openai_with_json(correction_messages, use_json_response_format=True)
            obj = _json.loads(text_response)
            is_valid, err = validate_label_object(obj)
            if is_valid:
                return obj if obj.get("promo") != "NONE" else None
            else:
                raise ValueError(f"Schema validation failed: {err}")

        except openai.RateLimitError as e:  # type: ignore[attr-defined]
            retry_after = None
            if hasattr(e, "response") and getattr(e, "response") is not None:  # pragma: no cover
                retry_after = e.response.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else 5 * attempt
            print(f"⏳ Rate limit (attempt {attempt}/{max_retries}). Waiting {wait}s …")
            time.sleep(wait)
        except (_json.JSONDecodeError, ValueError) as err:
            if attempt == max_retries:
                raise ValueError(f"Validation failed for {image_path.name}: {err}")
            print(f"⚠️  Validation/JSON error (attempt {attempt}/{max_retries}): {err}. Retrying in 3s …")
            time.sleep(3)
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"⚠️  Unexpected error (attempt {attempt}/{max_retries}): {e}. Retrying in 5s …")
            time.sleep(5)

    raise RuntimeError(f"All {max_retries} attempts failed for {image_path.name}")


def iter_jsons_with_images(data_dir: Path) -> List[Path]:
    return [
        p
        for p in sorted(data_dir.glob("*.json"))
        if any((p.with_suffix(ext)).exists() for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"])
    ]


def validate_existing_jsons_in_directory(
    data_dir: Path = DATA_DIR,
    delete_none: bool = True,
    delete_invalid: bool = True,
) -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory {data_dir} not found")

    json_files = iter_jsons_with_images(data_dir)
    total = len(json_files)
    if total == 0:
        print("ℹ️  No JSON files found to validate.")
        return

    start_time = time.time()
    fixed = 0
    removed = 0

    for idx, json_path in enumerate(json_files, start=1):
        img_path = None
        for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            candidate = json_path.with_suffix(ext)
            if candidate.exists():
                img_path = candidate
                break
        if img_path is None:
            print(f"[WARN] No image found for {json_path.name} — skipping")
            continue

        try:
            with json_path.open("r", encoding="utf-8") as h:
                existing = json.load(h)
        except Exception as e:
            print(f"[WARN] Cannot read JSON {json_path.name}: {e}")
            if delete_invalid and json_path.exists():
                json_path.unlink()
                removed += 1
                print(f"🗑️  Removed unreadable {json_path.name}")
            continue

        # If existing JSON fails schema validation, delete instead of fixing (per requirement)
        is_valid_schema, err_msg = validate_label_object(existing)
        if not is_valid_schema:
            if delete_invalid and json_path.exists():
                json_path.unlink()
                removed += 1
                print(f"🗑️  Removed {json_path.name} (invalid schema: {err_msg})")
            else:
                print(f"ℹ️  Invalid schema for {json_path.name} (kept)")
            continue

        try:
            corrected = validate_and_fix_label_for_image(img_path, existing)
        except Exception as e:  # noqa: BLE001
            print(f"⚠️  Error validating {json_path.name}: {e}")
            # Treat as invalid if requested
            if delete_invalid and json_path.exists():
                json_path.unlink()
                removed += 1
                print(f"🗑️  Removed {json_path.name} (validation error)")
            continue

        if corrected is None:
            if delete_none and json_path.exists():
                json_path.unlink()
                removed += 1
                print(f"🗑️  Removed {json_path.name} (promo == NONE)")
            else:
                print(f"ℹ️  promo == NONE for {json_path.name} (kept)")
            continue

        # Compare semantic equality
        if corrected == existing:
            pass  # unchanged
        else:
            change_line = _summarize_changes(existing, corrected)
            with json_path.open("w", encoding="utf-8") as handle:
                json.dump(corrected, handle, ensure_ascii=False, indent=2)
            fixed += 1
            print(f"✏️  Updated {json_path.name}: {change_line}")

        # pacing
        elapsed = time.time() - start_time
        remaining = total - idx
        if remaining:
            eta_sec = (elapsed / idx) * remaining
            print(f"⌛ Estimated time remaining: {format_duration(eta_sec)}")

        if idx < total and REQUEST_PAUSE_SEC > 0:
            print(f"⏸ Waiting {REQUEST_PAUSE_SEC}s before next request…")
            time.sleep(REQUEST_PAUSE_SEC)

    print(f"Done. Fixed: {fixed}, Removed: {removed}, Total processed: {total}")

