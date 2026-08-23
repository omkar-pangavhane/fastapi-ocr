"""
Upload validation helpers: extension/MIME checks, size limits, and
safe image loading.
"""
import io
from typing import Tuple

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.core.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    InvalidFileTypeError,
    UnreadableImageError,
)

settings = get_settings()

# Map extensions to acceptable MIME type prefixes/values for a defense-in-depth check.
_MIME_BY_EXT = {
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "png": {"image/png"},
    "tiff": {"image/tiff"},
    "tif": {"image/tiff"},
    "bmp": {"image/bmp", "image/x-ms-bmp"},
}


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def validate_extension(filename: str) -> str:
    ext = get_extension(filename)
    if ext not in settings.allowed_extensions_list:
        raise InvalidFileTypeError(filename, settings.allowed_extensions_list)
    return ext


def validate_content_type(filename: str, content_type: str, ext: str) -> None:
    """Best-effort MIME check. Browsers/clients can send generic types, so we
    only hard-fail on a clear mismatch (e.g. a .png that is declared text/html)."""
    if not content_type:
        return
    allowed = _MIME_BY_EXT.get(ext, set())
    if content_type == "application/octet-stream":
        return  # generic type, fall back to magic-byte check via PIL
    if allowed and content_type not in allowed:
        raise InvalidFileTypeError(filename, settings.allowed_extensions_list)


async def read_and_validate_upload(file: UploadFile) -> Tuple[bytes, str]:
    """
    Validate extension, content-type, and size for an UploadFile, then
    read and return its raw bytes along with the validated extension.
    """
    filename = file.filename or "unnamed_file"
    ext = validate_extension(filename)
    validate_content_type(filename, file.content_type or "", ext)

    contents = await file.read()
    if not contents:
        raise EmptyFileError(filename)
    if len(contents) > settings.max_file_size_bytes:
        raise FileTooLargeError(filename, settings.MAX_FILE_SIZE_MB)

    return contents, ext


def load_image(contents: bytes, filename: str) -> Image.Image:
    """Safely load raw bytes into a PIL Image, verifying it's a real image
    (protects against disguised/malicious files) before returning a usable copy."""
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # checks integrity; leaves the file object unusable afterwards
        # Re-open because verify() closes the file pointer / renders it unusable
        image = Image.open(io.BytesIO(contents))
        image.load()
        return image
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise UnreadableImageError(filename, str(exc)) from exc
