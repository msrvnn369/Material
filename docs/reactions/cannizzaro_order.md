# Author: msrvnn369
# Date: 2025-12-30

# Cannizzaro reaction: origin of “4th order” kinetics

## Transformation

The **Cannizzaro reaction** is a **base-promoted disproportionation** of a **non-enolizable aldehyde**:

\[
2\,\mathrm{RCHO} \xrightarrow[\text{conc. base}]{} \mathrm{RCH_2OH + RCOO^-}
\]

(Acid workup gives \(\mathrm{RCO_2H}\).)

## Mechanistic core

1. \(\mathrm{OH^-}\) adds to aldehyde → tetrahedral alkoxide (“hemiacetal” anion).
2. A **hydride transfer** occurs from that alkoxide to a second aldehyde molecule → gives a carboxylate + an alkoxide.
3. Proton transfers / workup give alcohol + carboxylate (or acid).

Key step: hydride transfer between two aldehyde-derived species.

## Apparent 4th order: kinetic rationale

In some regimes (often high base and aldehyde concentrations), an empirical rate law of the form:

\[
\text{rate} \propto [\mathrm{RCHO}]^2[\mathrm{OH^-}]^2
\]

is observed (overall order 4). This can arise as an **apparent order** from coupled pre-equilibria and a bimolecular rate-determining step.

Minimal derivation:

Let the reactive donor intermediate be \(I\), formed quickly:

\[
\mathrm{RCHO + OH^- \rightleftharpoons I}
\quad \Rightarrow \quad [I] \approx K[\mathrm{RCHO}][\mathrm{OH^-}]
\]

If the slow step is bimolecular in \(I\):

\[
\text{rate} = k[I]^2
\]

Then:

\[
\text{rate} = kK^2[\mathrm{RCHO}]^2[\mathrm{OH^-}]^2
\]

This dependence is not universal; it is condition- and model-dependent (identity of the kinetically relevant intermediate and the molecularity of the slow step).
