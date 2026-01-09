from __future__ import annotations

import json
import os
import re
from urllib.parse import quote, urlparse

from ..fetch import ensure_dir, fetch_url
from ..util import sha256_bytes, utc_now_iso
from .base import IngestResult, Ingester, QuestionDraft


class YouTubeIngester(Ingester):
    def can_handle(self, url: str) -> bool:
        return "youtube.com" in url or "youtu.be" in url

    def ingest(self, url: str, *, raw_dir: str, attachments_dir: str) -> IngestResult:
        ensure_dir(raw_dir)
        ensure_dir(attachments_dir)

        oembed = f"https://www.youtube.com/oembed?url={quote(url, safe='')}&format=json"
        res = fetch_url(oembed)
        if res.status >= 400:
            raise RuntimeError(f"Fetch failed {res.status} for {oembed}")

        raw_name = f"youtube_{sha256_bytes(res.content)[:12]}.json"
        raw_path = os.path.join(raw_dir, raw_name)
        with open(raw_path, "wb") as f:
            f.write(res.content)

        meta = json.loads(res.content.decode("utf-8", errors="replace"))
        title = (meta.get("title") or "").strip()
        author = (meta.get("author_name") or "").strip()

        # We treat this as a "discussion-rich reference" but do not scrape comments (API/key).
        stem = "\n".join([x for x in [title, f"Author: {author}", f"Video: {url}"] if x]).strip()
        draft = QuestionDraft(
            stem=stem,
            discussion_url=url,
            discussion_metrics={"comments": None, "note": "YouTube comments not ingested (API/key needed)."},
            discussion_summary="",
            extra={"oembed": meta, "ingested_at": utc_now_iso()},
        )

        p = urlparse(url)
        return IngestResult(
            source_name="YouTube",
            source_type="video",
            base_url=f"{p.scheme}://{p.netloc}",
            attribution=f"YouTube: {url}",
            url=url,
            raw_path=raw_path,
            drafts=[draft],
        )

