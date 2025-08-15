"""Process images command handler."""

from typing import Dict, Any

from .command_handler import CommandHandler
from ..config import DATA_DIR, DEFAULT_ENGINE
from ..processing.directory_processor import process_images_in_directory


class ProcessImagesHandler(CommandHandler):
    """Handles the process-images command."""

    def execute(self) -> Dict[str, Any]:
        """Execute image processing."""
        data_dir = DATA_DIR
        engine_name = DEFAULT_ENGINE

        print(f"🚀 Starting image processing...")
        print(f"📁 Data directory: {data_dir}")
        print(f"🔧 Engine: {engine_name}")
        print("-" * 50)

        try:
            result = process_images_in_directory(
                data_dir=data_dir,
                engine_name=engine_name
            )
            return {"status": "success", "result": result}
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            return {"status": "error", "error": str(e)}
