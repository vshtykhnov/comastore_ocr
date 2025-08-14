"""File sorter class for handling file sorting based on OCR text classification."""

import shutil
from pathlib import Path
from typing import List, Dict, Optional

from .text_classifier import TextClassifier
from ..local_ocr.text_ocr import ocr_image_to_text


class FileSorter:
    """Handles file sorting based on OCR text classification."""
    
    def __init__(
        self, 
        allowed_extensions: set,
        tesseract_lang: str = "pol",
        dump_text: bool = True
    ):
        self.allowed_extensions = allowed_extensions
        self.tesseract_lang = tesseract_lang
        self.dump_text = dump_text
        self.classifier = TextClassifier()
        
        # Statistics
        self.copied_count = 0
        self.skipped_count = 0
        self.unknown_count = 0
        self.pre_skipped_count = 0
    
    def find_images_in_directory(self, data_dir: Path) -> List[Path]:
        """Find all images in the specified directory."""
        return [
            p for p in sorted(data_dir.iterdir()) 
            if self._is_image_file(p)
        ]
    
    def get_existing_outputs(self, out_root: Path) -> set:
        """Get set of filenames that already exist in output directories."""
        existing_names: set = set()
        
        for promo_dir in out_root.iterdir():
            if promo_dir.is_dir() and promo_dir.name != "_ocr_text":
                for file_path in promo_dir.iterdir():
                    if file_path.is_file():
                        existing_names.add(file_path.name)
        
        return existing_names
    
    def filter_images_to_process(
        self, 
        images: List[Path], 
        existing_names: set
    ) -> List[Path]:
        """Filter images to only those that need processing."""
        return [
            img for img in images 
            if img.name not in existing_names
        ]
    
    def setup_output_directories(self, out_root: Path) -> Optional[Path]:
        """Setup output directories and return text dump directory if needed."""
        self._ensure_directory_exists(out_root)
        
        if self.dump_text:
            text_dump_dir = out_root / "_ocr_text"
            self._ensure_directory_exists(text_dump_dir)
            return text_dump_dir
        
        return None
    
    def get_ocr_text(
        self, 
        image_path: Path, 
        text_dump_dir: Optional[Path] = None
    ) -> str:
        """Get OCR text for image, optionally using cached text dump."""
        if text_dump_dir:
            dump_file = text_dump_dir / f"{image_path.stem}.txt"
            
            if dump_file.exists():
                return dump_file.read_text(encoding="utf-8")
            else:
                text = ocr_image_to_text(image_path, lang=self.tesseract_lang)
                dump_file.write_text(text, encoding="utf-8")
                return text
        else:
            return ocr_image_to_text(image_path, lang=self.tesseract_lang)
    
    def copy_image_to_category(
        self, 
        image_path: Path, 
        category: str, 
        out_root: Path
    ) -> bool:
        """Copy image to appropriate category directory."""
        try:
            dst_dir = out_root / category
            self._ensure_directory_exists(dst_dir)
            
            dest_img = dst_dir / image_path.name
            if dest_img.exists():
                print(f"[SKIP] Exists: {dest_img}")
                self.skipped_count += 1
                return False
            
            shutil.copy2(image_path, dest_img)
            self.copied_count += 1
            return True
            
        except Exception as e:
            print(f"⚠️  Error copying {image_path.name}: {e}")
            return False
    
    def process_image(
        self, 
        image_path: Path, 
        index: int, 
        total: int,
        out_root: Path,
        text_dump_dir: Optional[Path] = None
    ) -> None:
        """Process a single image for sorting."""
        prefix = f"[{index}/{total} | left {total - index}]"
        
        # Get OCR text
        text = self.get_ocr_text(image_path, text_dump_dir)
        
        # Classify text
        promo = self.classifier.classify_text(text)
        if promo is None:
            print(f"{prefix} [WARN] Could not classify: {image_path.name}")
            promo = "UNKNOWN"
            self.unknown_count += 1
        
        # Copy to category directory
        if self.copy_image_to_category(image_path, promo, out_root):
            print(f"{prefix} Copied -> {out_root / promo / image_path.name}")
    
    def sort_files(
        self, 
        data_dir: Path, 
        out_root: Path
    ) -> Dict:
        """Main method to sort files based on OCR classification."""
        if not data_dir.exists():
            raise FileNotFoundError(f"Directory {data_dir} not found")
        
        # Setup
        text_dump_dir = self.setup_output_directories(out_root)
        
        # Find images
        images = self.find_images_in_directory(data_dir)
        if not images:
            print("ℹ️  No images found to sort.")
            return self._get_statistics()
        
        # Check existing outputs
        existing_names = self.get_existing_outputs(out_root)
        images_to_process = self.filter_images_to_process(images, existing_names)
        
        self.pre_skipped_count = len(images) - len(images_to_process)
        if self.pre_skipped_count:
            print(f"ℹ️  Pre-skip: {self.pre_skipped_count} already present in output. Will process {len(images_to_process)}.")
        
        # Process images
        total = len(images_to_process)
        for index, img in enumerate(images_to_process, start=1):
            self.process_image(img, index, total, out_root, text_dump_dir)
        
        # Print summary
        self._print_summary(out_root)
        return self._get_statistics()
    
    def _print_summary(self, out_root: Path) -> None:
        """Print processing summary."""
        print(
            f"Done. Processed {len(images_to_process)} images (pre-skipped {self.pre_skipped_count}). "
            f"Copied {self.copied_count}. Unknown: {self.unknown_count}. Output: {out_root}"
        )
    
    def _get_statistics(self) -> Dict:
        """Get processing statistics."""
        return {
            "copied": self.copied_count,
            "skipped": self.skipped_count,
            "unknown": self.unknown_count,
            "pre_skipped": self.pre_skipped_count
        }
    
    def _is_image_file(self, file_path: Path) -> bool:
        """Check if file is an image based on extension."""
        return file_path.is_file() and file_path.suffix.lower() in self.allowed_extensions
    
    def _ensure_directory_exists(self, directory: Path) -> None:
        """Ensure directory exists, creating parent directories if needed."""
        directory.mkdir(parents=True, exist_ok=True)
