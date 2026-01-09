async function qbankLoadJsonl(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  const text = await res.text();
  const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
  const items = [];
  for (const line of lines) {
    try {
      items.push(JSON.parse(line));
    } catch (_) {
      // skip malformed lines
    }
  }
  return items;
}

function el(tag, attrs = {}, children = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else e.setAttribute(k, v);
  }
  for (const c of children) e.appendChild(c);
  return e;
}

function renderQuestion(q, idx) {
  const stem = (q.stem || "").trim();
  const tags = Array.isArray(q.tags) ? q.tags : [];
  const primaryChapter = q.primary_chapter || "";
  const qtype = q.question_type || "";

  const header = el("div", { class: "qbank-q-header" }, [
    el("div", { class: "qbank-q-title", text: `${idx + 1}. ${primaryChapter}` }),
    el("div", { class: "qbank-q-meta", text: `${qtype}${qtype && q.id ? " · " : ""}${q.id || ""}` }),
  ]);

  const stemEl = el("div", { class: "qbank-q-stem" });
  stemEl.textContent = stem;

  const tagsWrap = el("div", { class: "qbank-q-tags" });
  for (const t of tags.slice(0, 40)) {
    tagsWrap.appendChild(el("span", { class: "qbank-tag", text: t }));
  }

  const card = el("div", { class: "qbank-card md-typeset" }, [header, stemEl, tagsWrap]);
  return card;
}

async function main() {
  const root = document.querySelector("[data-qbank-root]");
  if (!root) return;

  const src = root.getAttribute("data-qbank-src");
  const dataUrl = new URL(src, window.location.href).toString();

  const status = el("div", { class: "qbank-status", text: "Loading questions…" });
  root.appendChild(status);

  try {
    const items = await qbankLoadJsonl(dataUrl);
    status.textContent = `Loaded ${items.length} questions.`;

    const list = el("div", { class: "qbank-list" });
    items.forEach((q, i) => list.appendChild(renderQuestion(q, i)));
    root.appendChild(list);

    // Let MathJax re-typeset if needed.
    if (window.MathJax && window.MathJax.typesetPromise) {
      try {
        await window.MathJax.typesetPromise();
      } catch (_) {}
    }
  } catch (e) {
    status.textContent = `Failed to load questions: ${e}`;
  }
}

document.addEventListener("DOMContentLoaded", main);

