from __future__ import annotations

import argparse
from pathlib import Path

from .config import DATA_DIR
from .processing import process_images_in_directory
from .local_ocr.sort_textual import sort_by_text_rules


def _cmd_process(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    process_images_in_directory(
        data_dir=data_dir,
        engine_name=args.engine,
    )



def main() -> None:
    parser = argparse.ArgumentParser(description="ComaStore OCR commands")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("process-images", help="Generate labels for images in directory")
    p1.add_argument("--data-dir", type=Path, default=None, help="Images directory (default: config.DATA_DIR)")
    p1.add_argument("--engine", type=str, default="openai", help="Label engine: openai (default)")
    p1.set_defaults(func=_cmd_process)

    p2 = sub.add_parser("sort-text", help="Sort images into out/sorted/<PROMO> using Tesseract + rules")
    p2.add_argument("--data-dir", type=Path, default=None, help="Images directory (default: config.DATA_DIR)")
    p2.add_argument("--out", type=Path, default=None, help="Output root (default: comastore_ocr/out/sorted)")
    p2.add_argument("--lang", type=str, default="pol", help="Tesseract language (default: pol)")
    p2.add_argument("--move", action="store_true", help="Move files instead of copying")
    p2.add_argument("--no-dump-text", action="store_true", help="Do not save raw OCR text dumps")
    p2.set_defaults(func=lambda a: sort_by_text_rules(
        data_dir=Path(a.data_dir) if a.data_dir else DATA_DIR,
        out_root=a.out,
        tesseract_lang=a.lang,
        move=a.move,
        dump_text=not a.no_dump_text,
    ))

    

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()


