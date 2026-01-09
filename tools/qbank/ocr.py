from __future__ import annotations

import shutil
from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float | None


def ocr_available() -> bool:
    return shutil.which("tesseract") is not None


def ocr_image(path: str) -> OcrResult:
    """
    OCR via tesseract (if installed). Confidence is best-effort:
    pytesseract provides per-word conf, but varies by output type, so we keep it optional.
    """
    try:
        import pytesseract
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"pytesseract not available: {e}") from e

    if not ocr_available():
        raise RuntimeError("tesseract binary not installed")

    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang="eng")
    text = text.strip()
    return OcrResult(text=text, confidence=None)

