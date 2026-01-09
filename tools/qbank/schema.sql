PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Core question record.
CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY,                 -- stable id (sha256 derived)
  subject TEXT NOT NULL DEFAULT 'Chemistry',
  primary_chapter TEXT NOT NULL DEFAULT 'Ionic Equilibrium',
  language TEXT NOT NULL DEFAULT 'en',

  exam TEXT,                           -- 'JEE Main' | 'JEE Advanced' | etc
  year INTEGER,
  paper TEXT,                          -- e.g. 'Paper 1'
  shift TEXT,                          -- e.g. 'Shift 2'

  question_type TEXT,                  -- mcq_single|mcq_multi|integer|matrix|match|assertion_reason|paragraph|unknown
  stem TEXT NOT NULL,
  options_json TEXT,                   -- JSON array or null
  answer_json TEXT,                    -- JSON object (key(s), explanation, etc.)
  solution_text TEXT,

  normalized_text TEXT NOT NULL,        -- for dedupe/search
  simhash64 TEXT NOT NULL,              -- unsigned 64-bit represented as decimal string
  duplicate_group_id TEXT,              -- id of canonical question

  time_to_solve_sec INTEGER,

  -- difficulty signals and computed values as JSON for flexibility
  difficulty_json TEXT,                 -- {"human":{"score_1_10":...}, "ai":{"no_tools":...,"with_tools":...}, "signals":{...}}

  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_questions_exam_year ON questions(exam, year);
CREATE INDEX IF NOT EXISTS idx_questions_simhash ON questions(simhash64);
CREATE INDEX IF NOT EXISTS idx_questions_dup_group ON questions(duplicate_group_id);

-- Where a question came from. A question can appear in multiple sources.
CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  source_type TEXT NOT NULL,           -- official|coaching|community|video|unknown
  base_url TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS question_sources (
  question_id TEXT NOT NULL,
  source_id INTEGER NOT NULL,
  source_url TEXT NOT NULL,
  retrieved_at TEXT NOT NULL,

  raw_path TEXT,                       -- saved HTML/JSON/PDF (relative)
  attribution_text TEXT,               -- what to show on site
  extra_json TEXT,                     -- parser-specific metadata

  PRIMARY KEY (question_id, source_url),
  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_question_sources_source ON question_sources(source_id);

-- Tags/Concepts (fine grained). We store both to let you keep a curated concept set
-- while still attaching free-form tags.
CREATE TABLE IF NOT EXISTS tags (
  tag TEXT PRIMARY KEY,                 -- e.g. 'buffer', 'ksp', 'common-ion'
  tag_type TEXT NOT NULL,               -- keyword|concept|chapter|type|source|intent|meta
  description TEXT
);

CREATE TABLE IF NOT EXISTS question_tags (
  question_id TEXT NOT NULL,
  tag TEXT NOT NULL,
  weight REAL,                          -- for ranked tags
  PRIMARY KEY (question_id, tag),
  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
  FOREIGN KEY (tag) REFERENCES tags(tag) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_question_tags_tag ON question_tags(tag);

-- Discussion capture + summary (may come from reddit thread, comments on page, etc).
CREATE TABLE IF NOT EXISTS discussions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id TEXT NOT NULL,
  source_id INTEGER,
  discussion_url TEXT,

  metrics_json TEXT,                    -- {"comment_count":..., "upvotes":..., "disagreement":...}
  summary_text TEXT,                    -- "without missing any niche point" (best-effort)
  raw_path TEXT,                        -- saved raw discussion JSON/HTML

  created_at TEXT NOT NULL,

  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL
);

-- Attachments (images/pdfs) + OCR.
CREATE TABLE IF NOT EXISTS attachments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id TEXT NOT NULL,
  kind TEXT NOT NULL,                   -- image|pdf|other
  path TEXT NOT NULL,                   -- relative to repo root
  sha256 TEXT,
  ocr_text TEXT,
  ocr_confidence REAL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

