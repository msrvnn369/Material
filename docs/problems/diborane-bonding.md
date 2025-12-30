# Author: msrvnn369
# Date: 2025-12-30

# Worked example: Diborane (B₂H₆) bonding + geometry

## The key picture

Diborane is **electron-deficient**. It is best described as:

- **4 terminal B–H bonds** (normal 2-center–2-electron, “2c–2e”)
- **2 bridging B–H–B bonds** (3-center–2-electron, “3c–2e”, also called “banana bonds”)

So, out of the **six** B–H connections:

- **4 are terminal 2c–2e**
- **2 are bridging 3c–2e**

## Interpreting the screenshot-style MCQ

Rewritten cleanly (so we don’t need to publish a textbook photo):

- **A)** The two bridged H atoms and the two boron atoms lie in one plane.  
- **B)** Out of six B–H bonds, two can be described as 3-center–2-electron bonds.  
- **C)** Out of six B–H bonds, four can be described as 3-center–2-electron bonds.  
- **D)** The four terminal B–H bonds are 2-center–2-electron regular bonds.

**Correct statements: B and D.**

Why:

- **B**: there are exactly **two** B–H–B bridges → **two 3c–2e bonds**
- **D**: the remaining **four** B–H bonds are terminal → **2c–2e**
- **C** is wrong for the same reason (only **two** bridges exist, not four).
- **A** is wrong: the **bridging hydrogens are above and below** the plane formed by \( \mathrm{B_2H_4} \).

## The “coplanar 6 atoms” plane

The **two boron atoms** + the **four terminal hydrogens** form an (approximately) **single plane** (often described as the **\( \mathrm{B_2H_4} \)** plane).  
The **two bridging H** atoms sit **one above** and **one below** that plane.

That’s the clean geometric reason A is not correct.

## Interactive 3D model (with labeled structure)

This is a simple bridged model intended for teaching (SDF does not have true “3-center bonds”, so we represent each bridge as two B–H single bonds):

<div
  class="mol3d"
  data-model="/assets/molecules/diborane_model.sdf"
  data-style="stick"
  data-measure="dist:1-2,dist:1-3,dist:2-5,dist:1-7,dist:2-7,angle:1-7-2"
  data-plane="atoms:1-2-3-4-5-6;size:4;color:#0066cc;opacity:0.18;grid:10"
  data-label-size="10.5"
></div>

## Typical bond lengths / angles (order-of-magnitude correct)

These are the standard numbers students are usually expected to know (values vary slightly by method/phase):

- **B–H (terminal)**: ~**1.19 Å**
- **B–H (bridge)**: ~**1.33 Å** (longer / weaker than terminal)
- **B–B**: ~**1.77 Å**

Angle highlights:

- **B–H–B (bridge angle)** is **acute** (often quoted around **80–85°**)
- The **terminal H–B–H** angle is around **120°** (each B is close to trigonal-planar-like when viewed as “two terminal + one bridge region”)

### Values used by the embedded teaching model

The embedded `diborane_model.sdf` is constructed so the core teaching numbers match the list above:

- **B–B** = **1.77 Å**
- **terminal B–H** = **1.19 Å**
- **bridge B–H** = **1.33 Å**
- **terminal H–B–H** ≈ **120°**
- **B–H(bridge)–B** ≈ **84°**

And it enforces the coplanarity idea very explicitly:

- **Coplanar 6 atoms**: \( \mathrm{B_2H_4} \) are set to **z = 0**
- **Bridge H atoms**: one at **z ≈ +0.99 Å**, one at **z ≈ −0.99 Å**

## What we can add next (if you want it even more “exam-ready”)

- A clean SVG diagram with curved-arrow *orbital donation picture* (3c–2e MO cartoon).
- A “plane highlight” figure: show the \( \mathrm{B_2H_4} \) plane and label which atoms are in/out of plane.
- A second 3D view with **distance labels** and **angle labels** drawn onto a static figure (for PDFs/handouts).
