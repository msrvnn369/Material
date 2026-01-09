from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QuestionDraft:
    stem: str
    options: list[str] | None = None
    answer: dict | None = None
    solution: str | None = None
    exam: str | None = None
    year: int | None = None
    paper: str | None = None
    shift: str | None = None
    question_type: str | None = None

    # discussion
    discussion_url: str | None = None
    discussion_metrics: dict | None = None
    discussion_summary: str | None = None

    # attachments (downloaded)
    attachment_paths: list[str] = field(default_factory=list)
    ocr_text: str | None = None

    # parser metadata
    extra: dict = field(default_factory=dict)


@dataclass
class IngestResult:
    source_name: str
    source_type: str
    base_url: str | None
    attribution: str | None
    url: str
    raw_path: str | None
    drafts: list[QuestionDraft]


class Ingester:
    def can_handle(self, url: str) -> bool:
        raise NotImplementedError

    def ingest(self, url: str, *, raw_dir: str, attachments_dir: str) -> IngestResult:
        raise NotImplementedError

