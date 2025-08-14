"""Image file manager class for handling image file operations and filtering."""

from pathlib import Path
from typing import Dict, List
from collections import defaultdict, OrderedDict


class ImageFileManager:
    """Manages image file operations and filtering."""
    
    def __init__(self, allowed_extensions: set):
        self.allowed_extensions = allowed_extensions
    
    def find_images_to_process(self, data_dir: Path) -> List[Path]:
        """Find images that need processing (no existing JSON)."""
        images = []
        for file_path in sorted(data_dir.rglob("*")):
            if not self._is_image_file(file_path):
                continue
            
            # Skip if JSON already exists
            if self._has_json_pair(file_path):
                continue
            
            # Skip UNKNOWN directory
            parent_name = file_path.parent.name.strip().upper()
            if parent_name == "UNKNOWN":
                continue
            
            images.append(file_path)
        
        return self._sort_files_by_directory_size(images)
    
    def get_processing_summary(self, images: List[Path]) -> Dict:
        """Get summary of images to be processed."""
        folder_stats = self._get_folder_statistics(images)
        order_preview = ", ".join(f"{k}:{v}" for k, v in folder_stats.items())
        
        return {
            "total_images": len(images),
            "folder_distribution": dict(folder_stats),
            "order_preview": order_preview
        }
    
    def _is_image_file(self, file_path: Path) -> bool:
        """Check if file is an image based on extension."""
        return file_path.is_file() and file_path.suffix.lower() in self.allowed_extensions
    
    def _has_json_pair(self, file_path: Path) -> bool:
        """Check if file has a corresponding JSON file."""
        json_path = file_path.with_suffix(".json")
        return json_path.exists()
    
    def _group_files_by_directory(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Group files by their parent directory name."""
        buckets: Dict[str, List[Path]] = defaultdict(list)
        
        for file_path in files:
            parent_name = file_path.parent.name.strip().upper()
            buckets[parent_name].append(file_path)
        
        return buckets
    
    def _sort_files_by_directory_size(self, files: List[Path]) -> List[Path]:
        """Sort files by directory size (ascending) and then by filename."""
        buckets = self._group_files_by_directory(files)
        
        # Sort directories by number of files, then by name
        ordered_parent_names = sorted(
            buckets.keys(), 
            key=lambda k: (len(buckets[k]), k)
        )
        
        ordered_files: List[Path] = []
        for parent in ordered_parent_names:
            ordered_files.extend(sorted(buckets[parent]))
        
        return ordered_files
    
    def _get_folder_statistics(self, files: List[Path]) -> OrderedDict[str, int]:
        """Get statistics about files grouped by folder."""
        folder_counts: OrderedDict[str, int] = OrderedDict()
        
        for file_path in files:
            folder_name = file_path.parent.name
            folder_counts[folder_name] = folder_counts.get(folder_name, 0) + 1
        
        return folder_counts
