"""Common helper functions for the ComaStore OCR project."""

import time
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict, OrderedDict


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format."""
    seconds = int(seconds)
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def calculate_eta(elapsed_time: float, processed_items: int, total_items: int) -> Optional[float]:
    """Calculate estimated time remaining for processing."""
    if processed_items == 0:
        return None
    
    remaining_items = total_items - processed_items
    if remaining_items <= 0:
        return 0.0
    
    avg_time_per_item = elapsed_time / processed_items
    return avg_time_per_item * remaining_items


def group_files_by_directory(files: List[Path]) -> Dict[str, List[Path]]:
    """Group files by their parent directory name."""
    buckets: Dict[str, List[Path]] = defaultdict(list)
    
    for file_path in files:
        parent_name = file_path.parent.name.strip().upper()
        buckets[parent_name].append(file_path)
    
    return buckets


def sort_files_by_directory_size(files: List[Path]) -> List[Path]:
    """Sort files by directory size (ascending) and then by filename."""
    buckets = group_files_by_directory(files)
    
    # Sort directories by number of files, then by name
    ordered_parent_names = sorted(
        buckets.keys(), 
        key=lambda k: (len(buckets[k]), k)
    )
    
    ordered_files: List[Path] = []
    for parent in ordered_parent_names:
        ordered_files.extend(sorted(buckets[parent]))
    
    return ordered_files


def get_folder_statistics(files: List[Path]) -> OrderedDict[str, int]:
    """Get statistics about files grouped by folder."""
    folder_counts: OrderedDict[str, int] = OrderedDict()
    
    for file_path in files:
        folder_name = file_path.parent.name
        folder_counts[folder_name] = folder_counts.get(folder_name, 0) + 1
    
    return folder_counts


def format_progress_message(
    current: int, 
    total: int, 
    filename: str, 
    additional_info: str = ""
) -> str:
    """Format a progress message with current/total and filename."""
    progress_pct = round(current / total * 100, 1)
    base_msg = f"[{current}/{total} | {progress_pct}%] → Processing {filename}"
    
    if additional_info:
        base_msg += f" {additional_info}"
    
    return base_msg + "…"


def ensure_directory_exists(directory: Path) -> None:
    """Ensure directory exists, creating parent directories if needed."""
    directory.mkdir(parents=True, exist_ok=True)


def is_image_file(file_path: Path, allowed_extensions: set) -> bool:
    """Check if file is an image based on extension."""
    return file_path.is_file() and file_path.suffix.lower() in allowed_extensions


def has_json_pair(file_path: Path) -> bool:
    """Check if file has a corresponding JSON file."""
    json_path = file_path.with_suffix(".json")
    return json_path.exists()


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    """Get relative path from base path."""
    return file_path.relative_to(base_path)
