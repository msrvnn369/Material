from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from . import dedupe as dedupe_mod
from .db import (
    add_attachment,
    add_discussion,
    attach_source,
    connect,
    get_or_create_source,
    init_db,
    set_question_tags,
    upsert_question,
)
from .ingesters.generic import GenericHtmlIngester
from .ingesters.reddit import RedditIngester
from .ingesters.youtube import YouTubeIngester
from .ocr import ocr_image
from .tagging import infer_primary_chapter, infer_question_type, tag_question
from .util import json_dumps, normalize_text, sha256_bytes, simhash64, stable_question_id, tokenize_for_simhash, utc_now_iso


INGESTERS = [
    RedditIngester(),
    YouTubeIngester(),
    GenericHtmlIngester(),
]


def _pick_ingester(url: str):
    for ing in INGESTERS:
        if ing.can_handle(url):
            return ing
    return None


def cmd_init(args: argparse.Namespace) -> None:
    con = connect(args.db)
    init_db(con, args.schema)
    con.close()
    print(f"Initialized DB: {args.db}")


def _repo_root() -> Path:
    # tools/qbank/cli.py -> repo root
    return Path(__file__).resolve().parents[2]


def cmd_ingest(args: argparse.Namespace) -> None:
    root = _repo_root()
    con = connect(args.db)
    init_db(con, args.schema)

    raw_dir = str((root / args.raw_dir).resolve())
    att_dir = str((root / args.attachments_dir).resolve())
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(att_dir, exist_ok=True)

    urls: list[str] = []
    if args.urls_file:
        urls.extend([ln.strip() for ln in Path(args.urls_file).read_text(encoding="utf-8").splitlines() if ln.strip()])
    urls.extend(args.urls)
    if not urls:
        raise SystemExit("No URLs provided.")

    inserted = 0
    for url in urls:
        ing = _pick_ingester(url)
        if not ing:
            print(f"SKIP (no ingester): {url}")
            continue

        try:
            result = ing.ingest(url, raw_dir=raw_dir, attachments_dir=att_dir)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR ingesting {url}: {e}")
            continue
        source_id = get_or_create_source(
            con,
            name=result.source_name,
            source_type=result.source_type,
            base_url=result.base_url,
            notes=None,
        )

        for draft in result.drafts:
            stem = draft.stem.strip()
            opts = [o.strip() for o in (draft.options or []) if o.strip()] or None
            qtype = draft.question_type or infer_question_type(stem, opts)

            # Drop OCR split artifacts like "31." or empty fragments.
            if not stem:
                continue
            norm_stem_only = normalize_text(stem)
            if (not opts) and (len(norm_stem_only) < 25 or re.fullmatch(r"\d{1,4}\.?", stem.strip())):
                continue

            norm = normalize_text(stem + "\n" + ("\n".join(opts) if opts else ""))
            qid = stable_question_id(stem, "\n".join(opts or []))
            sh = simhash64(tokenize_for_simhash(norm))

            primary_chapter = infer_primary_chapter(stem + "\n" + ("\n".join(opts) if opts else ""))

            upsert_question(
                con,
                qid=qid,
                stem=stem,
                normalized_text=norm,
                simhash64=str(sh),
                primary_chapter=primary_chapter,
                question_type=qtype,
                options_json=json_dumps(opts) if opts else None,
                answer_json=json_dumps(draft.answer) if draft.answer else None,
                solution_text=draft.solution,
                exam=draft.exam,
                year=draft.year,
                paper=draft.paper,
                shift=draft.shift,
                difficulty_json=json_dumps(
                    {
                        "signals": {
                            "has_options": bool(opts),
                            "text_len": len(norm),
                            "source": result.source_name,
                            "ingested_at": utc_now_iso(),
                        }
                    }
                ),
            )

            attach_source(
                con,
                qid=qid,
                source_id=source_id,
                source_url=result.url,
                raw_path=os.path.relpath(result.raw_path, str(root)) if result.raw_path else None,
                attribution_text=result.attribution,
                extra_json=json_dumps(draft.extra) if draft.extra else None,
            )

            # Tags (concept + keyword + intent + chapter)
            tags = tag_question(stem, opts, primary_chapter=primary_chapter)
            set_question_tags(con, qid=qid, tags=tags)

            # Discussion capture
            if draft.discussion_url or draft.discussion_metrics or draft.discussion_summary:
                add_discussion(
                    con,
                    qid=qid,
                    source_id=source_id,
                    discussion_url=draft.discussion_url,
                    metrics_json=json_dumps(draft.discussion_metrics) if draft.discussion_metrics else None,
                    summary_text=draft.discussion_summary,
                    raw_path=None,
                )

            # Attachments + OCR (best-effort)
            for ap in draft.attachment_paths:
                try:
                    abs_path = Path(ap).resolve()
                    b = abs_path.read_bytes()
                    shx = sha256_bytes(b)
                    rel = os.path.relpath(str(abs_path), str(root))
                    ocr_text = None
                    ocr_conf = None
                    if args.ocr:
                        try:
                            o = ocr_image(str(abs_path))
                            ocr_text = o.text
                            ocr_conf = o.confidence
                        except Exception:
                            ocr_text = None
                            ocr_conf = None
                    add_attachment(
                        con,
                        qid=qid,
                        kind="image",
                        path=rel,
                        sha256=shx,
                        ocr_text=ocr_text,
                        ocr_confidence=ocr_conf,
                    )
                except Exception:
                    continue

            inserted += 1

    con.commit()
    con.close()
    print(f"Ingested drafts: {inserted}")


def cmd_dedupe(args: argparse.Namespace) -> None:
    con = connect(args.db)
    n = dedupe_mod.dedupe_questions(con, max_hamming=args.max_hamming)
    con.close()
    print(f"Updated duplicate_group_id for {n} questions")


def cmd_export(args: argparse.Namespace) -> None:
    root = _repo_root()
    con = connect(args.db)
    rows = con.execute(
        """
        SELECT
          q.*,
          GROUP_CONCAT(qt.tag, '||') AS tags_concat
        FROM questions q
        LEFT JOIN question_tags qt ON qt.question_id = q.id
        GROUP BY q.id
        """
    ).fetchall()
    out_path = (root / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            tags = (r["tags_concat"] or "").split("||") if r["tags_concat"] else []
            obj = dict(r)
            obj["tags"] = [t for t in tags if t]
            obj.pop("tags_concat", None)
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    con.close()
    print(f"Exported {len(rows)} questions -> {os.path.relpath(str(out_path), str(root))}")


def main() -> None:
    p = argparse.ArgumentParser(prog="qbank")
    p.add_argument("--db", default="data/questions.sqlite", help="SQLite DB path")
    p.add_argument("--schema", default="tools/qbank/schema.sql", help="Schema SQL path")

    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", help="Initialize DB")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("ingest", help="Ingest URLs into DB")
    sp.add_argument("urls", nargs="*", help="URLs to ingest")
    sp.add_argument("--urls-file", help="Text file with one URL per line")
    sp.add_argument("--raw-dir", default="data/raw", help="Where to store raw HTML/JSON")
    sp.add_argument("--attachments-dir", default="data/attachments", help="Where to store downloaded images")
    sp.add_argument("--ocr", action="store_true", help="Run OCR on downloaded images")
    sp.set_defaults(func=cmd_ingest)

    sp = sub.add_parser("dedupe", help="Run near-duplicate grouping")
    sp.add_argument("--max-hamming", type=int, default=3, help="Simhash hamming threshold")
    sp.set_defaults(func=cmd_dedupe)

    sp = sub.add_parser("export", help="Export questions to JSONL")
    sp.add_argument("--out", default="data/questions.jsonl", help="Output JSONL path")
    sp.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

