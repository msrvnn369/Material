# SN2 reactions: major patterns + exceptions

## The core pattern

**SN2** is a single-step substitution where a nucleophile attacks as the leaving group leaves:

\[
\mathrm{Nu^- + R{-}LG \rightarrow R{-}Nu + LG^-}
\]

Key features:

- **One step**: no discrete carbocation.
- **Backside attack**: gives **inversion of configuration** (Walden inversion) at a stereogenic center.
- **Rate law**: \( \text{rate} = k[\mathrm{Nu^-}][\mathrm{R{-}LG}] \).

## Substrate reactivity (typical)

**Methyl > 1° > 2° \(\gg\) 3°** (sterics dominate).

- **3°**: essentially “no SN2” under ordinary conditions; elimination (E2) dominates with strong base.
- **Neopentyl** (formally 1° but very hindered): extremely slow SN2.
- **Benzylic / allylic**: can be fast (transition state stabilized; geometry often accessible).

## Leaving group trends

Good leaving groups are weak bases:

- **Best**: \(\mathrm{I^- > Br^- > Cl^- \gg F^-}\)
- **Sulfonates**: OTs, OMs, OTf are excellent.

Bad leaving groups (unless activated): \(\mathrm{HO^-}\), \(\mathrm{RO^-}\), \(\mathrm{NH_2^-}\).

## Nucleophile trends (SN2 context)

What usually matters: **nucleophilicity + sterics**.

- **Steric hindrance**: bulky nucleophiles slow SN2 and bias E2 (e.g., \(t\)-BuO⁻).
- **Charge**: anions are usually more nucleophilic than neutral analogs.

### Solvent effects (big exception-driver)

**Polar aprotic** solvents (DMSO, DMF, MeCN, acetone) generally **accelerate SN2** by not strongly solvating anions.

**Polar protic** solvents (ROH, H₂O) strongly solvate anions and can **slow SN2**.

Classic “textbook reversal” in protic solvents:

- **Halides as nucleophiles** in protic solvent: \( \mathrm{I^- > Br^- > Cl^- > F^-} \) (more polarizable = less solvated = better nucleophile).
- In polar aprotic solvent, nucleophilicity often tracks basicity more closely for small nucleophiles.

## Stereochemistry: inversion, not scrambling

At a stereocenter, SN2 gives **inversion** (not retention, not racemization).

If you see **racemization**, you’re almost certainly in **SN1** territory (or neighboring group participation / ion pairs, which are special cases).

## “Exceptions” and common traps

### 1) “No SN2 on tertiary” (with special cases)

- Simple 3° alkyl halides: SN2 is blocked sterically.
- **Allylic/benzylic 3°**: substitution can occur, but typically by **SN1/SN1′** pathways (or via resonance-stabilized cations), not classic clean SN2.

### 2) Strong nucleophile vs strong base: SN2 vs E2 competition

Rules of thumb:

- **Hindered base** (e.g., \(t\)-BuO⁻): pushes **E2**.
- **Good nucleophile, weak base** (e.g., \( \mathrm{I^-}\), \( \mathrm{RS^-}\), \( \mathrm{CN^-}\), \( \mathrm{N_3^-}\)): favors **SN2**.
- Higher temperature usually increases elimination fraction.

### 3) Substrate class matters: aryl/vinyl halides

**Aryl/vinyl halides do not undergo SN2** at the C(sp²)–X bond (geometry + partial double-bond character).

Substitution on aryl/vinyl requires different mechanisms (e.g., SNAr with strong EWG + leaving group, benzyne, metal-catalyzed coupling).

### 4) Solvolysis can masquerade as “failed SN2”

If your nucleophile is weak and the solvent is protic, you might drift into SN1/E1 (if cation is stabilized) or just slow/no reaction.

## Quick “decision table”

- **Methyl / 1° substrate + polar aprotic + decent nucleophile** → SN2 very likely.
- **2° substrate + strong base/nucleophile** → SN2/E2 competition; sterics + temperature decide.
- **3° substrate + strong base** → E2.
- **Aryl/vinyl substrate** → not SN2.

## 3D model demo (example)

This is just a proof-of-plumbing (you can replace with any SDF/MOL you add):

<div class="mol3d" data-model="/assets/molecules/ethanol.sdf" data-style="stick"></div>
