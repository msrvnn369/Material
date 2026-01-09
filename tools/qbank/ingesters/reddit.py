from __future__ import annotations

import json
import os
import re
from urllib.parse import urlparse

import requests

from ..fetch import DEFAULT_HEADERS, ensure_dir, fetch_url
from ..util import sha256_bytes, utc_now_iso
from .base import IngestResult, Ingester, QuestionDraft


_COMMENTS_URL_RE = re.compile(r"(https?://(www\.)?reddit\.com/r/[^/]+/comments/[^/]+/[^/]+)")


def _canonical_comments_url(url: str) -> str:
    # Resolve share links / redirects (some /s/ links don't redirect server-side).
    r = requests.get(url, headers=dict(DEFAULT_HEADERS), timeout=20, allow_redirects=True)
    final = r.url

    for candidate in (final, url):
        m = _COMMENTS_URL_RE.search(candidate)
        if m:
            return m.group(1).rstrip("/")
        if "reddit.com" in candidate and "/comments/" in candidate:
            return candidate.split("?")[0].rstrip("/")

    # Fallback: fetch HTML and extract canonical comments URL from markup.
    try:
        hres = fetch_url(final)
        html = hres.content.decode("utf-8", errors="replace")
        m = _COMMENTS_URL_RE.search(html)
        if m:
            return m.group(1).rstrip("/")
        # Common pattern: <link rel="canonical" href=".../comments/...">
        m2 = re.search(r'rel="canonical"\s+href="([^"]+)"', html, re.I)
        if m2 and "/comments/" in m2.group(1):
            return m2.group(1).split("?")[0].rstrip("/")
    except Exception:
        pass

    raise RuntimeError(f"Could not canonicalize reddit url: {url} -> {final}")


def _flatten_comments(node) -> list[dict]:
    out: list[dict] = []
    if not isinstance(node, dict):
        return out
    kind = node.get("kind")
    data = node.get("data") or {}
    if kind == "t1":  # comment
        out.append(data)
        replies = data.get("replies")
        if isinstance(replies, dict):
            children = (replies.get("data") or {}).get("children") or []
            for c in children:
                out.extend(_flatten_comments(c))
    elif kind == "Listing":
        children = (data.get("children") or [])
        for c in children:
            out.extend(_flatten_comments(c))
    return out


def _discussion_summary(comments: list[dict], *, top_n: int = 20) -> str:
    # Best-effort: take top-scoring + include "correction/disagreement" flags.
    def score(c: dict) -> int:
        return int(c.get("score") or 0)

    interesting = []
    for c in comments:
        body = (c.get("body") or "").strip()
        if not body:
            continue
        flags = 0
        if re.search(r"\bwrong\b|\bincorrect\b|\bmistake\b|\bactually\b|\bbut\b|\bhowever\b", body, re.I):
            flags += 2
        if re.search(r"\banswer\b|\bsolution\b|\bapproach\b|\bmethod\b", body, re.I):
            flags += 1
        interesting.append((score(c) + 5 * flags, score(c), body))

    interesting.sort(reverse=True)
    picked = interesting[:top_n]
    lines = []
    for _, sc, body in picked:
        body = body.replace("\n", " ").strip()
        if len(body) > 320:
            body = body[:320].rstrip() + "…"
        lines.append(f"- ({sc:+d}) {body}")
    return "Top discussion points (auto-summary):\n" + "\n".join(lines) if lines else ""


class RedditIngester(Ingester):
    def can_handle(self, url: str) -> bool:
        return "reddit.com" in url or "redd.it" in url

    def ingest(self, url: str, *, raw_dir: str, attachments_dir: str) -> IngestResult:
        ensure_dir(raw_dir)
        ensure_dir(attachments_dir)

        comments_url = _canonical_comments_url(url)
        json_url = comments_url + ".json?raw_json=1"
        res = fetch_url(json_url)
        if res.status >= 400:
            raise RuntimeError(f"Fetch failed {res.status} for {json_url}")

        raw_name = f"reddit_{sha256_bytes(res.content)[:12]}.json"
        raw_path = os.path.join(raw_dir, raw_name)
        with open(raw_path, "wb") as f:
            f.write(res.content)

        payload = json.loads(res.content.decode("utf-8", errors="replace"))
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError("Unexpected reddit payload")

        post_listing = payload[0]
        comments_listing = payload[1]

        post_children = ((post_listing.get("data") or {}).get("children") or [])
        post = (post_children[0].get("data") if post_children else {}) or {}

        title = (post.get("title") or "").strip()
        selftext = (post.get("selftext") or "").strip()

        # Attach images if any.
        attachment_paths: list[str] = []
        preview = post.get("preview") or {}
        imgs = preview.get("images") or []
        for im in imgs:
            src = ((im.get("source") or {}).get("url") or "").replace("&amp;", "&")
            if not src:
                continue
            try:
                ires = fetch_url(src)
                if ires.status >= 400:
                    continue
                ext = ".jpg"
                name = f"reddit_img_{sha256_bytes(ires.content)[:12]}{ext}"
                path = os.path.join(attachments_dir, name)
                with open(path, "wb") as f:
                    f.write(ires.content)
                attachment_paths.append(path)
            except Exception:
                continue

        comments = _flatten_comments(comments_listing)
        summary = _discussion_summary(comments)

        metrics = {
            "comment_count": int(post.get("num_comments") or len(comments)),
            "score": int(post.get("score") or 0),
            "upvote_ratio": float(post.get("upvote_ratio") or 0.0),
        }

        stem = "\n\n".join(x for x in [title, selftext] if x).strip()
        if not stem:
            stem = f"Reddit discussion thread: {comments_url}"

        draft = QuestionDraft(
            stem=stem,
            options=None,
            discussion_url=comments_url,
            discussion_metrics=metrics,
            discussion_summary=summary,
            attachment_paths=attachment_paths,
            extra={"subreddit": post.get("subreddit"), "permalink": post.get("permalink"), "ingested_at": utc_now_iso()},
        )

        p = urlparse(comments_url)
        return IngestResult(
            source_name="Reddit",
            source_type="community",
            base_url=f"{p.scheme}://{p.netloc}",
            attribution=f"Reddit thread: {comments_url}",
            url=comments_url,
            raw_path=raw_path,
            drafts=[draft],
        )

