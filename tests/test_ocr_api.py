"""
Basic tests for the OCR API. Run with: pytest -v
Generates a synthetic image with known text using PIL so tests don't
depend on external fixture files.
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont

from app.main import app

client = TestClient(app)


def make_text_image(text: str = "Hello World 123") -> bytes:
    img = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((10, 35), text, fill="black", font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def test_health_check():
    response = client.get("/api/v1/ocr/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "tesseract_available" in body


def test_languages_endpoint():
    response = client.get("/api/v1/ocr/languages")
    assert response.status_code == 200
    body = response.json()
    assert "available_languages" in body
    assert body["total_installed"] >= 0


def test_languages_endpoint_handles_missing_tesseract(monkeypatch):
    from app.api.v1 import ocr as ocr_routes
    from app.core.exceptions import OCREngineError

    def raise_engine_error() -> None:
        raise OCREngineError("Tesseract binary not found")

    monkeypatch.setattr(ocr_routes.ocr_service, "get_installed_languages", raise_engine_error)
    response = client.get("/api/v1/ocr/languages")
    assert response.status_code == 200
    body = response.json()
    assert body["available_languages"] == []
    assert body["total_installed"] == 0


def test_extract_handles_missing_tesseract(monkeypatch):
    from app.api.v1 import ocr as ocr_routes
    from app.core.exceptions import OCREngineError

    def raise_engine_error(*args, **kwargs):
        raise OCREngineError("Tesseract binary not found")

    monkeypatch.setattr(ocr_routes.ocr_service, "extract_text", raise_engine_error)
    image_bytes = make_text_image("Hello World")
    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": ("test.png", image_bytes, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert "Tesseract binary not found" in body["error"]


def test_extract_valid_image():
    image_bytes = make_text_image("Hello World")
    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": ("test.png", image_bytes, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["filename"] == "test.png"
    assert "extracted_text" in body


def test_extract_rejects_bad_extension():
    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": ("test.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_extract_rejects_empty_file():
    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400


def test_extract_rejects_oversized_file(monkeypatch):
    import app.utils.validators as validators_module

    monkeypatch.setattr(validators_module.settings, "MAX_FILE_SIZE_MB", 0.0001)
    big_bytes = make_text_image() * 50
    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": ("big.png", big_bytes, "image/png")},
    )
    assert response.status_code == 413


def test_batch_extract():
    image_bytes = make_text_image("Batch Test")
    response = client.post(
        "/api/v1/ocr/extract-batch",
        files=[
            ("files", ("a.png", image_bytes, "image/png")),
            ("files", ("b.png", image_bytes, "image/png")),
        ],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_files"] == 2


def test_batch_extract_too_many_files():
    from app.core.config import get_settings

    settings = get_settings()
    image_bytes = make_text_image()
    files = [
        ("files", (f"{i}.png", image_bytes, "image/png"))
        for i in range(settings.MAX_BATCH_FILES + 1)
    ]
    response = client.post("/api/v1/ocr/extract-batch", files=files)
    assert response.status_code == 400
