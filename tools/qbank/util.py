from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """
    Normalization tuned for dedupe/search:
    - collapse whitespace
    - strip
    - lowercase
    - normalize common option markers
    """
    t = text or ""
    t = t.replace("\u00a0", " ")
    t = _WS_RE.sub(" ", t).strip().lower()
    t = t.replace("−", "-")
    return t


def stable_question_id(*parts: str) -> str:
    """
    Stable id based on normalized content; keep it deterministic across sources.
    """
    joined = "\n".join(normalize_text(p) for p in parts if p)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:24]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def tokenize_for_simhash(text: str) -> list[str]:
    # Keep chemistry-ish tokens: letters, digits, +, -, parentheses, decimal points
    t = normalize_text(text)
    tokens = re.findall(r"[a-z0-9][a-z0-9\+\-\(\)\.\%]*", t)
    return tokens


def simhash64(tokens: Iterable[str]) -> int:
    """
    Tiny simhash implementation (64-bit) for dedupe.
    """
    v = [0] * 64
    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        for i in range(64):
            bit = (h >> i) & 1
            v[i] += 1 if bit else -1
    out = 0
    for i, score in enumerate(v):
        if score > 0:
            out |= 1 << i
    return out


def hamming64(a: int, b: int) -> int:
    return (a ^ b).bit_count()


@dataclass(frozen=True)
class HttpResult:
    url: str
    status: int
    content_type: str | None
    content: bytes
    elapsed_ms: int


def backoff_sleep(attempt: int, base: float = 0.7, cap: float = 12.0) -> None:
    delay = min(cap, base * (2**attempt))
    time.sleep(delay)

