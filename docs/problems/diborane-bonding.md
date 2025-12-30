# Author: msrvnn369
# Date: 2025-12-30

# Diborane (B₂H₆): bonding and geometry

## Question (statements)

- **A)** The two bridged H atoms and the two boron atoms lie in one plane.  
- **B)** Out of six B–H bonds, two can be described as 3-center–2-electron bonds.  
- **C)** Out of six B–H bonds, four can be described as 3-center–2-electron bonds.  
- **D)** The four terminal B–H bonds are 2-center–2-electron regular bonds.

## Answer

**Correct statements: B and D.**

## Bonding classification

- **B–B bond**: present.
- **B–H (terminal)**: **4** bonds; **2-center–2-electron (2c–2e)**.
- **B–H–B (bridging)**: **2** bridges; **3-center–2-electron (3c–2e)**.

Implications for the statements:

- **B** is true: there are exactly **two** bridges → **two** 3c–2e bonds.
- **D** is true: the remaining **four** B–H bonds are terminal → 2c–2e.
- **C** is false: there are not four bridging 3c–2e bonds.
- **A** is false: the two bridging H atoms are displaced **above and below** the \( \mathrm{B_2H_4} \) plane.

## Geometry: coplanarity

Define the **\( \mathrm{B_2H_4} \) plane** as the plane containing the two boron atoms and the four terminal hydrogens.  
The two bridging hydrogens are not in this plane (one is above, one below).

## Labeled 3D model

<div
  class="mol3d"
  data-model="/assets/molecules/diborane_model.sdf"
  data-style="stick"
  data-measure="dist:1-2,dist:1-3,dist:2-5,dist:1-7,dist:2-7,angle:1-7-2"
  data-plane="atoms:1-2-3-4-5-6;size:4;color:#0066cc;opacity:0.18;grid:10"
  data-label-size="8.5"
></div>

## Reference metrics (typical)

- **B–B**: ~**1.77 Å**
- **B–H (terminal)**: ~**1.19 Å**
- **B–H (bridge)**: ~**1.33 Å**
- **∠B–H(bridge)–B**: ~**80–85°**

## Embedded model parameters

The embedded SDF is parameterized to match the reference metrics and to enforce the plane definition:

- \( \mathrm{B_2H_4} \) atoms set to **z = 0**
- bridging H atoms set to **z ≈ ±0.99 Å**
