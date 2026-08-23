"""
OCR service: wraps pytesseract, handles language validation,
confidence scoring, and structured word-level output.
"""
import time
from typing import List, Optional, Tuple

import pytesseract
from PIL import Image

from app.core.config import get_settings
from app.core.exceptions import OCREngineError, UnsupportedLanguageError
from app.models.schemas import OCRResult, PreprocessingMode, WordBox
from app.services.preprocessing import preprocess_image

settings = get_settings()

if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

# Human-readable names for common Tesseract language codes.
LANGUAGE_NAMES = {
    "eng": "English",
    "spa": "Spanish",
    "fra": "French",
    "deu": "German",
    "ita": "Italian",
    "por": "Portuguese",
    "nld": "Dutch",
    "rus": "Russian",
    "chi_sim": "Chinese (Simplified)",
    "chi_tra": "Chinese (Traditional)",
    "jpn": "Japanese",
    "kor": "Korean",
    "ara": "Arabic",
    "hin": "Hindi",
    "mar": "Marathi",
    "ben": "Bengali",
    "tur": "Turkish",
    "vie": "Vietnamese",
    "tha": "Thai",
    "pol": "Polish",
    "ukr": "Ukrainian",
    "osd": "Orientation & Script Detection (internal)",
}


def get_installed_languages() -> List[str]:
    try:
        langs = pytesseract.get_languages(config="")
        return sorted(langs)
    except pytesseract.TesseractNotFoundError as exc:
        raise OCREngineError(
            "Tesseract binary not found. Install it and/or set TESSERACT_CMD."
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise OCREngineError(str(exc)) from exc


def validate_language(lang: str) -> None:
    """Raise if the requested language (or '+'-joined set) isn't installed."""
    requested = [code.strip() for code in lang.split("+") if code.strip()]
    if not requested:
        raise UnsupportedLanguageError(lang)
    installed = set(get_installed_languages())
    for code in requested:
        if code not in installed:
            raise UnsupportedLanguageError(code)


def get_tesseract_version() -> Optional[str]:
    try:
        return str(pytesseract.get_tesseract_version())
    except Exception:
        return None


def _run_tesseract(image: Image.Image, lang: str) -> Tuple[str, List[WordBox], float]:
    """
    Run pytesseract's image_to_data to get both text and per-word confidence.
    Returns (full_text, word_boxes, average_confidence).
    """
    try:
        data = pytesseract.image_to_data(
            image, lang=lang, output_type=pytesseract.Output.DICT
        )
    except pytesseract.TesseractNotFoundError as exc:
        raise OCREngineError(
            "Tesseract binary not found. Install it and/or set TESSERACT_CMD."
        ) from exc
    except pytesseract.TesseractError as exc:
        raise OCREngineError(str(exc)) from exc

    words: List[WordBox] = []
    confidences: List[float] = []
    text_lines: List[str] = []
    current_line: List[str] = []
    last_line_num = None

    n = len(data.get("text", []))
    for i in range(n):
        raw_text = data["text"][i].strip()
        conf_raw = data["conf"][i]
        try:
            conf = float(conf_raw)
        except (TypeError, ValueError):
            conf = -1.0

        line_num = data.get("line_num", [0] * n)[i]
        if last_line_num is not None and line_num != last_line_num:
            if current_line:
                text_lines.append(" ".join(current_line))
                current_line = []
        last_line_num = line_num

        if raw_text:
            current_line.append(raw_text)
            if conf >= 0:
                confidences.append(conf)
                words.append(
                    WordBox(
                        text=raw_text,
                        confidence=round(conf, 2),
                        left=int(data["left"][i]),
                        top=int(data["top"][i]),
                        width=int(data["width"][i]),
                        height=int(data["height"][i]),
                    )
                )

    if current_line:
        text_lines.append(" ".join(current_line))

    full_text = "\n".join(text_lines)
    avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    return full_text, words, avg_conf


def extract_text(
    image: Image.Image,
    filename: str,
    lang: str = "eng",
    preprocessing: PreprocessingMode = PreprocessingMode.AUTO,
    include_word_boxes: bool = False,
) -> OCRResult:
    """Run the full OCR pipeline on a single image and return a structured result."""
    start = time.perf_counter()

    validate_language(lang)
    processed_image = preprocess_image(image, preprocessing)
    full_text, words, avg_conf = _run_tesseract(processed_image, lang)

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return OCRResult(
        filename=filename,
        success=True,
        extracted_text=full_text,
        average_confidence=avg_conf,
        word_count=len(words),
        language=lang,
        preprocessing_applied=preprocessing,
        processing_time_ms=elapsed_ms,
        words=words if include_word_boxes else None,
    )
