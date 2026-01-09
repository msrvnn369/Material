from __future__ import annotations

import os
from typing import Mapping

import requests

from .util import HttpResult, backoff_sleep


DEFAULT_HEADERS: Mapping[str, str] = {
    # Reddit blocks empty UA; set something consistent.
    "User-Agent": "qbank-bot/0.1 (edu; +https://github.com/msrvnn369/Material)",
    "Accept": "*/*",
}


def fetch_url(url: str, *, timeout_s: float = 25.0, max_attempts: int = 4) -> HttpResult:
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            r = requests.get(url, headers=dict(DEFAULT_HEADERS), timeout=timeout_s)
            ct = r.headers.get("content-type")
            return HttpResult(
                url=url,
                status=r.status_code,
                content_type=ct,
                content=r.content,
                elapsed_ms=int(r.elapsed.total_seconds() * 1000),
            )
        except Exception as e:  # noqa: BLE001
            last_exc = e
            if attempt < max_attempts - 1:
                backoff_sleep(attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_exc}")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

