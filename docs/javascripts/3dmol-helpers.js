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

async function renderMol3D(container) {
  const modelUrl = container.getAttribute("data-model");
  const style = container.getAttribute("data-style") || "stick";
  const background = container.getAttribute("data-bg") || "white";

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

  viewer.addModel(data, format);

  if (style === "sphere") viewer.setStyle({}, { sphere: { scale: 0.3 } });
  else if (style === "line") viewer.setStyle({}, { line: {} });
  else viewer.setStyle({}, { stick: {} });

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

