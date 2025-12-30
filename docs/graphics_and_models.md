# Graphics & 3D models workflow

This site is set up so you can keep **repeatable, consistent** assets:

- Mechanism figures: `docs/assets/mechanisms/` (SVG preferred)
- Molecule models: `docs/assets/molecules/` (SDF or MOL)

## Mechanism graphics (electron-pushing)

### Recommended authoring workflow

- **ChemDraw** (or similar) for structures + curved arrows
- Export as **SVG** into `docs/assets/mechanisms/`
- Embed in Markdown:

```markdown
![Caption](/assets/mechanisms/my_figure.svg)
```

### Conventions to keep figures consistent

- Use **curved arrows** with clear start/end points.
- Use **lone pairs** only when mechanistically relevant.
- Keep **charges explicit** where electron flow depends on them.
- Prefer **separate panels** for multi-step mechanisms.

## 3D molecule models

### File formats

- **SDF** (`.sdf`): great default, supports 3D coordinates.
- **MOL** (`.mol`): also supported.

Place files under `docs/assets/molecules/`.

### Embedding an interactive viewer

Add a div like this:

```html
<div class="mol3d" data-model="/assets/molecules/ethanol.sdf" data-style="stick"></div>
```

Supported attributes:

- `data-model`: required, path under `/assets/molecules/...`
- `data-style`: `stick` (default), `line`, `sphere`
- `data-bg`: `white` (default) or any CSS color

## How to generate 3D coordinates (practical options)

- **From online**: download SDF from PubChem, ChemSpider, etc. (check license/terms).
- **From local tools**:
  - RDKit (Python) to embed and optimize conformers
  - Open Babel to convert SMILES → SDF and do quick 3D generation

If you tell me your preferred toolchain (ChemDraw-only vs open-source), I can add scripts under `tools/` to automate:

- SMILES → 3D SDF generation
- Batch rendering “thumbnail” PNGs
- Consistent SVG export + optimization for web
