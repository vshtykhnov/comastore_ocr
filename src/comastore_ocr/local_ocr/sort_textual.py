from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List

from ..config import DATA_DIR, IMAGE_EXTENSIONS, PROJECT_ROOT
from .text_ocr import ocr_image_to_text
from .text_rules import DEFAULT_RULES


def _iter_images(data_dir: Path) -> List[Path]:
    return [p for p in sorted(data_dir.iterdir()) if p.suffix.lower() in IMAGE_EXTENSIONS]


def classify_text_to_promo(text: str) -> str | None:
    for rule in DEFAULT_RULES:
        result = rule(text)
        if result:
            return result
    return None


def sort_by_text_rules(
    data_dir: Path = DATA_DIR,
    out_root: Path | None = None,
    tesseract_lang: str = "pol",
    move: bool = False,
    dump_text: bool = True,
) -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory {data_dir} not found")

    if out_root is None:
        out_root = PROJECT_ROOT / "out" / "sorted"

    out_root.mkdir(parents=True, exist_ok=True)

    images = _iter_images(data_dir)
    if not images:
        print("ℹ️  No images found to sort.")
        return

    copied = 0
    moved = 0
    unknown = 0

    if dump_text:
        text_dump_dir = out_root / "_ocr_text"
        text_dump_dir.mkdir(parents=True, exist_ok=True)

    # Pre-scan existing outputs to skip without doing OCR
    existing_names: set[str] = set()
    for promo_dir in out_root.iterdir():
        if promo_dir.is_dir() and promo_dir.name != "_ocr_text":
            for f in promo_dir.iterdir():
                if f.is_file():
                    existing_names.add(f.name)

    images_to_process = [img for img in images if img.name not in existing_names]
    skipped_pre = len(images) - len(images_to_process)
    if skipped_pre:
        print(f"ℹ️  Pre-skip: {skipped_pre} already present in output. Will process {len(images_to_process)}.")

    total = len(images_to_process)

    for index, img in enumerate(images_to_process, start=1):
        prefix = f"[{index}/{total} | left {total - index}]"

        # Reuse existing OCR dump if available
        text: str
        if dump_text:
            dump_file = (text_dump_dir / f"{img.stem}.txt")
            if dump_file.exists():
                text = dump_file.read_text(encoding="utf-8")
            else:
                text = ocr_image_to_text(img, lang=tesseract_lang)
        else:
            text = ocr_image_to_text(img, lang=tesseract_lang)
        if dump_text:
            (text_dump_dir / f"{img.stem}.txt").write_text(text, encoding="utf-8")
        promo = classify_text_to_promo(text)
        if promo is None:
            print(f"{prefix} [WARN] Could not classify: {img.name}")
            promo = "UNKNOWN"
            unknown += 1

        dst_dir = out_root / promo
        dst_dir.mkdir(parents=True, exist_ok=True)
        dest_img = dst_dir / img.name
        if dest_img.exists():
            print(f"{prefix} [SKIP] Exists: {dest_img}")
            continue

        if move:
            shutil.move(str(img), str(dest_img))
            moved += 1
            print(f"{prefix} Moved -> {dest_img}")
        else:
            shutil.copy2(img, dest_img)
            copied += 1
            print(f"{prefix} Copied -> {dest_img}")

    print(
        f"Done. Processed {total} images (pre-skipped {skipped_pre}). {'Moved' if move else 'Copied'} {moved if move else copied}. Unknown: {unknown}. Output: {out_root}"
    )


