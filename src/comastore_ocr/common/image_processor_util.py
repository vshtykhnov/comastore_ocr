"""Image processor utility class for enhanced image processing."""

from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image


class ImageProcessorUtil:
    """Enhanced image processing utilities."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
    MAX_SIZE = (4096, 4096)  # Maximum dimensions for processing
    
    @staticmethod
    def is_supported_format(file_path: Path) -> bool:
        """Check if image format is supported."""
        return file_path.suffix.lower() in ImageProcessorUtil.SUPPORTED_FORMATS
    
    @staticmethod
    def get_image_info(file_path: Path) -> Dict:
        """Get comprehensive image information."""
        try:
            with Image.open(file_path) as img:
                info = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": round(img.width / img.height, 3),
                    "file_size": file_path.stat().st_size,
                    "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
                }
                
                # Add color information if available
                if hasattr(img, 'getcolors'):
                    colors = img.getcolors()
                    info["unique_colors"] = len(colors) if colors else "Unknown"
                
                return info
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def resize_image(
        file_path: Path, 
        max_size: Tuple[int, int] = None,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Resize image to fit within maximum dimensions."""
        max_size = max_size or ImageProcessorUtil.MAX_SIZE
        
        try:
            with Image.open(file_path) as img:
                # Calculate new size maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Determine output path
                if output_path is None:
                    output_path = file_path.parent / f"{file_path.stem}_resized{file_path.suffix}"
                
                # Save resized image
                img.save(output_path, quality=95, optimize=True)
                return output_path
                
        except Exception as e:
            print(f"Error resizing image {file_path}: {e}")
            return None
    
    @staticmethod
    def convert_format(
        file_path: Path, 
        target_format: str, 
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Convert image to different format."""
        if target_format not in ImageProcessorUtil.SUPPORTED_FORMATS:
            print(f"Unsupported target format: {target_format}")
            return None
        
        try:
            with Image.open(file_path) as img:
                # Convert RGBA to RGB if saving as JPEG
                if target_format in {'.jpg', '.jpeg'} and img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Determine output path
                if output_path is None:
                    output_path = file_path.parent / f"{file_path.stem}.{target_format[1:]}"
                
                # Save in target format
                img.save(output_path, quality=95, optimize=True)
                return output_path
                
        except Exception as e:
            print(f"Error converting image {file_path}: {e}")
            return None
    
    @staticmethod
    def optimize_image(
        file_path: Path, 
        quality: int = 85,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Optimize image file size."""
        try:
            with Image.open(file_path) as img:
                # Determine output path
                if output_path is None:
                    output_path = file_path.parent / f"{file_path.stem}_optimized{file_path.suffix}"
                
                # Save with optimization
                img.save(output_path, quality=quality, optimize=True)
                return output_path
                
        except Exception as e:
            print(f"Error optimizing image {file_path}: {e}")
            return None
