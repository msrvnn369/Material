# Cannizzaro reaction: why “4th order” shows up (and what it really means)

## The reaction

The **Cannizzaro reaction** is a **base-promoted disproportionation** of a **non-enolizable aldehyde**:

\[
2\,\mathrm{RCHO} \xrightarrow[\text{conc. base}]{} \mathrm{RCH_2OH + RCOO^-}
\]

(Acid workup gives \(\mathrm{RCO_2H}\).)

Classic substrate: benzaldehyde (no \(\alpha\)-H, so no aldol).

## The mechanistic core

At a high level:

1. \(\mathrm{OH^-}\) adds to aldehyde → tetrahedral alkoxide (“hemiacetal” anion).
2. A **hydride transfer** occurs from that alkoxide to a second aldehyde molecule → gives a carboxylate + an alkoxide.
3. Proton transfers / workup give alcohol + carboxylate (or acid).

The famous step is the **hydride transfer between two aldehyde-derived species**.

## So why do some sources say “4th order”?

### What you may see reported

In some kinetic regimes (often **very concentrated base** and **high aldehyde concentration**), authors report a rate law that *appears* like:

\[
\text{rate} \propto [\mathrm{RCHO}]^2[\mathrm{OH^-}]^2
\]

Overall order \(= 4\).

### The key idea: “apparent order” from coupled equilibria + a bimolecular RDS

One consistent way to rationalize a higher apparent order is:

- **Fast pre-equilibrium(s)** create the reactive hydride-donor species from aldehyde + base.
- The **rate-determining step** is then **bimolecular** between:
  - a “donor” species derived from aldehyde + base, and
  - an “acceptor” aldehyde-derived species (often just aldehyde itself, depending on the model).

If the concentration of the donor intermediate is proportional to both \([\mathrm{RCHO}]\) and \([\mathrm{OH^-}]\),
then a bimolecular RDS between two such species can yield terms like \([\mathrm{RCHO}]^2[\mathrm{OH^-}]^2\).

### A concrete (simplified) sketch

Let the reactive donor intermediate be \(I\), formed quickly:

\[
\mathrm{RCHO + OH^- \rightleftharpoons I}
\quad \Rightarrow \quad [I] \approx K[\mathrm{RCHO}][\mathrm{OH^-}]
\]

If the slow step is a bimolecular hydride transfer involving \(I\) and another aldehyde-derived partner (often another \(I\), in simplified treatments):

\[
\text{rate} = k[I]^2
\]

Then:

\[
\text{rate} = kK^2[\mathrm{RCHO}]^2[\mathrm{OH^-}]^2
\]

That’s an **overall 4th-order** dependence, but it hinges on:

- Which intermediate is assumed “reactive”
- Whether one or two aldehyde molecules participate in the slow step
- Whether base participates only via pre-equilibrium(s) or also directly in the RDS

## Practical takeaway

- The Cannizzaro mechanism is fundamentally a **two-aldehyde** process (disproportionation).
- “4th order” is typically an **apparent kinetic order** that can emerge in certain concentration regimes from **pre-equilibria + bimolecular hydride transfer**.
- Different substrates/conditions can show different apparent orders (and competing pathways like Tishchenko can complicate kinetics).

## What we can add next

If you want this to read like a Master Organic Chemistry-style article, the next upgrade is to pin to a specific, cited mechanistic model and show:

- Full curved-arrow hydride transfer step (with a consistent convention)
- Experimental kinetic plots / linearizations (what was actually fit)
- How ionic strength and water activity affect the observed order
