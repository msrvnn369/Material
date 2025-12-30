# Organic Chemistry Notes (Docs Site)

This repo contains an MkDocs site for compiling **organic reactions**, **mechanisms**, **exceptions**, and **3D molecular models**.

## View the site

### Option A: open the already-built static site (fastest)

The static build output is in `site/`.

- Open `site/index.html` in a browser.

### Option B: build + serve locally

```bash
python3 -m pip install -r requirements.txt
python3 -m mkdocs serve
```

## What’s included right now

- SN2 overview + common exceptions: `docs/reactions/sn2.md`
- Reimer–Tiemann overview: `docs/reactions/reimer_tiemann.md`
- Cannizzaro “4th order” discussion: `docs/reactions/cannizzaro_order.md`
- Assets workflow (SVG + 3D models): `docs/graphics_and_models.md`
