# Hydrogen: spherical coordinates & the wave equation (interactive)
This page is an interactive companion to the LibreTexts section on the hydrogen atom.

It’s meant to make the **spherical coordinate system** feel concrete:

- You can place a **point** at \((r,\theta,\phi)\) and see where it lands in 3D.
- You can overlay “coordinate surfaces”:
  - **constant \(\phi\)** → a *half-plane* through the \(z\)-axis (like slicing an orange)
  - **constant \(\theta\)** → a *cone* around the \(z\)-axis
- You can render simple hydrogen models from the separated Schrödinger solution:
  \[
  \psi_{nlm}(r,\theta,\phi) = R_{nl}(r)\,Y_l^m(\theta,\phi)
  \]

---

## Interactive 3D explorer

<div class="hydrogen3d"></div>

---

## Notes on conventions (what this widget assumes)

- \(\theta\) is the **polar angle** down from the \(+z\) axis (\(\theta=0^\circ\) points along \(+z\)).
- \(\phi\) is the **azimuthal angle** in the \(xy\)-plane measured from \(+x\) toward \(+y\).
- Distances are shown in **Bohr radii** (atomic units) for the orbital model grid.

