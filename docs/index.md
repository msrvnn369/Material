# Organic Chemistry Notes

This repo is a **curated compilation** of organic reactions, mechanisms, rules-of-thumb, and the places those rules break.

## What you'll find here

- **Reaction summaries**: major patterns, scope, and common exam/lab traps.
- **Mechanism-first explanations**: electron-pushing logic, not just memorized outcomes.
- **Graphics + models**: a workflow to maintain **consistent SVG mechanism figures** and **3D molecular models** you can embed in pages.

## How to build the site locally

```bash
python3 -m pip install -r requirements.txt
python3 -m mkdocs serve
```

Then open the local URL printed in the terminal.

## Conventions

- Curved-arrow steps are shown as **SVG figures** stored under `docs/assets/mechanisms/`.
- 3D models (SDF/MOL) are stored under `docs/assets/molecules/` and embedded with a small helper.
- Chemical equations use MathJax (for example: \( \mathrm{RO^- + R'X \rightarrow ROR' + X^-} \)).
