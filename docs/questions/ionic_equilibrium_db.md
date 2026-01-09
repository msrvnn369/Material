# Ionic Equilibrium — Question Database (beta)

This repo now includes a **question ingestion + tagging pipeline** that builds:

- `data/questions.sqlite` (SQLite database)
- `data/questions.jsonl` (line-delimited JSON export for AI agents)

## Install ingestion dependencies

From the repo root:

```bash
python3 -m pip install -r requirements-ingest.txt
```

## Ingest URLs

Create a text file with one URL per line (example: `data/seed_urls.txt`) and run:

```bash
python3 -m tools.qbank.cli ingest --urls-file data/seed_urls.txt --ocr
python3 -m tools.qbank.cli dedupe
python3 -m tools.qbank.cli export
```

## What gets tagged (v1)

- **Chapter**: `chapter:Ionic Equilibrium`
- **Concepts**: `concept:ka`, `concept:kb`, `concept:buffers`, `concept:hydrolysis`, `concept:ksp`, `concept:common-ion`, …
- **Intent**: `intent:calculation-heavy`, `intent:conceptual`, …
- **Keywords**: `kw:<token>` (raw keyword tags)

## Notes / limitations (v1)

- YouTube comments are **not ingested** yet (needs API/key or a separate comment extraction method).
- Reddit threads are ingested via the public JSON endpoint and stored as raw JSON under `data/raw/`.
- OCR uses `tesseract-ocr` (installed on the machine) + `pytesseract`.

