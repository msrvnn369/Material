/**
 * Simple helper for embedding SDF/MOL blocks in MkDocs pages.
 *
 * Usage (in Markdown):
 * <div class="mol3d" data-model="/assets/molecules/ethanol.sdf"></div>
 */
function pagesBasePrefixFromCanonical() {
  const canonical = document.querySelector('link[rel="canonical"]')?.href;
  if (!canonical) return "";
  try {
    const u = new URL(canonical);
    const parts = u.pathname.split("/").filter(Boolean);
    // For GitHub Pages project sites, the first path segment is the repo name.
    return parts.length >= 1 ? `/${parts[0]}` : "";
  } catch {
    return "";
  }
}

async function fetchTextWithFallback(urlCandidates) {
  let lastErr = null;
  for (const url of urlCandidates) {
    try {
      const res = await fetch(url);
      if (res.ok) return { url, text: await res.text() };
      lastErr = new Error(`HTTP ${res.status} for ${url}`);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error("Failed to fetch model");
}

function dist(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  const dz = a.z - b.z;
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

function angleDeg(a, b, c) {
  // angle ABC in degrees
  const v1 = { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
  const v2 = { x: c.x - b.x, y: c.y - b.y, z: c.z - b.z };
  const dot = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
  const n1 = Math.sqrt(v1.x * v1.x + v1.y * v1.y + v1.z * v1.z);
  const n2 = Math.sqrt(v2.x * v2.x + v2.y * v2.y + v2.z * v2.z);
  const cos = Math.max(-1, Math.min(1, dot / (n1 * n2)));
  return (Math.acos(cos) * 180) / Math.PI;
}

function midpoint(a, b) {
  return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, z: (a.z + b.z) / 2 };
}

function parseMeasures(spec) {
  // Format:
  // "dist:1-2,dist:1-7,angle:1-7-2"
  // Indices are 1-based (SDF atom numbering).
  if (!spec) return [];
  return spec
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .map((item) => {
      const [kindRaw, restRaw] = item.split(":").map((x) => (x || "").trim());
      const kind = kindRaw.toLowerCase();
      const rest = (restRaw || "").trim();
      if (!kind || !rest) return null;
      if (kind === "dist" || kind === "distance") {
        const [i, j] = rest.split("-").map((n) => parseInt(n, 10));
        if (!Number.isFinite(i) || !Number.isFinite(j)) return null;
        return { kind: "dist", i, j };
      }
      if (kind === "angle") {
        const [i, j, k] = rest.split("-").map((n) => parseInt(n, 10));
        if (!Number.isFinite(i) || !Number.isFinite(j) || !Number.isFinite(k)) return null;
        return { kind: "angle", i, j, k };
      }
      return null;
    })
    .filter(Boolean);
}

function labelStyleFromContainer(container) {
  const fontSize = parseFloat(container.getAttribute("data-label-size") || "12");
  const fontColor = container.getAttribute("data-label-color") || "#111";
  const bg = container.getAttribute("data-label-bg") || "rgba(255,255,255,0.80)";
  const border = container.getAttribute("data-label-border") || "rgba(0,0,0,0.25)";
  return {
    fontSize,
    fontColor,
    backgroundColor: bg,
    borderColor: border,
    borderThickness: 1,
    inFront: true,
    showBackground: true,
  };
}

function addMeasurementLabels(viewer, model, measures, container) {
  if (!measures.length) return;

  const atoms = model.selectedAtoms({});
  const style = labelStyleFromContainer(container);

  const getAtom = (idx1) => atoms[idx1 - 1]; // 1-based to 0-based

  measures.forEach((m) => {
    if (m.kind === "dist") {
      const a = getAtom(m.i);
      const b = getAtom(m.j);
      if (!a || !b) return;
      const d = dist(a, b);
      const pos = midpoint(a, b);
      // slight offset to reduce overlap with bonds
      pos.z += 0.12;
      viewer.addLabel(`${d.toFixed(2)} Å`, { position: pos, ...style });
    } else if (m.kind === "angle") {
      const a = getAtom(m.i);
      const b = getAtom(m.j);
      const c = getAtom(m.k);
      if (!a || !b || !c) return;
      const ang = angleDeg(a, b, c);
      // Place label near the vertex atom with a small offset
      const pos = { x: b.x, y: b.y, z: b.z + 0.22 };
      viewer.addLabel(`${ang.toFixed(1)}°`, { position: pos, ...style });
    }
  });
}

async function renderMol3D(container) {
  const modelUrl = container.getAttribute("data-model");
  const style = container.getAttribute("data-style") || "stick";
  const background = container.getAttribute("data-bg") || "white";
  const measuresSpec = container.getAttribute("data-measure") || "";

  if (!modelUrl) return;

  container.style.width = container.style.width || "100%";
  container.style.height = container.style.height || "380px";

  const viewer = $3Dmol.createViewer(container, { backgroundColor: background });

  const basePrefix = pagesBasePrefixFromCanonical();
  const candidates = [];

  // If someone uses "/assets/..." (works on local `mkdocs serve`),
  // it *won't* work on GitHub Pages project sites (needs "/<repo>/assets/...").
  if (modelUrl.startsWith("/assets/") && basePrefix) {
    candidates.push(`${basePrefix}${modelUrl}`);
  }
  candidates.push(modelUrl);
  if (modelUrl.startsWith(`${basePrefix}/assets/`)) {
    candidates.push(modelUrl.replace(basePrefix, ""));
  }

  let data;
  try {
    const fetched = await fetchTextWithFallback(candidates);
    data = fetched.text;
  } catch (err) {
    container.innerText = `Failed to load model. Tried: ${candidates.join(", ")}`;
    return;
  }

  // Try SDF first; 3Dmol also supports "mol" for V2000 molfiles.
  // We'll guess from extension if present.
  const ext = (modelUrl.split(".").pop() || "").toLowerCase();
  const format = ext === "mol" ? "mol" : "sdf";

  const model = viewer.addModel(data, format);

  if (style === "sphere") viewer.setStyle({}, { sphere: { scale: 0.3 } });
  else if (style === "line") viewer.setStyle({}, { line: {} });
  else viewer.setStyle({}, { stick: {} });

  const measures = parseMeasures(measuresSpec);
  addMeasurementLabels(viewer, model, measures, container);

  viewer.zoomTo();
  viewer.render();
}

function renderAllMol3D() {
  if (typeof $3Dmol === "undefined") return;
  document.querySelectorAll(".mol3d").forEach((el) => {
    // Avoid double-render on MkDocs live reload
    if (el.getAttribute("data-rendered") === "true") return;
    el.setAttribute("data-rendered", "true");
    renderMol3D(el).catch((err) => {
      el.innerText = `3D render error: ${err?.message || String(err)}`;
    });
  });
}

// MkDocs Material does instant navigation; hook both events.
document.addEventListener("DOMContentLoaded", renderAllMol3D);
document.addEventListener("navigation:complete", renderAllMol3D);

