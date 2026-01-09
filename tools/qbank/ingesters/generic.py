from __future__ import annotations

import os
import re
from urllib.parse import urljoin, urlparse

import html2text
from bs4 import BeautifulSoup
from readability import Document

from ..fetch import ensure_dir, fetch_url
from ..pdf import extract_pdf_text_with_ocr
from ..util import sha256_bytes, utc_now_iso
from .base import IngestResult, Ingester, QuestionDraft


_Q_SPLIT_RE = re.compile(
    r"(?m)^\s*(?:q(?:uestion)?\s*)?(\d{1,4})\s*[\)\.\:\-]\s+"
)

_PDF_Q_SPLIT_RE = re.compile(
    r"(?m)^\s*(?:q(?:uestion)?\.?\s*)?(\d{1,4})\s*[\)\.\:\-]\s+"
)

# Require explicit option markers like "(A)" / "A)" / "A." / "1)" etc.
_OPT_RE = re.compile(r"(?m)^\s*(?:\(([A-H])\)|([A-H])\)|([A-H])\.|([1-8])\))\s+")


def _slug(url: str) -> str:
    p = urlparse(url)
    base = (p.netloc + p.path).strip("/").replace("/", "_")
    base = re.sub(r"[^a-zA-Z0-9_\-\.]+", "_", base)
    return base[:180] or "page"


class GenericHtmlIngester(Ingester):
    def can_handle(self, url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    def ingest(self, url: str, *, raw_dir: str, attachments_dir: str) -> IngestResult:
        ensure_dir(raw_dir)
        ensure_dir(attachments_dir)

        res = fetch_url(url)
        if res.status >= 400:
            raise RuntimeError(f"Fetch failed {res.status} for {url}")

        raw_name = f"{_slug(url)}_{sha256_bytes(res.content)[:12]}.html"
        raw_path = os.path.join(raw_dir, raw_name)
        with open(raw_path, "wb") as f:
            f.write(res.content)

        html = res.content.decode("utf-8", errors="replace")

        # If the page links to a PDF, prefer extracting questions from the PDF.
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        full_soup = BeautifulSoup(html, "lxml")
        pdf_urls: list[str] = []
        for a in full_soup.find_all("a"):
            href = a.get("href") or ""
            if ".pdf" in href.lower():
                pdf_urls.append(urljoin(base_url, href))
        pdf_text = ""
        pdf_attachment_paths: list[str] = []
        if pdf_urls:
            # Best-effort: take the first PDF link.
            pdf_url = pdf_urls[0]
            try:
                pres = fetch_url(pdf_url)
                ct = (pres.content_type or "").lower()
                if pres.status < 400 and ("pdf" in ct or pdf_url.lower().endswith(".pdf")):
                    pdf_name = f"{_slug(pdf_url)}_{sha256_bytes(pres.content)[:12]}.pdf"
                    pdf_path = os.path.join(attachments_dir, pdf_name)
                    with open(pdf_path, "wb") as f:
                        f.write(pres.content)
                    pdf_attachment_paths.append(pdf_path)
                    pdf_text = extract_pdf_text_with_ocr(pdf_path, max_pages=20).strip()
            except Exception:
                pdf_text = ""

        # Extract main article-ish content.
        doc = Document(html)
        summary_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(summary_html, "lxml")

        # Download images in the main content (best-effort).
        attachment_paths: list[str] = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src or src.startswith("data:"):
                continue
            try:
                ires = fetch_url(src)
                if ires.status >= 400:
                    continue
                ext = ".img"
                ctype = (ires.content_type or "").lower()
                if "png" in ctype:
                    ext = ".png"
                elif "jpeg" in ctype or "jpg" in ctype:
                    ext = ".jpg"
                elif "webp" in ctype:
                    ext = ".webp"
                name = f"{_slug(src)}_{sha256_bytes(ires.content)[:12]}{ext}"
                path = os.path.join(attachments_dir, name)
                with open(path, "wb") as f:
                    f.write(ires.content)
                attachment_paths.append(path)
            except Exception:
                continue

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        text = h.handle(str(soup))
        text = text.strip()

        drafts: list[QuestionDraft] = []

        # If PDF produced question-like splits, use that.
        if pdf_text:
            splits = list(_PDF_Q_SPLIT_RE.finditer(pdf_text))
            if len(splits) >= 2:
                chunks: list[str] = []
                for i, m in enumerate(splits):
                    start = m.start()
                    end = splits[i + 1].start() if i + 1 < len(splits) else len(pdf_text)
                    chunks.append(pdf_text[start:end].strip())
                for chunk in chunks:
                    d = self._chunk_to_draft(chunk, pdf_attachment_paths)
                    d.extra["pdf_url"] = pdf_urls[0]
                    drafts.append(d)
            else:
                d = self._chunk_to_draft(pdf_text, pdf_attachment_paths)
                d.extra["pdf_url"] = pdf_urls[0]
                drafts.append(d)
        else:
            # If the page looks like a question list, try to split.
            splits = list(_Q_SPLIT_RE.finditer(text))
            if len(splits) >= 2:
                chunks: list[str] = []
                for i, m in enumerate(splits):
                    start = m.start()
                    end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
                    chunks.append(text[start:end].strip())
                for chunk in chunks:
                    drafts.append(self._chunk_to_draft(chunk, attachment_paths))
            else:
                # Single-question page.
                drafts.append(self._chunk_to_draft(text, attachment_paths))

        p = urlparse(url)
        return IngestResult(
            source_name=p.netloc,
            source_type="unknown",
            base_url=base_url,
            attribution=f"Source: {url}",
            url=url,
            raw_path=raw_path,
            drafts=drafts,
        )

    def _chunk_to_draft(self, chunk: str, attachment_paths: list[str]) -> QuestionDraft:
        # Split out options if present.
        lines = [ln.rstrip() for ln in chunk.splitlines() if ln.strip()]
        stem_lines: list[str] = []
        options: list[str] = []
        in_opts = False
        for ln in lines:
            if _OPT_RE.match(ln):
                in_opts = True
            if in_opts:
                options.append(ln)
            else:
                stem_lines.append(ln)
        stem = "\n".join(stem_lines).strip() or chunk.strip()
        opts = options if len(options) >= 2 else None
        return QuestionDraft(stem=stem, options=opts, attachment_paths=list(attachment_paths), extra={"ingested_at": utc_now_iso()})

