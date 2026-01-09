from __future__ import annotations

import re
from collections import Counter

from .util import normalize_text


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "for",
    "on",
    "at",
    "with",
    "is",
    "are",
    "was",
    "were",
    "be",
    "as",
    "by",
    "from",
    "that",
    "this",
    "these",
    "those",
    "which",
    "if",
    "then",
    "find",
    "calculate",
    "determine",
    "given",
    "following",
    "among",
    "correct",
    "statement",
    "statements",
    "option",
    "options",
}


# Fine-grained ionic equilibrium concept map (v1, rule-based).
CONCEPT_RULES: list[tuple[str, str, re.Pattern[str]]] = [
    ("concept", "chemical-equilibrium", re.compile(r"\bK\s*c\b|\bkc\b|\bK\s*p\b|\bkp\b|\ble\s+chatelier\b|\breaction quotient\b|\bqc\b|\bqp\b", re.I)),
    ("concept", "acid-base", re.compile(r"\bacid\b|\bbase\b|\bbrønsted\b|\blewis\b", re.I)),
    ("concept", "ph", re.compile(r"\bp\s*h\b|\bph\b|\b\-\s*log\b|\blog\s*\[h\+\]", re.I)),
    ("concept", "pka-pkb", re.compile(r"\bpka\b|\bpkb\b", re.I)),
    ("concept", "ka", re.compile(r"\bK\s*a\b|\bka\b", re.I)),
    ("concept", "kb", re.compile(r"\bK\s*b\b|\bkb\b", re.I)),
    ("concept", "kw", re.compile(r"\bK\s*w\b|\bkw\b|\bionic product of water\b", re.I)),
    ("concept", "buffers", re.compile(r"\bbuffer\b|\bhenderson\b|\bhasselbalch\b|\bbuffer capacity\b", re.I)),
    ("concept", "hydrolysis", re.compile(r"\bhydrolysis\b|\bdegree of hydrolysis\b|\bh\b=\b", re.I)),
    ("concept", "salt-hydrolysis", re.compile(r"\bsalt\b.*\bhydrolysis\b|\bsalt of\b", re.I)),
    ("concept", "ksp", re.compile(r"\bK\s*sp\b|\bksp\b|\bsolubility product\b", re.I)),
    ("concept", "common-ion", re.compile(r"\bcommon ion\b|\bcommon-ion\b", re.I)),
    ("concept", "solubility", re.compile(r"\bsolubility\b|\bmolar solubility\b|\bS\b\s*=", re.I)),
    ("concept", "selective-precipitation", re.compile(r"\bselective precipitation\b|\bfractional precipitation\b", re.I)),
    ("concept", "complexation", re.compile(r"\bKf\b|\bformation constant\b|\bcomplex\b", re.I)),
    ("concept", "salt-analysis", re.compile(r"\bsalt analysis\b|\bgroup analysis\b|\bqualitative analysis\b", re.I)),
]


INTENT_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("intent:calculation-heavy", re.compile(r"\bcalculate\b|\bfind\b|\bdetermine\b|\bevaluate\b", re.I)),
    ("intent:conceptual", re.compile(r"\bexplain\b|\breason\b|\bwhy\b|\bwhich of the following is true\b", re.I)),
    ("intent:approximation", re.compile(r"\bapprox\b|\bassume\b|\bneglect\b|\b(\<\<)\b", re.I)),
    ("intent:multi-step", re.compile(r"\bthen\b|\bsubsequently\b|\bafter that\b|\bstep\b", re.I)),
]


def infer_question_type(stem: str, options: list[str] | None) -> str:
    s = stem or ""
    if options and len(options) >= 4:
        return "mcq_single"
    if re.search(r"\bassertion\b.*\breason\b", s, re.I):
        return "assertion_reason"
    if re.search(r"\bmatch\b|\bcolumn\b", s, re.I):
        return "match"
    if re.search(r"\binteger\b|\bnumerical\b", s, re.I):
        return "integer"
    return "unknown"


def keyword_tags(text: str, *, top_k: int = 20) -> list[tuple[str, float]]:
    t = normalize_text(text)
    toks = re.findall(r"[a-z][a-z0-9\-]{2,}", t)
    toks = [x for x in toks if x not in STOPWORDS]
    c = Counter(toks)
    common = c.most_common(top_k)
    if not common:
        return []
    maxc = common[0][1]
    out: list[tuple[str, float]] = []
    for w, cnt in common:
        out.append((f"kw:{w}", cnt / maxc))
    return out


def concept_tags(text: str) -> list[str]:
    tags: list[str] = []
    for tag_type, name, pat in CONCEPT_RULES:
        if pat.search(text):
            tags.append(f"{tag_type}:{name}")
    return tags


def intent_tags(text: str) -> list[str]:
    tags: list[str] = []
    for name, pat in INTENT_RULES:
        if pat.search(text):
            tags.append(name)
    return tags


def tag_question(stem: str, options: list[str] | None, *, primary_chapter: str = "Ionic Equilibrium") -> list[tuple[str, str, float | None]]:
    """
    Returns (tag, tag_type, weight).
    """
    full = stem + "\n" + ("\n".join(options) if options else "")

    tags: list[tuple[str, str, float | None]] = []
    tags.append((f"chapter:{primary_chapter}", "chapter", None))
    tags.append(("subject:chemistry", "meta", None))

    for ctag in concept_tags(full):
        tags.append((ctag, "concept", None))

    for itag in intent_tags(full):
        tags.append((itag, "intent", None))

    for kw, w in keyword_tags(full):
        tags.append((kw, "keyword", float(w)))

    return tags


def infer_primary_chapter(text: str) -> str:
    t = text or ""
    # Ionic equilibrium signals
    if re.search(r"\bka\b|\bkb\b|\bkw\b|\bksp\b|\bph\b|\bbuffer\b|\bhydrolysis\b|\bcommon ion\b", t, re.I):
        return "Ionic Equilibrium"
    # Chemical equilibrium signals
    if re.search(r"\bkc\b|\bkp\b|\ble\s+chatelier\b|\bqc\b|\bqp\b|\bequilibrium constant\b", t, re.I):
        return "Chemical Equilibrium"
    return "Ionic Equilibrium"

