import json
from pathlib import Path
from typing import Tuple

from .config import DATA_DIR


def convert_json_dir_to_jsonl(
    data_dir: Path = DATA_DIR, output_file: Path | str = "training_data.jsonl"
) -> Tuple[int, int, Path]:
    """Convert all JSON files inside data_dir to a single JSONL file.

    The output record format mirrors the previous behavior:
    {"image_path": "images/<image>", "label": "<raw JSON string>"}

    Returns (processed_count, error_count, output_path).
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory {data_dir} not found")

    json_files = sorted(data_dir.glob("*.json"))
    output_path = Path(output_file)

    processed_count = 0
    error_count = 0

    with output_path.open("w", encoding="utf-8") as outfile:
        for json_path in json_files:
            try:
                with json_path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)

                # Prefer JPG; fall back to PNG
                image_name = json_path.stem + ".jpg"
                image_path = data_dir / image_name
                if not image_path.exists():
                    image_name = json_path.stem + ".png"
                    image_path = data_dir / image_name
                    if not image_path.exists():
                        print(f"⚠️  No image found for {json_path.name}")
                        error_count += 1
                        continue

                record = {"image_path": f"images/{image_name}", "label": json.dumps(data, ensure_ascii=False)}
                outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
                processed_count += 1
                print(f"✅ Processed {json_path.name}")

            except Exception as e:  # noqa: BLE001
                print(f"❌ Error processing {json_path.name}: {e}")
                error_count += 1

    return processed_count, error_count, output_path


