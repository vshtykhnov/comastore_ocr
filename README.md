## ComaStore OCR

Utilities to extract structured labels from retail promotion images.

### Features

- OpenAI-based vision extraction via pluggable engines
- Tesseract OCR + rule-based textual sorter
- Validates labels with a strict schema

### Project layout

- `src/comastore_ocr/`: library and CLI
  - `config.py`: paths and runtime settings (`DATA_DIR`, model)
  - `engines/`: pluggable backends for label generation
    - `openai_engine.py`: OpenAI-powered engine (default)
    - `base.py`: engine interface
  - `prompts.py`: system prompt for vision extraction
  - `openai_utils.py`: low-level OpenAI chat wrapper used by the OpenAI engine
  - `processing.py`: iterate images, call selected engine, save `<image>.json`
  - `sort_textual.py`: Tesseract OCR + rule-based classifier for manual grouping
  - `validation.py`: JSON schema checks for labels
  - `image_utils.py`: image → data URI helpers
  - `train_data/`: images and generated JSON labels

### Installation

```bash
pip install -e .
```

Environment variable `OPENAI_API_KEY` must be set.
You can put it in `.env` at the repo root or in `comastore_ocr/.env`, e.g.:

```
OPENAI_API_KEY=sk-...
```

Optional environment variables:

- `DATA_DIR` (default: `./train_data`)
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `OPENAI_MAX_TOKENS` (default: 120) — cap on response tokens

### Usage (CLI)

Process images and generate `<image>.json` labels. You can choose an engine; currently supported: `openai` (default).

Windows PowerShell (from the repo root):

```powershell
python -m comastore_ocr.cli process-images --data-dir comastore_ocr\train_data --engine openai
```

Windows PowerShell (from the `comastore_ocr` folder):

```powershell
cd comastore_ocr
python -m comastore_ocr.cli process-images --engine openai
```

Sort images by textual rules (requires Tesseract with Polish language installed):

```powershell
python -m comastore_ocr.cli sort-text --data-dir comastore_ocr\train_data --out comastore_ocr\out\sorted --lang pol
```

If you installed the package:

```powershell
comastore-ocr process-images --data-dir comastore_ocr\train_data --engine openai
```

### Notes

- Adjust `DATA_DIR` if your dataset directory differs.
- Install Tesseract OCR and Polish language pack (e.g., Windows installer + `pol` traineddata).
- The tool waits only when API returns 429 and honors Retry-After.
