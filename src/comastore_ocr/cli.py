from __future__ import annotations

import argparse
from pathlib import Path

from .config import DATA_DIR
from .processing import process_images_in_directory


def _cmd_process(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    process_images_in_directory(data_dir=data_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="ComaStore OCR commands")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("process-images", help="Generate labels for images in directory")
    p1.add_argument("--data-dir", type=Path, default=None, help="Images directory (default: config.DATA_DIR)")
    p1.set_defaults(func=_cmd_process)

    # JSONL conversion moved to comastore_dataset_tools (comastore-ds convert)

    # validation and sorting moved to comastore_dataset_tools

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()


