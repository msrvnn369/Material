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

function normalize(v) {
  const n = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z) || 1;
  return { x: v.x / n, y: v.y / n, z: v.z / n };
}

function cross(a, b) {
  return { x: a.y * b.z - a.z * b.y, y: a.z * b.x - a.x * b.z, z: a.x * b.y - a.y * b.x };
}

function add(a, b) {
  return { x: a.x + b.x, y: a.y + b.y, z: a.z + b.z };
}

function sub(a, b) {
  return { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
}

function mul(v, s) {
  return { x: v.x * s, y: v.y * s, z: v.z * s };
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

function parsePlane(spec) {
  // Format:
  // "atoms:1-2-3-4-5-6;size:4;color:#0077cc;opacity:0.22;grid:9"
  if (!spec) return null;
  const parts = spec.split(";").map((s) => s.trim()).filter(Boolean);
  const out = {
    atoms: [],
    size: 4,
    color: "#0077cc",
    opacity: 0.22,
    grid: 9,
  };
  for (const p of parts) {
    const [kRaw, vRaw] = p.split(":");
    const k = (kRaw || "").trim().toLowerCase();
    const v = (vRaw || "").trim();
    if (!k) continue;
    if (k === "atoms") {
      out.atoms = v
        .split("-")
        .map((n) => parseInt(n, 10))
        .filter((n) => Number.isFinite(n));
    } else if (k === "size") out.size = parseFloat(v) || out.size;
    else if (k === "color") out.color = v || out.color;
    else if (k === "opacity") out.opacity = Math.max(0, Math.min(1, parseFloat(v)));
    else if (k === "grid") out.grid = Math.max(3, Math.min(25, parseInt(v, 10) || out.grid));
  }
  return out.atoms.length >= 3 ? out : null;
}

function labelStyleFromContainer(container) {
  const fontSize = parseFloat(container.getAttribute("data-label-size") || "11");
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

function atomTag(atom, idx1) {
  const e = atom?.elem || "?";
  return `${e}${idx1}`;
}

function preferredPerpOffset(vec) {
  // Choose a stable perpendicular direction for label offsets
  const z = { x: 0, y: 0, z: 1 };
  const y = { x: 0, y: 1, z: 0 };
  let p = cross(vec, z);
  const pn = Math.sqrt(p.x * p.x + p.y * p.y + p.z * p.z);
  if (pn < 1e-6) p = cross(vec, y);
  return normalize(p);
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
      const bondVec = normalize(sub(b, a));
      const off = preferredPerpOffset(bondVec);
      const labelPos = add(pos, mul(off, 0.35));
      labelPos.z += 0.10;

      // leader line (best practice: makes it obvious what the label refers to)
      viewer.addLine({
        start: pos,
        end: labelPos,
        color: "#666",
        opacity: 0.6,
        dashed: true,
      });

      const label = `${atomTag(a, m.i)}–${atomTag(b, m.j)}  ${d.toFixed(2)} Å`;
      viewer.addLabel(label, { position: labelPos, ...style });
    } else if (m.kind === "angle") {
      const a = getAtom(m.i);
      const b = getAtom(m.j);
      const c = getAtom(m.k);
      if (!a || !b || !c) return;
      const ang = angleDeg(a, b, c);
      const v1 = normalize(sub(a, b));
      const v2 = normalize(sub(c, b));
      const bis = normalize(add(v1, v2));
      const labelPos = add(b, mul(bis, 0.55));
      labelPos.z += 0.12;

      viewer.addLine({
        start: { x: b.x, y: b.y, z: b.z },
        end: labelPos,
        color: "#666",
        opacity: 0.6,
        dashed: true,
      });

      const label = `∠${atomTag(a, m.i)}–${atomTag(b, m.j)}–${atomTag(c, m.k)}  ${ang.toFixed(1)}°`;
      viewer.addLabel(label, { position: labelPos, ...style });
    }
  });
}

function addPlaneGrid(viewer, model, planeSpec) {
  if (!planeSpec) return;
  const atoms = model.selectedAtoms({});
  const getAtom = (idx1) => atoms[idx1 - 1];
  const pts = planeSpec.atoms.map((i) => getAtom(i)).filter(Boolean);
  if (pts.length < 3) return;

  // pick 3 points to define a plane and build a rectangle centered at centroid
  const c = pts.reduce((acc, p) => add(acc, p), { x: 0, y: 0, z: 0 });
  const centroid = mul(c, 1 / pts.length);

  const a0 = pts[0];
  // find a point not equal to a0
  const a1 = pts.find((p) => dist(p, a0) > 1e-6) || pts[1];
  const a2 = pts.find((p) => {
    const v1 = sub(a1, a0);
    const v2 = sub(p, a0);
    const cr = cross(v1, v2);
    return Math.sqrt(cr.x * cr.x + cr.y * cr.y + cr.z * cr.z) > 1e-6;
  }) || pts[2];

  const u = normalize(sub(a1, a0));
  const n = normalize(cross(sub(a1, a0), sub(a2, a0)));
  const v = normalize(cross(n, u));

  const half = planeSpec.size / 2;
  const p00 = add(add(centroid, mul(u, -half)), mul(v, -half));
  const p10 = add(add(centroid, mul(u, half)), mul(v, -half));
  const p01 = add(add(centroid, mul(u, -half)), mul(v, half));
  const p11 = add(add(centroid, mul(u, half)), mul(v, half));

  // draw outline
  const edges = [
    [p00, p10],
    [p10, p11],
    [p11, p01],
    [p01, p00],
  ];
  edges.forEach(([s, e]) =>
    viewer.addLine({ start: s, end: e, color: planeSpec.color, opacity: Math.min(1, planeSpec.opacity + 0.15) }),
  );

  // draw a grid (gives a “plane” feel without relying on unsupported polygon primitives)
  const steps = planeSpec.grid;
  for (let i = 1; i < steps; i++) {
    const t = -half + (i * planeSpec.size) / steps;
    const s1 = add(add(centroid, mul(u, -half)), mul(v, t));
    const e1 = add(add(centroid, mul(u, half)), mul(v, t));
    viewer.addLine({ start: s1, end: e1, color: planeSpec.color, opacity: planeSpec.opacity });

    const s2 = add(add(centroid, mul(u, t)), mul(v, -half));
    const e2 = add(add(centroid, mul(u, t)), mul(v, half));
    viewer.addLine({ start: s2, end: e2, color: planeSpec.color, opacity: planeSpec.opacity });
  }
}

async function renderMol3D(container) {
  const modelUrl = container.getAttribute("data-model");
  const style = container.getAttribute("data-style") || "stick";
  const background = container.getAttribute("data-bg") || "white";
  const measuresSpec = container.getAttribute("data-measure") || "";
  const planeSpecRaw = container.getAttribute("data-plane") || "";

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

  const planeSpec = parsePlane(planeSpecRaw);
  addPlaneGrid(viewer, model, planeSpec);

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

