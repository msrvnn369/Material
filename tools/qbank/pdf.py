from __future__ import annotations

from pdfminer.high_level import extract_text


def extract_pdf_text_with_ocr(path: str, *, max_pages: int | None = 12) -> str:
    """
    Tries pdfminer first; falls back to OCR for scanned PDFs.
    """
    text = (extract_text(path) or "").strip()
    if len(text) >= 250:
        return text

    # OCR fallback (requires poppler + tesseract).
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception:
        return text

    pages = convert_from_path(path, dpi=220, first_page=1, last_page=max_pages or None)
    ocr_chunks: list[str] = []
    for i, img in enumerate(pages, start=1):
        try:
            t = pytesseract.image_to_string(img, lang="eng")
            t = t.strip()
            if t:
                ocr_chunks.append(f"\n\n--- Page {i} ---\n{t}")
        except Exception:
            continue
    ocr_text = "\n".join(ocr_chunks).strip()
    return ocr_text or text


def extract_pdf_text(path: str) -> str:
    # pdfminer handles many scanned PDFs poorly; OCR-on-PDF can be added later.
    return extract_text(path) or ""

