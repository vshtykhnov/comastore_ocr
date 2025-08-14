"""Image encoder class for enhanced image encoding utilities."""

import base64
import mimetypes
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from .image_processor_util import ImageProcessorUtil


class ImageEncoder:
    """Enhanced image encoding utilities."""
    
    @staticmethod
    def encode_to_data_uri(file_path: Path, max_size: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """Encode image to data URI with optional resizing."""
        try:
            # Resize if needed
            if max_size:
                temp_path = ImageProcessorUtil.resize_image(file_path, max_size)
                if temp_path is None:
                    return None
                file_path = temp_path
            
            # Read and encode image
            with open(file_path, "rb") as f:
                image_data = f.read()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type is None:
                mime_type = "image/jpeg"  # Default fallback
            
            # Encode to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Clean up temporary file
            if max_size and temp_path and temp_path != file_path:
                temp_path.unlink()
            
            return f"data:{mime_type};base64,{base64_data}"
            
        except Exception as e:
            print(f"Error encoding image {file_path}: {e}")
            return None
    
    @staticmethod
    def encode_multiple_images(
        file_paths: List[Path], 
        max_size: Optional[Tuple[int, int]] = None
    ) -> Dict[Path, Optional[str]]:
        """Encode multiple images to data URIs."""
        results = {}
        
        for file_path in file_paths:
            results[file_path] = ImageEncoder.encode_to_data_uri(file_path, max_size)
        
        return results
