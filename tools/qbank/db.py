from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from .util import utc_now_iso


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON;")
    return con


def init_db(con: sqlite3.Connection, schema_path: str) -> None:
    with open(schema_path, "r", encoding="utf-8") as f:
        con.executescript(f.read())
    con.commit()


def get_or_create_source(
    con: sqlite3.Connection,
    *,
    name: str,
    source_type: str,
    base_url: str | None = None,
    notes: str | None = None,
) -> int:
    row = con.execute("SELECT id FROM sources WHERE name = ?", (name,)).fetchone()
    if row:
        return int(row["id"])
    con.execute(
        "INSERT INTO sources(name, source_type, base_url, notes) VALUES(?,?,?,?)",
        (name, source_type, base_url, notes),
    )
    con.commit()
    return int(con.execute("SELECT last_insert_rowid()").fetchone()[0])


def upsert_tag(con: sqlite3.Connection, *, tag: str, tag_type: str, description: str | None = None) -> None:
    con.execute(
        """
        INSERT INTO tags(tag, tag_type, description)
        VALUES(?,?,?)
        ON CONFLICT(tag) DO UPDATE SET
          tag_type=excluded.tag_type,
          description=COALESCE(excluded.description, tags.description)
        """,
        (tag, tag_type, description),
    )


def upsert_question(
    con: sqlite3.Connection,
    *,
    qid: str,
    stem: str,
    normalized_text: str,
    simhash64: str,
    subject: str = "Chemistry",
    primary_chapter: str = "Ionic Equilibrium",
    language: str = "en",
    exam: str | None = None,
    year: int | None = None,
    paper: str | None = None,
    shift: str | None = None,
    question_type: str | None = None,
    options_json: str | None = None,
    answer_json: str | None = None,
    solution_text: str | None = None,
    time_to_solve_sec: int | None = None,
    difficulty_json: str | None = None,
    duplicate_group_id: str | None = None,
) -> None:
    now = utc_now_iso()
    con.execute(
        """
        INSERT INTO questions(
          id, subject, primary_chapter, language,
          exam, year, paper, shift,
          question_type, stem, options_json, answer_json, solution_text,
          normalized_text, simhash64, duplicate_group_id,
          time_to_solve_sec, difficulty_json,
          created_at, updated_at
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          subject=excluded.subject,
          primary_chapter=excluded.primary_chapter,
          language=excluded.language,
          exam=COALESCE(excluded.exam, questions.exam),
          year=COALESCE(excluded.year, questions.year),
          paper=COALESCE(excluded.paper, questions.paper),
          shift=COALESCE(excluded.shift, questions.shift),
          question_type=COALESCE(excluded.question_type, questions.question_type),
          stem=excluded.stem,
          options_json=COALESCE(excluded.options_json, questions.options_json),
          answer_json=COALESCE(excluded.answer_json, questions.answer_json),
          solution_text=COALESCE(excluded.solution_text, questions.solution_text),
          normalized_text=excluded.normalized_text,
          simhash64=excluded.simhash64,
          duplicate_group_id=COALESCE(excluded.duplicate_group_id, questions.duplicate_group_id),
          time_to_solve_sec=COALESCE(excluded.time_to_solve_sec, questions.time_to_solve_sec),
          difficulty_json=COALESCE(excluded.difficulty_json, questions.difficulty_json),
          updated_at=?
        """,
        (
            qid,
            subject,
            primary_chapter,
            language,
            exam,
            year,
            paper,
            shift,
            question_type,
            stem,
            options_json,
            answer_json,
            solution_text,
            normalized_text,
            simhash64,
            duplicate_group_id,
            time_to_solve_sec,
            difficulty_json,
            now,
            now,
            now,
        ),
    )


def attach_source(
    con: sqlite3.Connection,
    *,
    qid: str,
    source_id: int,
    source_url: str,
    raw_path: str | None,
    attribution_text: str | None,
    extra_json: str | None,
) -> None:
    con.execute(
        """
        INSERT INTO question_sources(question_id, source_id, source_url, retrieved_at, raw_path, attribution_text, extra_json)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(question_id, source_url) DO UPDATE SET
          retrieved_at=excluded.retrieved_at,
          raw_path=COALESCE(excluded.raw_path, question_sources.raw_path),
          attribution_text=COALESCE(excluded.attribution_text, question_sources.attribution_text),
          extra_json=COALESCE(excluded.extra_json, question_sources.extra_json)
        """,
        (qid, source_id, source_url, utc_now_iso(), raw_path, attribution_text, extra_json),
    )


def set_question_tags(con: sqlite3.Connection, *, qid: str, tags: list[tuple[str, str, float | None]]) -> None:
    """
    tags: list of (tag, tag_type, weight)
    """
    for tag, tag_type, weight in tags:
        upsert_tag(con, tag=tag, tag_type=tag_type)
        con.execute(
            """
            INSERT INTO question_tags(question_id, tag, weight)
            VALUES(?,?,?)
            ON CONFLICT(question_id, tag) DO UPDATE SET
              weight=COALESCE(excluded.weight, question_tags.weight)
            """,
            (qid, tag, weight),
        )


def add_discussion(
    con: sqlite3.Connection,
    *,
    qid: str,
    source_id: int | None,
    discussion_url: str | None,
    metrics_json: str | None,
    summary_text: str | None,
    raw_path: str | None,
) -> None:
    con.execute(
        """
        INSERT INTO discussions(question_id, source_id, discussion_url, metrics_json, summary_text, raw_path, created_at)
        VALUES(?,?,?,?,?,?,?)
        """,
        (qid, source_id, discussion_url, metrics_json, summary_text, raw_path, utc_now_iso()),
    )


def add_attachment(
    con: sqlite3.Connection,
    *,
    qid: str,
    kind: str,
    path: str,
    sha256: str | None,
    ocr_text: str | None,
    ocr_confidence: float | None,
) -> None:
    con.execute(
        """
        INSERT INTO attachments(question_id, kind, path, sha256, ocr_text, ocr_confidence, created_at)
        VALUES(?,?,?,?,?,?,?)
        """,
        (qid, kind, path, sha256, ocr_text, ocr_confidence, utc_now_iso()),
    )

