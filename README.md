# 🔍 OCR Extraction API

A production-ready **FastAPI OCR service** for extracting text from images using **Tesseract OCR**, with OpenCV/Pillow preprocessing, multi-language support, confidence scoring, and batch processing.

![OCR](https://raw.githubusercontent.com/tesseract-ocr/tessdoc/main/images/tesseract.png)

## ✨ Features

* 📷 JPG, JPEG, PNG, TIFF & BMP support
* 🔐 File extension, MIME, size & image validation
* 🧠 OpenCV/Pillow image preprocessing
* 🌍 Multi-language OCR — English, Hindi, Marathi, French, German, Spanish & more
* 📊 Word-level & average confidence scoring
* 📦 Batch OCR with per-file failure isolation
* ⚡ Non-blocking OCR execution using FastAPI threadpool
* 🐳 Docker & Docker Compose support
* ❤️ Health-check endpoint
* 🧪 Pytest test suite
* 📚 Swagger & ReDoc API documentation

## 🏗️ Architecture

```text
                ┌───────────────┐
                │     Client    │
                │ Web / Postman │
                │     / cURL    │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │    FastAPI    │
                │   REST API    │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ File Validation│
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Preprocessing │
                │ OpenCV/Pillow │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Tesseract OCR │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ JSON Response │
                └───────────────┘
```

## 🛠️ Tech Stack

| Technology  | Purpose                       |
| ----------- | ----------------------------- |
| Python      | Backend                       |
| FastAPI     | REST API                      |
| Tesseract   | OCR Engine                    |
| Pytesseract | Tesseract Python wrapper      |
| OpenCV      | Image preprocessing           |
| Pillow      | Image processing & validation |
| Pydantic    | Data validation               |
| Pytest      | Testing                       |
| Docker      | Containerization              |

## 📂 Project Structure

```text
fastapi-ocr/
│
├── app/
│   ├── main.py
│   ├── api/v1/ocr.py
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── models/schemas.py
│   ├── services/
│   │   ├── ocr_service.py
│   │   └── preprocessing.py
│   └── utils/validators.py
│
├── tests/
│   └── test_ocr_api.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### 1. Install Tesseract

**Ubuntu / Debian**

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

**macOS**

```bash
brew install tesseract
```

**Windows**

Install Tesseract and configure the executable path:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 2. Setup Python

```bash
git clone <repository-url>
cd fastapi-ocr

python -m venv venv
```

**Windows**

```powershell
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## 🐳 Docker

Run the complete service with Docker:

```bash
docker-compose up --build
```

## 🔌 API Endpoints

| Method | Endpoint                    | Description                       |
| ------ | --------------------------- | --------------------------------- |
| `POST` | `/api/v1/ocr/extract`       | Extract text from one image       |
| `POST` | `/api/v1/ocr/extract-batch` | Extract text from multiple images |
| `GET`  | `/api/v1/ocr/languages`     | Get installed OCR languages       |
| `GET`  | `/api/v1/ocr/health`        | Check OCR service health          |

### Single Image OCR

```bash
curl -X POST \
"http://localhost:8000/api/v1/ocr/extract?lang=eng&preprocessing=auto" \
-F "file=@invoice.jpg"
```

Example response:

```json
{
  "filename": "invoice.jpg",
  "success": true,
  "extracted_text": "INVOICE #1042\nDate: 12 Mar 2026",
  "average_confidence": 91.42,
  "word_count": 38,
  "language": "eng",
  "preprocessing_applied": "auto",
  "processing_time_ms": 214.7
}
```

## 🧠 Preprocessing

| Mode          | Processing                 | Use Case          |
| ------------- | -------------------------- | ----------------- |
| `none`        | No processing              | Clean images      |
| `auto`        | Grayscale + Otsu + upscale | General OCR       |
| `document`    | Adaptive thresholding      | Scanned documents |
| `low_quality` | Denoising + thresholding   | Noisy images      |

## 🌍 Multi-language OCR

Use any language installed with Tesseract:

```text
eng
fra
deu
spa
hin
mar
```

Multiple languages:

```text
eng+fra
eng+hin
eng+mar
```

Check available languages:

```http
GET /api/v1/ocr/languages
```

## 🔒 Production Features

* Image authenticity verification using `Image.verify()`
* Configurable upload limits
* MIME + extension validation
* Consistent HTTP error responses
* Threadpool-based OCR execution
* Batch failure isolation
* Environment-based configuration
* Dockerized deployment
* Health/readiness endpoint

## 🧪 Testing

```bash
pytest tests/ -v
```

Tests use synthetic images generated with Pillow, so external test images are not required.

## 📈 Future Improvements

* JWT / API-key authentication
* Rate limiting
* Celery + Redis task queue
* PDF OCR
* Table extraction
* OCR result caching
* Prometheus monitoring
* OpenTelemetry
* CI/CD with GitHub Actions
* LLM-based OCR post-processing
* RAG pipeline integration

## 👨‍💻 Author

**Omkar Pangavhane**

Software Developer | Python Backend | AI & Generative AI

---

⭐ **If you find this project useful, consider giving it a star.**
