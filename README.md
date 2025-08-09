## ComaStore OCR

Utilities to generate and prepare training data from retail promotion images.

### Features

- Extracts structured labels from images using OpenAI vision models
- Validates labels with a strict schema
- Converts per-image JSON labels into a single JSONL file

### Project layout

- `src/comastore_ocr/`: library and CLI
  - `config.py`: paths and runtime settings (`DATA_DIR`, model, rate limits)
  - `prompts.py`: system prompt for vision extraction
  - `validation.py`: JSON schema checks for labels
  - `image_utils.py`: image → data URI helpers
  - `openai_utils.py`: OpenAI chat wrapper
  - `processing.py`: iterate images, call model, save `<image>.json`
  - `convert.py`: merge `train_data/*.json` → `training_data.jsonl`
- `scripts/`: optional module runners
  - `process_images.py`: process new images in `train_data/`
  - `convert_to_jsonl.py`: create `training_data.jsonl`
- `train_data/`: images and generated JSON labels

### Installation

```bash
pip install -e .
```

Environment variable `OPENAI_API_KEY` must be set.

Optional environment variables:

- `DATA_DIR` (default: `./train_data`)
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `OPENAI_MAX_RPM` (default: 500) and/or `REQUEST_PAUSE_SEC`

### Usage (CLI)

1. Process images and generate `<image>.json` labels

```bash
comastore-ocr process-images --data-dir train_data
```

2. Convert all labels to JSONL

```bash
comastore-ocr convert-jsonl --data-dir train_data --output training_data.jsonl
```

The JSONL format mirrors the previous behavior:

```
{"image_path": "images/<file>", "label": "<raw JSON string>"}
```

### Notes

- The refactor keeps behavior the same but organizes code into modules. Adjust `DATA_DIR` if your dataset directory differs.
