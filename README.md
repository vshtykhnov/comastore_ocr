## ComaStore OCR

Utilities to extract structured labels from retail promotion images.

### Features

- Extracts structured labels from images using OpenAI vision models
- Validates labels with a strict schema

### Project layout

- `src/comastore_ocr/`: library and CLI
  - `config.py`: paths and runtime settings (`DATA_DIR`, model, rate limits)
  - `prompts.py`: system prompt for vision extraction
- `validation.py`: JSON schema checks for labels
- `image_utils.py`: image → data URI helpers
- `openai_utils.py`: OpenAI chat wrapper
- `processing.py`: iterate images, call model, save `<image>.json`
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

Process images and generate `<image>.json` labels:

```bash
comastore-ocr process-images --data-dir train_data
```

### Notes

- Adjust `DATA_DIR` if your dataset directory differs.
