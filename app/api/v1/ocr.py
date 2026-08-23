"""
OCR API routes:
  POST /api/v1/ocr/extract         - single image OCR
  POST /api/v1/ocr/extract-batch   - multiple images OCR
  GET  /api/v1/ocr/languages       - list installed Tesseract languages
  GET  /api/v1/ocr/health          - health / readiness check
"""
import asyncio
import time

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.core.exceptions import OCRBaseException, OCREngineError, TooManyFilesError
from app.models.schemas import (
    BatchOCRResponse,
    HealthResponse,
    LanguageInfo,
    LanguagesResponse,
    OCRResult,
    PreprocessingMode,
)
from app.services import ocr_service
from app.utils.validators import load_image, read_and_validate_upload

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    version = await run_in_threadpool(ocr_service.get_tesseract_version)
    return HealthResponse(
        status="ok" if version else "degraded",
        tesseract_available=version is not None,
        tesseract_version=version,
        app_version=settings.APP_VERSION,
    )


@router.get("/languages", response_model=LanguagesResponse, summary="List available OCR languages")
async def list_languages() -> LanguagesResponse:
    try:
        codes = await run_in_threadpool(ocr_service.get_installed_languages)
    except OCRBaseException:
        return LanguagesResponse(
            default_language=settings.DEFAULT_OCR_LANGUAGE,
            available_languages=[],
            total_installed=0,
        )

    languages = [
        LanguageInfo(code=code, name=ocr_service.LANGUAGE_NAMES.get(code, code.title()))
        for code in codes
        if code != "osd"
    ]
    return LanguagesResponse(
        default_language=settings.DEFAULT_OCR_LANGUAGE,
        available_languages=languages,
        total_installed=len(languages),
    )


async def _process_single_upload(
    file: UploadFile,
    lang: str,
    preprocessing: PreprocessingMode,
    include_word_boxes: bool,
    raise_on_error: bool = False,
) -> OCRResult:
    """
    Run the OCR pipeline for one upload.
    - raise_on_error=True (used by /extract): lets OCRBaseException propagate
      so FastAPI returns the correct HTTP status code (415, 413, 422, etc).
    - raise_on_error=False (used by /extract-batch): swallows errors into the
      OCRResult so one bad file doesn't fail the whole batch.
    """
    filename = file.filename or "unnamed_file"
    try:
        contents, _ext = await read_and_validate_upload(file)
        image = await run_in_threadpool(load_image, contents, filename)
        result = await run_in_threadpool(
            ocr_service.extract_text,
            image,
            filename,
            lang,
            preprocessing,
            include_word_boxes,
        )
        return result
    except OCRBaseException as exc:
        if raise_on_error and not isinstance(exc, OCREngineError):
            raise
        return OCRResult(filename=filename, success=False, error=exc.message, language=lang)


@router.post(
    "/extract",
    response_model=OCRResult,
    summary="Extract text from a single uploaded image",
)
async def extract_text(
    file: UploadFile = File(..., description="Image file (jpg, jpeg, png, tiff, bmp)"),
    lang: str = Query(
        default=settings.DEFAULT_OCR_LANGUAGE,
        description="Tesseract language code, or '+' joined for multiple e.g. 'eng+fra'",
    ),
    preprocessing: PreprocessingMode = Query(
        default=PreprocessingMode.AUTO,
        description="Preprocessing pipeline to apply before OCR",
    ),
    include_word_boxes: bool = Query(
        default=False, description="Include per-word bounding boxes and confidences"
    ),
) -> OCRResult:
    return await _process_single_upload(
        file, lang, preprocessing, include_word_boxes, raise_on_error=True
    )


@router.post(
    "/extract-batch",
    response_model=BatchOCRResponse,
    summary="Extract text from multiple uploaded images",
)
async def extract_text_batch(
    files: list[UploadFile] = File(..., description="Multiple image files"),
    lang: str = Query(default=settings.DEFAULT_OCR_LANGUAGE),
    preprocessing: PreprocessingMode = Query(default=PreprocessingMode.AUTO),
    include_word_boxes: bool = Query(default=False),
) -> BatchOCRResponse:
    if len(files) > settings.MAX_BATCH_FILES:
        raise TooManyFilesError(settings.MAX_BATCH_FILES)

    start = time.perf_counter()
    tasks = [
        _process_single_upload(f, lang, preprocessing, include_word_boxes) for f in files
    ]
    results = await asyncio.gather(*tasks)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    successful = sum(1 for r in results if r.success)
    return BatchOCRResponse(
        success=successful > 0,
        total_files=len(results),
        successful=successful,
        failed=len(results) - successful,
        total_processing_time_ms=elapsed_ms,
        results=list(results),
    )
