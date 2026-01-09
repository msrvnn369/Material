from __future__ import annotations

import sqlite3

from .util import hamming64


def _bucket_keys(h: int) -> list[int]:
    """
    Simple LSH buckets: split into 4x16-bit chunks.
    """
    return [
        (h >> 0) & 0xFFFF,
        (h >> 16) & 0xFFFF,
        (h >> 32) & 0xFFFF,
        (h >> 48) & 0xFFFF,
    ]


def dedupe_questions(con: sqlite3.Connection, *, max_hamming: int = 3) -> int:
    """
    Sets questions.duplicate_group_id to the canonical id for near-duplicates.
    Returns number of questions updated.
    """
    rows = con.execute("SELECT id, simhash64 FROM questions").fetchall()
    items: list[tuple[str, int]] = [(r["id"], int(r["simhash64"])) for r in rows]

    buckets: dict[tuple[int, int], list[tuple[str, int]]] = {}
    for qid, h in items:
        for i, key in enumerate(_bucket_keys(h)):
            buckets.setdefault((i, key), []).append((qid, h))

    parent: dict[str, str] = {qid: qid for qid, _ in items}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        parent[max(ra, rb)] = min(ra, rb)

    # Compare within buckets only.
    seen_pairs: set[tuple[str, str]] = set()
    for _, lst in buckets.items():
        n = len(lst)
        if n > 600:  # avoid blowups; these buckets are too generic
            continue
        for i in range(n):
            id1, h1 = lst[i]
            for j in range(i + 1, n):
                id2, h2 = lst[j]
                a, b = (id1, id2) if id1 < id2 else (id2, id1)
                if (a, b) in seen_pairs:
                    continue
                seen_pairs.add((a, b))
                if hamming64(h1, h2) <= max_hamming:
                    union(id1, id2)

    updates = 0
    for qid, _ in items:
        root = find(qid)
        if root != qid:
            con.execute("UPDATE questions SET duplicate_group_id=? WHERE id=?", (root, qid))
            updates += 1
        else:
            con.execute("UPDATE questions SET duplicate_group_id=NULL WHERE id=?", (qid,))
    con.commit()
    return updates

