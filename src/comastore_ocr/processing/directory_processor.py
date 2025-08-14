"""Main directory processing module that orchestrates image processing."""

from pathlib import Path
from typing import Dict

from .image_processor import ImageProcessor, PromoInferrer, ImageFileManager
from ..config import IMAGE_EXTENSIONS


class DirectoryProcessor:
    """Main orchestrator for processing images in a directory."""
    
    def __init__(self, engine_name: str = "openai", max_retries: int = 5):
        self.image_processor = ImageProcessor(engine_name, max_retries)
        self.promo_inferrer = PromoInferrer()
        self.file_manager = ImageFileManager(IMAGE_EXTENSIONS)
    
    def process_directory(self, data_dir: Path) -> Dict:
        """Process all images in the specified directory."""
        if not data_dir.exists():
            raise FileNotFoundError(f"Directory {data_dir} not found")
        
        # Find images to process
        images_to_process = self.file_manager.find_images_to_process(data_dir)
        
        total = len(images_to_process)
        if total == 0:
            print("🎉 All images are already processed — no new files.")
            return {"status": "completed", "message": "No images to process"}
        
        # Get processing summary
        summary = self.file_manager.get_processing_summary(images_to_process)
        if summary["order_preview"]:
            print(f"Order by folder (ascending): {summary['order_preview']}")
        
        # Start processing
        self.image_processor.start_processing()
        
        # Process each image
        for idx, image_path in enumerate(images_to_process, start=1):
            # Determine promo to use from folder inference
            effective_promo = self.promo_inferrer.infer_promo_from_parent(image_path)
            
            # Process image with progress tracking
            success = self.image_processor.process_image_with_progress(
                image_path, 
                idx, 
                total, 
                effective_promo
            )
            
            if not success:
                print(f"⚠️  Failed to process {image_path.name}")
        
        # Get final statistics
        stats = self.image_processor.get_processing_stats()
        
        print(f"\n✅ Processing completed!")
        print(f"📊 Statistics: {stats['processed_count']} processed, {stats['error_count']} errors")
        print(f"⏱️  Total time: {stats['elapsed_formatted']}")
        print(f"📈 Success rate: {stats['success_rate']:.1f}%")
        
        return {
            "status": "completed",
            "statistics": stats,
            "summary": summary
        }
    
    def get_processing_status(self) -> Dict:
        """Get current processing status."""
        return self.image_processor.get_processing_stats()
    
    def reset_processing_stats(self) -> None:
        """Reset processing statistics."""
        self.image_processor.start_processing()


def process_images_in_directory(
    data_dir: Path, 
    engine_name: str = "openai"
) -> Dict:
    """Convenience function to process images in a directory."""
    processor = DirectoryProcessor(engine_name)
    return processor.process_directory(data_dir)
