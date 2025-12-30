/**
 * Simple helper for embedding SDF/MOL blocks in MkDocs pages.
 *
 * Usage (in Markdown):
 * <div class="mol3d" data-model="/assets/molecules/ethanol.sdf"></div>
 */
async function renderMol3D(container) {
  const modelUrl = container.getAttribute("data-model");
  const style = container.getAttribute("data-style") || "stick";
  const background = container.getAttribute("data-bg") || "white";

  if (!modelUrl) return;

  container.style.width = container.style.width || "100%";
  container.style.height = container.style.height || "380px";

  const viewer = $3Dmol.createViewer(container, { backgroundColor: background });

  const res = await fetch(modelUrl);
  if (!res.ok) {
    container.innerText = `Failed to load model: ${modelUrl}`;
    return;
  }
  const data = await res.text();

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

