"""Image validator class for enhanced image validation utilities."""

from pathlib import Path
from typing import Dict, List, Tuple

from .image_processor_util import ImageProcessorUtil


class ImageValidator:
    """Enhanced image validation utilities."""
    
    @staticmethod
    def validate_image_file(file_path: Path) -> Tuple[bool, List[str]]:
        """Validate image file comprehensively."""
        errors = []
        
        # Check if file exists
        if not file_path.exists():
            errors.append("File does not exist")
            return False, errors
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size == 0:
                errors.append("File is empty")
            elif file_size > 100 * 1024 * 1024:  # 100MB limit
                errors.append("File is too large (>100MB)")
        except Exception as e:
            errors.append(f"Could not check file size: {e}")
        
        # Check file extension
        if not ImageProcessorUtil.is_supported_format(file_path):
            errors.append(f"Unsupported file format: {file_path.suffix}")
        
        # Try to open image
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                # Check dimensions
                if img.width == 0 or img.height == 0:
                    errors.append("Image has zero dimensions")
                
                # Check if image is corrupted
                img.verify()
        except Exception as e:
            errors.append(f"Image is corrupted or cannot be opened: {e}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_directory(
        directory: Path, 
        recursive: bool = True
    ) -> Dict[Path, Tuple[bool, List[str]]]:
        """Validate all images in a directory."""
        results = {}
        
        if recursive:
            image_files = [f for f in directory.rglob("*") if ImageProcessorUtil.is_supported_format(f)]
        else:
            image_files = [f for f in directory.iterdir() if ImageProcessorUtil.is_supported_format(f)]
        
        for file_path in image_files:
            is_valid, errors = ImageValidator.validate_image_file(file_path)
            results[file_path] = (is_valid, errors)
        
        return results
