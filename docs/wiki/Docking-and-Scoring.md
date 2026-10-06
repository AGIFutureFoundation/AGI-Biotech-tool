# Docking and Scoring

This is the part of the product most likely to mislead you, so it gets the most honest page.

## What the score is

An empirical function shaped like AutoDock Vina's: five distance-dependent terms summed over every
protein-ligand atom pair inside a cutoff, then divided by a rotatable-bond penalty.

| Term | What it rewards or punishes |
| --- | --- |
| `gauss1`, `gauss2` | Steric complementarity at two length scales |
| `repulsion` | Atoms closer than the sum of their radii |
| `hydrophobic` | Carbon and halogen pairs in contact |
| `hbond` | Donor-acceptor pairs at hydrogen-bonding distance |
| rotatable-bond divisor | Entropy lost by freezing a flexible ligand |

Pair distances are measured surface to surface, using one shared radius table (`contactRadius` in
`js/dock.js`) so the scoring function and the dynamics engine cannot disagree about how big an atom is.

## What the score is not

**It has no units.** It is not kcal/mol, not ΔG, not a K<sub>d</sub>, and it is not calibrated against any
affinity dataset. The published Vina weights were fitted to a training set with Vina's own radii, typing
and search; this is a port, not that program. Every place the number is displayed says so, and the
provenance ledger records `ESTIMATE: unvalidated in-browser score, not kcal/mol` next to it.

Use it to rank compounds against one target in one pocket. Do not compare across targets, do not convert
it to an affinity, and do not put it in a figure caption without the caveat attached.

## How well it places a ligand

Re-docking is the test that matters: take a complex whose answer the crystal structure already gives,
extract the ligand, dock it back, and measure RMSD to where it really sat.

| Case | PDB | Top-pose RMSD | Crystal score | Docked score | Result |
| --- | --- | --- | --- | --- | --- |
| MAO-B · safinamide | — | 1.20 Å | −9.62 | −10.01 | pass |
| Oestrogen receptor · 4-OHT | — | 1.24 Å | −9.24 | −10.13 | pass |
| Thrombin · inhibitor | — | 3.83 Å | −11.03 | −8.34 | fail |
| BCL-X<sub>L</sub> · ABT-737 | 2YXJ | 4.04 Å | −9.96 | −6.92 | fail |

**2 of 4 within 2 Å. Median 2.54 Å.**

### Which half fails, and why that is predictable

The two passes are compact ligands in deep, enclosed, mostly rigid sites. The two failures are large and
flexible in shallow or groove-shaped sites. ABT-737 is a long peptidomimetic lying in a surface groove
where the pocket barely constrains it; the search has far more plausible placements to choose between and
the score cannot tell them apart. That is a known weakness of this class of scoring function, not a bug
specific to this implementation.

The pattern is useful: it tells you the tool is more trustworthy on the enzyme-and-small-molecule problems
than on protein-protein interface inhibitors.

### What the benchmark cannot tell you

Four cases is far too few to generalise. It does not measure screening enrichment, it does not measure
ranking across a congeneric series, and re-docking is the easiest version of the problem — the ligand's
bound conformation came from the structure it is being docked back into. Cross-docking into a different
structure of the same protein is harder and has not been measured.

This figure is **carried forward from the last run with network access** and is re-measured by
`node evals/redock.mjs`, which fetches structures from the RCSB. It is the first thing re-run when the
network allows.

## The search

1. **Grid.** A neighbour grid over the receptor, with the co-crystal ligand's own atoms excluded so an
   extracted ligand cannot clash with the ghost of itself.
2. **Pocket detection.** Grid points ranked by volume and enclosure.
3. **Monte Carlo.** Twelve runs by default, rigid-body moves plus torsion moves, Metropolis acceptance.
4. **Rigid-body refinement** (`js/refine.js`). Pattern search over six degrees of freedom with a shrinking
   step. The MC search stops wherever its last accepted move landed, which is near a minimum rather than in
   it; Vina follows every run with a quasi-Newton polish for the same reason. Rotations pivot on the ligand
   centroid, so a rotation probe never also translates the molecule.
5. **Torsional refinement** (`js/torsion.js`). Pattern search over every rotatable bond, alternating with
   step 4 until a full pass of both stops helping. Rotating one side of a bond about that bond's own axis
   changes exactly one dihedral: every bond length and bond angle is left intact, which is checked to
   1e-4 Å and 1e-4 rad in the tests.

Every refinement stage accepts **only strict improvements**, so a refined pose can never score worse than
the pose it started from. That property is unit-tested rather than asserted.

### What refinement does not do

It does not change the scoring function, and it does not generate conformers. `vinaScore` sees
protein-ligand contacts only — there is no internal-strain term — so a torsion that folds the ligand onto
itself costs nothing in this search. Refinement polishes the conformer it was handed. And a pose placed in
the wrong pocket is still in the wrong pocket; a tighter fit to an unvalidated score is not a better
prediction.

**Whether refinement improves the four-case benchmark has not been measured.** It cannot be until the
network allows the structures to be fetched. The figure above is not restated as improved.

## Verifying this page

```bash
node --test tests/refine.test.mjs tests/torsion.test.mjs
.venv/bin/python -m pytest tests/test_vina_score_port.py tests/test_dock_seeding.py -q
```

The JavaScript suites test the search and refinement on synthetic geometry — receptors and ligands built so
the right answer is known by construction. The Python suites check the scoring port term by term against
reference values. See [Testing](Testing).
