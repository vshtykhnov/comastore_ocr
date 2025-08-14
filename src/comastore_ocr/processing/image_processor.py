"""Image processor class for handling individual image processing."""

import json
import time
from pathlib import Path
from typing import Dict, Optional

from ..engines import get_engine


class ImageProcessor:
    """Handles image processing with retry logic and progress tracking."""
    
    def __init__(self, engine_name: str = "openai", max_retries: int = 5):
        self.engine = get_engine(engine_name)
        self.max_retries = max_retries
        self.start_time: Optional[float] = None
        self.processed_count = 0
        self.error_count = 0
    
    def start_processing(self) -> None:
        """Start processing session and record start time."""
        self.start_time = time.time()
        self.processed_count = 0
        self.error_count = 0
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics."""
        if self.start_time is None:
            return {}
        
        elapsed = time.time() - self.start_time
        return {
            "elapsed_time": elapsed,
            "elapsed_formatted": self._format_duration(elapsed),
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "success_rate": (self.processed_count / (self.processed_count + self.error_count)) * 100 if (self.processed_count + self.error_count) > 0 else 0
        }
    
    def process_single_image(
        self, 
        image_path: Path, 
        forced_promo: Optional[str] = None
    ) -> Optional[Dict]:
        """Process a single image with retry logic."""
        for attempt in range(1, self.max_retries + 1):
            try:
                label = self.engine.generate_label(
                    image_path, 
                    forced_promo=forced_promo
                )
                self.processed_count += 1
                return label
                
            except Exception as e:
                if attempt == self.max_retries:
                    self.error_count += 1
                    print(f"⚠️  Final error processing {image_path.name}: {e}")
                    return None
                
                print(f"⚠️  Error (attempt {attempt}/{self.max_retries}): {e}. Retrying...")
                time.sleep(0.5 * attempt)
        
        return None
    
    def save_label(self, image_path: Path, label: Dict) -> bool:
        """Save label to JSON file."""
        try:
            json_path = image_path.with_suffix(".json")
            self._ensure_directory_exists(json_path.parent)
            
            with json_path.open("w", encoding="utf-8") as handle:
                json.dump(label, handle, ensure_ascii=False, indent=2)
            
            print(f"💾 Saved {json_path.name}")
            return True
            
        except Exception as e:
            print(f"⚠️  Error saving label for {image_path.name}: {e}")
            return False
    
    def process_image_with_progress(
        self, 
        image_path: Path, 
        current_index: int, 
        total_count: int,
        forced_promo: Optional[str] = None
    ) -> bool:
        """Process image with progress information and ETA."""
        # Format progress message
        promo_note = f" promo={forced_promo}" if forced_promo else ""
        progress_msg = self._format_progress_message(
            current_index, 
            total_count, 
            image_path.name, 
            promo_note
        )
        print(progress_msg)
        
        # Process image
        label = self.process_single_image(image_path, forced_promo)
        if label is None:
            return False
        
        # Save label
        if not self.save_label(image_path, label):
            return False
        
        # Show ETA
        if self.start_time and current_index < total_count:
            elapsed = time.time() - self.start_time
            eta_sec = self._calculate_eta(elapsed, current_index, total_count)
            if eta_sec is not None:
                print(f"⌛ Estimated time remaining: {self._format_duration(eta_sec)}")
        
        return True
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable format."""
        seconds = int(seconds)
        minutes, secs = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours:
            return f"{hours}h {minutes}m {secs}s"
        if minutes:
            return f"{minutes}m {secs}s"
        return f"{secs}s"
    
    def _calculate_eta(self, elapsed_time: float, processed_items: int, total_items: int) -> Optional[float]:
        """Calculate estimated time remaining for processing."""
        if processed_items == 0:
            return None
        
        remaining_items = total_items - processed_items
        if remaining_items <= 0:
            return 0.0
        
        avg_time_per_item = elapsed_time / processed_items
        return avg_time_per_item * remaining_items
    
    def _format_progress_message(
        self, 
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
    
    def _ensure_directory_exists(self, directory: Path) -> None:
        """Ensure directory exists, creating parent directories if needed."""
        directory.mkdir(parents=True, exist_ok=True)
