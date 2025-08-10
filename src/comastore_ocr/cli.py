from __future__ import annotations

import argparse
from pathlib import Path

from .config import DATA_DIR
from .processing import process_images_in_directory, filter_sorted_directory
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

    p3 = sub.add_parser("filter-sorted", help="Copy/move only files with existing JSON pairs from a sorted tree")
    p3.add_argument("--src", type=Path, default=None, help="Source sorted dir (default: comastore_ocr/out/sorted if exists, else DATA_DIR)")
    p3.add_argument("--dst", type=Path, default=None, help="Destination dir (default: comastore_ocr/out/sorted_filtered)")
    p3.add_argument("--move", action="store_true", help="Move files instead of copying")
    def _run_filter(a):
        from .config import PROJECT_ROOT
        default_src = PROJECT_ROOT / "out" / "sorted"
        src = Path(a.src) if a.src else (default_src if default_src.exists() else DATA_DIR)
        dst = Path(a.dst) if a.dst else (PROJECT_ROOT / "out" / "sorted_filtered")
        filter_sorted_directory(src_dir=src, dst_dir=dst, move=a.move)
    p3.set_defaults(func=_run_filter)

    

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()


