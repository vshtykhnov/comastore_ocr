# ComaStore OCR

OCR system for analyzing product images and classifying them by promotion types.

## Installation

### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -e .
```

## Usage

### Process Images
Generate labels for images in directory:
```bash
python -m comastore_ocr.cli process
```

### Sort Images
Sort images using Tesseract + rules:
```bash
python -m comastore_ocr.cli sort
```

## Configuration

All commands use sensible defaults:
- **Data directory**: `train_data` or `out/sorted` (if exists)
- **Engine**: `openai`
- **Language**: `pol` (Polish)
- **Output**: `out/sorted` for sorting

## Environment Variables

- `DATA_DIR`: Override default data directory
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o-mini)
- `OPENAI_MAX_TOKENS`: Max tokens for OpenAI responses (default: 120)
