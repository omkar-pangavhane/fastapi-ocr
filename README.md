# OCR Extraction API

A production-ready FastAPI service for extracting text from images using Tesseract OCR, with an OpenCV/Pillow preprocessing pipeline, multi-language support, and batch processing.

## Features

- **Multi-format uploads**: JPG, JPEG, PNG, TIFF, BMP
- **10MB file size limit** (configurable) with strict validation (extension, MIME, magic-byte image verification)
- **Image preprocessing**: grayscale, denoising, adaptive/Otsu thresholding, auto-upscaling of small images
- **Multi-language OCR**: any language pack installed on the Tesseract binary (English, Spanish, French, German, Hindi, Marathi, etc. — combine with `eng+fra`)
- **Confidence scoring**: per-word and average confidence, optional bounding boxes
- **Batch processing**: OCR multiple images in one request, with per-file success/failure isolation
- **Robust error handling**: typed exceptions → correct HTTP status codes (415, 413, 422, etc.)
- **Async endpoints**: OCR runs in a threadpool so the event loop stays responsive
- **Dockerized**: `Dockerfile` + `docker-compose.yml` included

## Project Structure

```
ocr-api/
├── app/
│   ├── main.py                  # FastAPI app, middleware, exception handlers
│   ├── api/v1/ocr.py             # Route handlers
│   ├── core/
│   │   ├── config.py             # Settings (env-driven)
│   │   └── exceptions.py         # Custom exceptions + handler
│   ├── models/schemas.py         # Pydantic request/response models
│   ├── services/
│   │   ├── ocr_service.py        # pytesseract wrapper, confidence parsing
│   │   └── preprocessing.py      # OpenCV preprocessing pipeline
│   └── utils/validators.py       # Upload validation, safe image loading
├── tests/test_ocr_api.py         # Pytest suite (8 tests, self-contained)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Setup

### 1. Install Tesseract OCR (system dependency)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-spa tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-hin tesseract-ocr-mar
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:** download the installer from the [UB-Mannheim Tesseract build](https://github.com/UB-Mannheim/tesseract/wiki), then set `TESSERACT_CMD` in `.env` to the full path of `tesseract.exe`.

### 2. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# edit .env if needed (e.g. TESSERACT_CMD on Windows)
```

### 4. Run

```bash
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs (Swagger) or http://127.0.0.1:8000/redoc

### Docker (alternative — bundles Tesseract, no local install needed)

```bash
docker-compose up --build
```

## API Reference

### `POST /api/v1/ocr/extract`
Upload a single image and get extracted text back.

**Query params:**
| Param | Default | Description |
|---|---|---|
| `lang` | `eng` | Tesseract language code(s), e.g. `eng`, `spa`, `eng+fra` |
| `preprocessing` | `auto` | `none`, `auto`, `document`, `low_quality` |
| `include_word_boxes` | `false` | Include per-word bounding boxes + confidence |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract?lang=eng&preprocessing=auto" \
  -F "file=@invoice.jpg"
```

**Response:**
```json
{
  "filename": "invoice.jpg",
  "success": true,
  "extracted_text": "INVOICE #1042\nDate: 12 Mar 2026\n...",
  "average_confidence": 91.42,
  "word_count": 38,
  "language": "eng",
  "preprocessing_applied": "auto",
  "processing_time_ms": 214.7,
  "words": null,
  "error": null
}
```

### `POST /api/v1/ocr/extract-batch`
Same as above but accepts multiple files (`files` field, repeated). One failing file does not fail the whole batch — check `results[i].success`.

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract-batch" \
  -F "files=@page1.png" -F "files=@page2.png" -F "files=@page3.png"
```

### `GET /api/v1/ocr/languages`
Returns Tesseract language packs actually installed on the server (not a hardcoded list), so you always know what's usable.

### `GET /api/v1/ocr/health`
Checks that the Tesseract binary is reachable and returns its version — use this for container/readiness probes.

## Preprocessing Modes

| Mode | What it does | Best for |
|---|---|---|
| `none` | No preprocessing, raw image sent to Tesseract | Already-clean digital screenshots |
| `auto` | Grayscale + Otsu thresholding + upscale if small | General purpose (default) |
| `document` | Grayscale + adaptive thresholding | Scanned documents with uneven lighting |
| `low_quality` | Denoise + adaptive thresholding | Photos of text, noisy/low-res images |

## Error Handling

All errors return a consistent JSON shape:
```json
{ "success": false, "error": "description", "path": "/api/v1/ocr/extract" }
```

| Status | Meaning |
|---|---|
| 400 | Empty file, unsupported language, too many batch files |
| 413 | File exceeds `MAX_FILE_SIZE_MB` |
| 415 | Unsupported file extension/type |
| 422 | File isn't a valid/readable image |
| 500 | Tesseract engine failure |

## Testing

```bash
pytest tests/ -v
```

The test suite generates its own synthetic test images with PIL, so it has no external file dependencies and runs anywhere Tesseract is installed.

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `MAX_FILE_SIZE_MB` | `10` | Per-file upload limit |
| `ALLOWED_EXTENSIONS` | `jpg,jpeg,png,tiff,tif,bmp` | Accepted extensions |
| `TESSERACT_CMD` | *(empty)* | Path to tesseract binary (needed on Windows) |
| `DEFAULT_OCR_LANGUAGE` | `eng` | Default `lang` query value |
| `MAX_BATCH_FILES` | `10` | Max files per batch request |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |

## Notes on Production Hardening

- Uploads are verified as genuine images (`Image.verify()`) before processing, not just trusted by extension — protects against disguised/malicious files.
- OCR runs via `run_in_threadpool` so CPU-bound Tesseract calls don't block the async event loop.
- Batch endpoint processes files concurrently and isolates per-file failures.
- For heavy production load, consider adding a task queue (Celery/RQ) for batch jobs, rate limiting, and an API key/auth layer — not included here to keep the service dependency-light, but the router structure makes it straightforward to add.
