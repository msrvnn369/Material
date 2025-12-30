# Author: msrvnn369
# Date: 2025-12-30

# Reimer–Tiemann reaction (mechanism-first)

## What it does

The Reimer–Tiemann reaction is a **formylation of phenols** (classically giving **salicylaldehyde** from phenol) using **chloroform + strong base**.

Typical conditions: \(\mathrm{CHCl_3}\), \(\mathrm{NaOH}\) or \(\mathrm{KOH}\), heat; then acidic workup.

## The key reactive intermediate: dichlorocarbene

Base deprotonates chloroform:

\[
\mathrm{CHCl_3 + OH^- \rightleftharpoons CCl_3^- + H_2O}
\]

Then \(\mathrm{CCl_3^-}\) undergoes \(\alpha\)-elimination to give **dichlorocarbene**:

\[
\mathrm{CCl_3^- \rightarrow :CCl_2 + Cl^-}
\]

This step is favorable because it forms chloride (good leaving group) and a neutral carbene.

## Why phenol is required (and why base matters)

Under basic conditions, phenol becomes **phenoxide**, which is:

- **More nucleophilic** than phenol.
- Directing strongly **ortho/para** (via resonance donation into the ring).

## Ring attack and “where the formyl group comes from”

Mechanistic sketch (conceptual):

1. **Phenoxide ring attacks :CCl₂** at an **ortho/para** position → forms a \(\sigma\)-complex.
2. Rearomatization gives an aryl–CCl₂ substituted intermediate.
3. Under strongly basic aqueous conditions, the –CCl₂ group is converted (via hydrolysis) to a **–CHO** after workup.

> The important idea: **the carbon of the formyl group comes from chloroform** via the carbene.

## Regioselectivity (why ortho often dominates)

In many phenols:

- Ortho is favored because the **phenoxide oxygen can coordinate / chelate** in the transition state and because intramolecular H-bonding can stabilize products like salicylaldehyde.
- Sterics can push para if ortho is blocked.

## A minimal electron-pushing figure

For now this repo includes a **starter SVG** (meant as a placeholder until we generate ChemDraw-quality figures):

![Reimer–Tiemann (placeholder mechanism overview)](../assets/mechanisms/reimer_tiemann_placeholder.svg)

## Common failure modes

- Too little base → insufficient carbene generation.
- No phenoxide (weak base) → sluggish ring attack.
- Strongly deactivated rings → poor yield.

## Notes

This page is a “mechanism-first” overview. Next iteration can add:

- Stepwise intermediates with curved arrows and resonance forms.
- Substituent effects and para/ortho ratio trends.
- Variants (e.g., using \(\mathrm{CBrCl_2}\) analogs) if you want them included.
