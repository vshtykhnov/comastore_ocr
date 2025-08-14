"""File filter class for handling filtering of sorted directories."""

import shutil
from pathlib import Path
from typing import Dict

from ..common.helpers import get_relative_path


class FileFilter:
    """Handles filtering of sorted directories."""
    
    def __init__(self, allowed_extensions: set):
        self.allowed_extensions = allowed_extensions
    
    def filter_sorted_directory(
        self, 
        src_dir: Path, 
        dst_dir: Path, 
        move: bool = False
    ) -> Dict:
        """Copy/move only images that have a sibling .json from src_dir to dst_dir."""
        if not src_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {src_dir}")
        
        self._ensure_directory_exists(dst_dir)
        
        copied = 0
        moved = 0
        skipped = 0
        
        for file_path in sorted(src_dir.rglob("*")):
            if not self._is_image_file(file_path):
                continue
            
            json_path = file_path.with_suffix(".json")
            if not json_path.exists():
                skipped += 1
                continue
            
            rel = get_relative_path(file_path, src_dir)
            out_img = dst_dir / rel
            out_json = dst_dir / rel.with_suffix(".json")
            
            self._ensure_directory_exists(out_img.parent)
            
            try:
                if move:
                    shutil.move(str(file_path), str(out_img))
                    shutil.move(str(json_path), str(out_json))
                    moved += 1
                else:
                    shutil.copy2(file_path, out_img)
                    shutil.copy2(json_path, out_json)
                    copied += 1
            except Exception as e:
                print(f"⚠️  Error processing {file_path.name}: {e}")
                continue
        
        action = "Moved" if move else "Copied"
        print(f"Done. {action} {moved if move else copied} images with JSON. Skipped (no JSON): {skipped}. Output: {dst_dir}")
        
        return {
            "copied": copied,
            "moved": moved,
            "skipped": skipped,
            "action": action.lower()
        }
    
    def _is_image_file(self, file_path: Path) -> bool:
        """Check if file is an image based on extension."""
        return file_path.is_file() and file_path.suffix.lower() in self.allowed_extensions
    
    def _ensure_directory_exists(self, directory: Path) -> None:
        """Ensure directory exists, creating parent directories if needed."""
        directory.mkdir(parents=True, exist_ok=True)
