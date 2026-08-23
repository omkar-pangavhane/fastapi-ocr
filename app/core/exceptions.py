"""
Custom exception types and their FastAPI exception handlers.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse


class OCRBaseException(Exception):
    """Base exception for all OCR-API specific errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidFileTypeError(OCRBaseException):
    def __init__(self, filename: str, allowed: list):
        message = f"'{filename}' has an unsupported file type. Allowed types: {', '.join(allowed)}"
        super().__init__(message, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class FileTooLargeError(OCRBaseException):
    def __init__(self, filename: str, max_mb: int):
        message = f"'{filename}' exceeds the maximum allowed size of {max_mb}MB"
        super().__init__(message, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class EmptyFileError(OCRBaseException):
    def __init__(self, filename: str):
        super().__init__(f"'{filename}' is empty", status.HTTP_400_BAD_REQUEST)


class UnreadableImageError(OCRBaseException):
    def __init__(self, filename: str, detail: str = ""):
        message = f"Could not read '{filename}' as an image"
        if detail:
            message += f": {detail}"
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class UnsupportedLanguageError(OCRBaseException):
    def __init__(self, lang: str):
        super().__init__(
            f"Language code '{lang}' is not installed on this server. "
            f"Check GET /api/v1/ocr/languages for available options.",
            status.HTTP_400_BAD_REQUEST,
        )


class OCREngineError(OCRBaseException):
    def __init__(self, detail: str):
        super().__init__(f"OCR engine failed: {detail}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class TooManyFilesError(OCRBaseException):
    def __init__(self, max_files: int):
        super().__init__(
            f"Too many files in one batch request. Maximum allowed is {max_files}",
            status.HTTP_400_BAD_REQUEST,
        )


async def ocr_exception_handler(request: Request, exc: OCRBaseException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "path": str(request.url.path),
        },
    )
