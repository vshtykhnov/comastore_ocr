"""Sort text command handler."""

from pathlib import Path
from typing import Dict, Any

from .command_handler import CommandHandler
from ..config import DATA_DIR, DEFAULT_SORTED_OUTPUT, DEFAULT_LANGUAGE
from ..processing.file_sorter import FileSorter


class SortTextHandler(CommandHandler):
    """Handles the sort-text command."""

    def execute(self) -> Dict[str, Any]:
        """Execute text-based sorting."""
        data_dir = DATA_DIR
        out_root = DEFAULT_SORTED_OUTPUT
        lang = DEFAULT_LANGUAGE

        print(f"📂 Starting text-based sorting...")
        print(f"📁 Input directory: {data_dir}")
        print(f"📁 Output directory: {out_root}")
        print(f"🌐 Language: {lang}")
        print("-" * 50)

        try:
            sorter = FileSorter(
                allowed_extensions={".jpg", ".jpeg", ".png", ".webp", ".bmp"},
                tesseract_lang=lang,
                dump_text=True  # Always enabled
            )

            result = sorter.sort_files(data_dir, out_root)
            return {"status": "success", "result": result}
        except Exception as e:
            print(f"❌ Error during sorting: {e}")
            return {"status": "error", "error": str(e)}
