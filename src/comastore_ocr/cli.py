from __future__ import annotations

import argparse
from pathlib import Path

from .config import DATA_DIR
from .convert import convert_json_dir_to_jsonl
from .processing import process_images_in_directory, validate_existing_jsons_in_directory


def _cmd_process(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    process_images_in_directory(data_dir=data_dir)


def _cmd_convert(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    output = Path(args.output)
    convert_json_dir_to_jsonl(data_dir=data_dir, output_file=output)


def main() -> None:
    parser = argparse.ArgumentParser(description="ComaStore OCR commands")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("process-images", help="Generate labels for images in directory")
    p1.add_argument("--data-dir", type=Path, default=None, help="Images directory (default: config.DATA_DIR)")
    p1.set_defaults(func=_cmd_process)

    p2 = sub.add_parser("convert-jsonl", help="Convert JSON labels to a single JSONL")
    p2.add_argument("--data-dir", type=Path, default=None, help="Labels directory (default: config.DATA_DIR)")
    p2.add_argument("--output", type=Path, default=Path("training_data.jsonl"))
    p2.set_defaults(func=_cmd_convert)

    p3 = sub.add_parser("validate-jsons", help="Validate existing JSON files against images; fix or remove if needed")
    p3.add_argument("--data-dir", type=Path, default=None, help="Directory with images+JSONs (default: config.DATA_DIR)")
    p3.add_argument("--keep-none", action="store_true", help="Do not delete JSONs when promo == NONE")
    def _cmd_validate(args: argparse.Namespace) -> None:
        data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
        validate_existing_jsons_in_directory(data_dir=data_dir, delete_none=not args.keep_none)
    p3.set_defaults(func=_cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()


