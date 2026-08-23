"""
Image preprocessing pipeline to improve OCR accuracy.

Techniques used:
- Grayscale conversion
- Denoising (fastNlMeansDenoising)
- Adaptive thresholding / binarization
- Deskewing is intentionally left out of "auto" (kept lightweight) but the
  hook is provided in `deskew()` for callers that want it.
"""
import cv2
import numpy as np
from PIL import Image

from app.models.schemas import PreprocessingMode


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """Convert a PIL image (any mode) into an OpenCV BGR ndarray."""
    rgb_image = image.convert("RGB")
    array = np.array(rgb_image)
    return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    """Convert an OpenCV BGR/gray ndarray back into a PIL image."""
    if len(image.shape) == 2:
        return Image.fromarray(image)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def to_grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(gray_image: np.ndarray, strength: int = 10) -> np.ndarray:
    return cv2.fastNlMeansDenoising(gray_image, None, strength, 7, 21)


def adaptive_threshold(gray_image: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        gray_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )


def otsu_threshold(gray_image: np.ndarray) -> np.ndarray:
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def deskew(gray_image: np.ndarray) -> np.ndarray:
    """Rotate the image so that its dominant text angle is horizontal."""
    coords = np.column_stack(np.where(gray_image < 255))
    if coords.size == 0:
        return gray_image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if abs(angle) < 0.5:
        return gray_image
    (h, w) = gray_image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        gray_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def upscale_if_small(gray_image: np.ndarray, min_dimension: int = 1000) -> np.ndarray:
    """Tesseract performs poorly on very small images; upscale if needed."""
    h, w = gray_image.shape[:2]
    if max(h, w) >= min_dimension:
        return gray_image
    scale = min_dimension / max(h, w)
    return cv2.resize(gray_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def preprocess_image(image: Image.Image, mode: PreprocessingMode) -> Image.Image:
    """
    Apply a preprocessing pipeline to a PIL image and return a PIL image
    ready to be handed to pytesseract.
    """
    if mode == PreprocessingMode.NONE:
        return image

    cv_image = pil_to_cv2(image)
    gray = to_grayscale(cv_image)
    gray = upscale_if_small(gray)

    if mode == PreprocessingMode.AUTO:
        gray = otsu_threshold(gray)
    elif mode == PreprocessingMode.DOCUMENT:
        gray = adaptive_threshold(gray)
    elif mode == PreprocessingMode.LOW_QUALITY:
        gray = denoise(gray, strength=12)
        gray = adaptive_threshold(gray)

    return cv2_to_pil(gray)
