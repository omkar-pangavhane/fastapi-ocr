"""
Pydantic models used for request validation and response serialization.
"""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PreprocessingMode(str, Enum):
    NONE = "none"
    AUTO = "auto"
    DOCUMENT = "document"  # grayscale + adaptive threshold, good for scanned docs
    LOW_QUALITY = "low_quality"  # + denoise, good for noisy photos


class WordBox(BaseModel):
    text: str
    confidence: float = Field(..., ge=0, le=100)
    left: int
    top: int
    width: int
    height: int


class OCRResult(BaseModel):
    filename: str
    success: bool
    extracted_text: str = ""
    average_confidence: float = Field(0.0, ge=0, le=100)
    word_count: int = 0
    language: str = "eng"
    preprocessing_applied: PreprocessingMode = PreprocessingMode.AUTO
    processing_time_ms: float = 0.0
    words: Optional[List[WordBox]] = None
    error: Optional[str] = None


class BatchOCRResponse(BaseModel):
    success: bool
    total_files: int
    successful: int
    failed: int
    total_processing_time_ms: float
    results: List[OCRResult]


class LanguageInfo(BaseModel):
    code: str
    name: str


class LanguagesResponse(BaseModel):
    default_language: str
    available_languages: List[LanguageInfo]
    total_installed: int


class HealthResponse(BaseModel):
    status: str
    tesseract_available: bool
    tesseract_version: Optional[str] = None
    app_version: str
