# 🔍 OCR Extraction API

> **Production-ready OCR REST API built with FastAPI and Tesseract OCR for extracting text from images with preprocessing, multi-language support, confidence scoring, and batch processing.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python\&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tesseract](https://img.shields.io/badge/Tesseract-OCR-4285F4)](https://github.com/tesseract-ocr/tesseract)
[![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?logo=opencv)](https://opencv.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker\&logoColor=white)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest)](https://pytest.org/)

---

## 📌 Overview

**OCR Extraction API** is a RESTful OCR service that converts text from images into structured JSON responses.

The API combines:

* **FastAPI** for high-performance REST endpoints
* **Tesseract OCR** for text recognition
* **OpenCV + Pillow** for image preprocessing
* **Pydantic** for request/response validation
* **Docker** for reproducible deployment
* **Pytest** for automated testing

The service is designed with production-oriented concerns such as file validation, image verification, configurable limits, error handling, asynchronous execution, batch processing, and health checks.

---

## 🖼️ Screenshots

### Swagger API Documentation

![Swagger API Documentation](docs/images/swagger-ui.png)

### OCR Extraction

![OCR Extraction](docs/images/ocr-extraction.png)

### OCR Response

![OCR JSON Response](docs/images/ocr-response.png)

> **Note:** Add your screenshots to `docs/images/` using the filenames above.

Recommended screenshots:

```text
docs/
└── images/
    ├── swagger-ui.png
    ├── ocr-extraction.png
    └── ocr-response.png
```

---

## ✨ Features

### 📁 Multi-format Image Upload

Supports common image formats:

* JPG
* JPEG
* PNG
* TIFF
* BMP

### 🔐 Strict File Validation

Uploaded files are validated using multiple layers:

* File extension validation
* MIME type validation
* File size validation
* Actual image verification using `Pillow.Image.verify()`
* Protection against files disguised with incorrect extensions

Default maximum file size:

```text
10 MB
```

The limit can be configured through environment variables.

---

### 🧠 Image Preprocessing

The API provides multiple preprocessing strategies to improve OCR quality.

Supported modes:

| Mode          | Processing                        | Recommended For               |
| ------------- | --------------------------------- | ----------------------------- |
| `none`        | No preprocessing                  | Clean digital images          |
| `auto`        | Grayscale + Otsu + upscaling      | General OCR                   |
| `document`    | Grayscale + adaptive thresholding | Scanned documents             |
| `low_quality` | Denoising + adaptive thresholding | Noisy / low-resolution images |

Processing pipeline:

```text
Input Image
     │
     ▼
Image Validation
     │
     ▼
Pillow / OpenCV
     │
     ├── Grayscale
     ├── Denoising
     ├── Thresholding
     └── Upscaling
     │
     ▼
Preprocessed Image
     │
     ▼
Tesseract OCR
     │
     ▼
Structured JSON Response
```

---

### 🌍 Multi-language OCR

The API supports any language installed in the Tesseract environment.

Examples:

```text
eng
spa
fra
deu
hin
mar
```

Multiple languages can also be combined:

```text
eng+fra
eng+hin
eng+mar
```

Check installed languages:

```http
GET /api/v1/ocr/languages
```

This endpoint dynamically reports the language packs installed on the server.

---

### 📊 Confidence Scoring

OCR responses include:

* Average confidence
* Word count
* Optional per-word confidence
* Optional bounding boxes

Example:

```json
{
  "average_confidence": 91.42,
  "word_count": 38
}
```

When requested, individual words can include their coordinates and confidence values.

---

### 📦 Batch OCR Processing

Process multiple images in a single request:

```http
POST /api/v1/ocr/extract-batch
```

Each file is processed independently.

Therefore:

```text
File 1 → Success
File 2 → Success
File 3 → Failed
File 4 → Success
```

A failure in one file does not cause the entire batch request to fail.

---

### ⚡ Async API Execution

OCR is CPU-intensive, so Tesseract execution is moved to a threadpool.

This prevents long-running OCR operations from blocking the FastAPI event loop.

Conceptually:

```text
HTTP Request
     │
     ▼
FastAPI Event Loop
     │
     ▼
Threadpool
     │
     ▼
Tesseract OCR
     │
     ▼
JSON Response
```

---

### 🐳 Docker Support

The project includes:

```text
Dockerfile
docker-compose.yml
```

Docker packages the application together with its required Tesseract environment, making deployment more reproducible.

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │       Client         │
                         │ Browser / Postman    │
                         │ / Frontend / cURL    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │    REST API Layer    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   File Validation    │
                         │ Extension / MIME /   │
                         │ Size / Image Verify  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Image Preprocessing  │
                         │ Pillow + OpenCV      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Tesseract OCR     │
                         │ Text Recognition     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ OCR Result Processing│
                         │ Confidence / Words / │
                         │ Bounding Boxes       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    JSON Response     │
                         └──────────────────────┘
```

---

## 📂 Project Structure

```text
fastapi-ocr/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       └── ocr.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── ocr_service.py
│   │   └── preprocessing.py
│   │
│   └── utils/
│       └── validators.py
│
├── tests/
│   └── test_ocr_api.py
│
├── docs/
│   └── images/
│       ├── swagger-ui.png
│       ├── ocr-extraction.png
│       └── ocr-response.png
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

* Python 3.10+
* Tesseract OCR
* pip
* Git

Docker can be used instead of installing Tesseract locally.

---

## 1. Install Tesseract OCR

### Ubuntu / Debian

```bash
sudo apt-get update

sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-hin \
    tesseract-ocr-mar
```

### macOS

```bash
brew install tesseract
brew install tesseract-lang
```

### Windows

Install Tesseract using a Windows-compatible Tesseract distribution.

Then configure:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

# 🐍 Python Setup

## 2. Clone the Repository

```bash
git clone <your-repository-url>

cd fastapi-ocr
```

---

## 3. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create `.env` from the example:

### Linux / macOS

```bash
cp .env.example .env
```

### Windows

```powershell
copy .env.example .env
```

Example:

```env
MAX_FILE_SIZE_MB=10

ALLOWED_EXTENSIONS=jpg,jpeg,png,tiff,tif,bmp

TESSERACT_CMD=

DEFAULT_OCR_LANGUAGE=eng

MAX_BATCH_FILES=10

CORS_ORIGINS=*
```

---

# ▶️ Run the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 📚 API Documentation

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger provides an interactive interface for testing the OCR endpoints directly from the browser.

---

# 🐳 Docker Setup

Docker provides an alternative setup that bundles the required OCR environment.

Build and start:

```bash
docker-compose up --build
```

Run in detached mode:

```bash
docker-compose up -d --build
```

Stop containers:

```bash
docker-compose down
```

---

# 🔌 API Reference

## 1. Extract Text

```http
POST /api/v1/ocr/extract
```

Extract text from a single image.

### Query Parameters

| Parameter            | Default | Description                            |
| -------------------- | ------- | -------------------------------------- |
| `lang`               | `eng`   | Tesseract language code                |
| `preprocessing`      | `auto`  | Preprocessing strategy                 |
| `include_word_boxes` | `false` | Return word-level boxes and confidence |

### cURL

```bash
curl -X POST \
"http://localhost:8000/api/v1/ocr/extract?lang=eng&preprocessing=auto" \
-F "file=@invoice.jpg"
```

### Example Response

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

---

# 📦 Batch OCR

```http
POST /api/v1/ocr/extract-batch
```

Process multiple images in one request.

### Example

```bash
curl -X POST \
"http://localhost:8000/api/v1/ocr/extract-batch" \
-F "files=@page1.png" \
-F "files=@page2.png" \
-F "files=@page3.png"
```

Each file produces an independent result.

---

# 🌍 Available Languages

```http
GET /api/v1/ocr/languages
```

Returns the Tesseract language packs installed on the server.

Example:

```json
{
  "languages": [
    "eng",
    "fra",
    "deu",
    "hin",
    "mar"
  ]
}
```

This avoids relying on a hardcoded language list.

---

# ❤️ Health Check

```http
GET /api/v1/ocr/health
```

The health endpoint verifies that the Tesseract OCR engine is reachable and returns its version.

Useful for:

* Docker health checks
* Kubernetes readiness probes
* Monitoring
* Deployment verification

---

# 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

The test suite generates synthetic test images using Pillow, so external image files are not required.

Example:

```text
tests/test_ocr_api.py

✓ Image upload validation
✓ Invalid image handling
✓ File size validation
✓ OCR extraction
✓ Language validation
✓ Batch processing
✓ Health endpoint
✓ Error handling
```

---

# ⚠️ Error Handling

The API uses consistent JSON error responses.

Example:

```json
{
  "success": false,
  "error": "description",
  "path": "/api/v1/ocr/extract"
}
```

### HTTP Status Codes

| Status | Meaning                                              |
| ------ | ---------------------------------------------------- |
| `400`  | Invalid request / unsupported language / batch limit |
| `413`  | File exceeds configured size limit                   |
| `415`  | Unsupported file type                                |
| `422`  | Invalid or unreadable image                          |
| `500`  | Tesseract OCR engine failure                         |

---

# ⚙️ Configuration

Configuration is environment-driven through `.env`.

| Variable               |                     Default | Description                    |
| ---------------------- | --------------------------: | ------------------------------ |
| `MAX_FILE_SIZE_MB`     |                        `10` | Maximum size per uploaded file |
| `ALLOWED_EXTENSIONS`   | `jpg,jpeg,png,tiff,tif,bmp` | Accepted image formats         |
| `TESSERACT_CMD`        |                       Empty | Tesseract executable path      |
| `DEFAULT_OCR_LANGUAGE` |                       `eng` | Default OCR language           |
| `MAX_BATCH_FILES`      |                        `10` | Maximum files per batch        |
| `CORS_ORIGINS`         |                         `*` | Allowed CORS origins           |

---

# 🔒 Production Hardening

This project includes several production-oriented safeguards.

### Image Verification

Images are verified using Pillow rather than trusting only the filename or extension.

```python
Image.verify()
```

This helps detect files that are not actually valid images.

---

### Upload Restrictions

Uploads are restricted using:

```text
Extension validation
        +
MIME validation
        +
File size validation
        +
Actual image verification
```

---

### Non-blocking OCR

Tesseract is CPU-intensive.

OCR operations are executed through a threadpool so that long-running OCR processing does not directly block the FastAPI event loop.

---

### Batch Failure Isolation

Each file in a batch is processed independently.

A single invalid image does not invalidate successful OCR results from other files.

---

# 📈 Production Scaling Considerations

For high-volume workloads, additional infrastructure can be introduced:

```text
                    ┌──────────────┐
                    │   Client     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          FastAPI       FastAPI       FastAPI
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Task Queue   │
                    │ Celery / RQ  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ OCR Workers  │
                    │  Tesseract   │
                    └──────────────┘
```

Potential additions:

* Celery / RQ
* Redis
* Rate limiting
* API authentication
* API keys
* Structured logging
* Metrics
* Distributed tracing
* Object storage
* Horizontal scaling
* Kubernetes deployment

These components are intentionally not included in the current implementation to keep the service lightweight and dependency-conscious.

---

# 🛠️ Tech Stack

| Technology        | Purpose                       |
| ----------------- | ----------------------------- |
| **Python**        | Backend development           |
| **FastAPI**       | REST API framework            |
| **Tesseract OCR** | Optical character recognition |
| **Pytesseract**   | Python wrapper for Tesseract  |
| **OpenCV**        | Image preprocessing           |
| **Pillow**        | Image loading and validation  |
| **Pydantic**      | Data validation               |
| **Pytest**        | Automated testing             |
| **Docker**        | Containerization              |
| **Uvicorn**       | ASGI server                   |

---

# 🔄 OCR Processing Flow

```text
                    Upload Image
                         │
                         ▼
                  Validate Request
                         │
                         ▼
                  Validate File
                  ┌──────┴──────┐
                  │             │
              Valid          Invalid
                  │             │
                  ▼             ▼
           Verify Image       HTTP Error
                  │
                  ▼
           Preprocessing
                  │
        ┌─────────┼─────────┐
        │         │         │
     Grayscale Denoise  Threshold
        │         │         │
        └─────────┼─────────┘
                  │
                  ▼
              Tesseract
                  │
                  ▼
          Extract Text + Data
                  │
        ┌─────────┼─────────┐
        │         │         │
       Text   Confidence  Boxes
        │         │         │
        └─────────┼─────────┘
                  │
                  ▼
             JSON Response
```

---

# 📋 Example Use Cases

This API can be used for:

* 📄 Invoice text extraction
* 🧾 Receipt processing
* 🪪 Document digitization
* 📑 Scanned document OCR
* 🏷️ Label and packaging text extraction
* 📷 Text extraction from photographs
* 🌐 Multi-language document processing
* 📦 Batch document processing
* 🔎 Searchable document pipelines
* 🤖 OCR preprocessing for AI/RAG systems

---

# 🔮 Future Improvements

Potential extensions include:

* [ ] JWT authentication
* [ ] API key authentication
* [ ] Rate limiting
* [ ] Celery + Redis task queue
* [ ] PostgreSQL metadata storage
* [ ] Object storage integration
* [ ] OCR result caching
* [ ] Structured logging
* [ ] Prometheus metrics
* [ ] OpenTelemetry tracing
* [ ] Kubernetes deployment
* [ ] CI/CD with GitHub Actions
* [ ] PDF OCR support
* [ ] Multi-page document processing
* [ ] Table extraction
* [ ] Layout-aware OCR
* [ ] LLM-based post-processing
* [ ] RAG pipeline integration

---

# 🎯 Project Goals

The primary goals of this project are:

1. Build a reliable OCR REST API.
2. Improve OCR accuracy through image preprocessing.
3. Support multiple languages.
4. Provide structured OCR metadata.
5. Handle invalid uploads safely.
6. Support batch processing.
7. Keep the API responsive during CPU-intensive OCR operations.
8. Make the application easy to run locally and in Docker.
9. Follow production-oriented backend engineering practices.

---

# 👨‍💻 Author

**Omkar Pangavhane**

Software Developer focused on **Python Backend, AI, and Generative AI Engineering**.

---

# ⭐ If You Find This Project Useful

If this project helped you understand OCR, FastAPI, image preprocessing, or backend engineering, consider giving the repository a ⭐.

---

## 📄 License

Add your preferred license to the repository, for example:

```text
MIT License
```

See `LICENSE` for details.
