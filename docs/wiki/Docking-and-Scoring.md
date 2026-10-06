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

`evals/redock.mjs` defines eleven cases. The last recorded run:

**5 of 11 succeed. 9 of 11 are reachable.**

| Case | PDB | Ranked | Best found | Failure mode |
| --- | --- | --- | --- | --- |
| CDK5 · roscovitine analogue | 1UNL | 6.00 Å | **1.29 Å** | scoring |
| GSK-3β · indirubin-3-monoxime | 1Q41 | 6.82 Å | **0.54 Å** | scoring |
| Carbonic anhydrase II · celecoxib | 1OQ5 | 7.50 Å | **1.63 Å** | scoring |
| β-II tryptase | 2BM2 | 5.22 Å | **1.60 Å** | scoring |
| BCL-X<sub>L</sub> · ABT-737 | 2YXJ | 4.59 Å | 3.86 Å | sampling |
| MetAP2 · A-357300 | 1R58 | 3.25 Å | 3.02 Å | sampling |

### The failure mode is ranking, not search

Read the two right-hand columns together. In four of the six failures the search **did** generate a pose
within 2 Å of the crystal — 0.54 Å in the GSK-3β case — and the scoring function ranked something wrong
above it. Only two cases are genuine sampling failures, where no good pose was produced at all.

That is why "reachable" is the more useful number. Perfect ranking over poses the search is *already*
producing would take the benchmark from 45% to 82% with no change to the search whatsoever. The bottleneck
is in the energy terms.

It is worth saying what this cost. Iterations 7, 8 and 10 of the build loop invested in the search —
rigid-body refinement, torsional refinement, binding-mode clustering — while this diagnosis was already
recorded in the repository. The refinement work is correct and the binding-mode work addresses ranking
directly, but the ordering was driven by a superseded four-case benchmark rather than by this one. See
iteration 19 in `docs/ROADMAP_LOOP.md`.

### The four-case set this replaced

Until iteration 19 this page published a four-case table reporting 2 of 4 within 2 Å and a 2.54 Å median.
Those four cases (MAO-B, oestrogen receptor, thrombin, BCL-X<sub>L</sub>) are now four of the eleven, and
the four-case figure is **superseded**. It is recorded here rather than deleted because the figure appeared
in a published whitepaper, deck, investor brief and film, and a number that was shown to people should be
retired in public rather than quietly overwritten.

Neither figure can be re-measured in the current environment: the benchmark fetches structures from the
RCSB and the network is blocked.

### What the benchmark cannot tell you

Eleven cases is still far too few to generalise. It does not measure screening enrichment, it does not measure
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

## Binding modes, and whether the score chose

A ranked list of poses invites one reading: row one is the answer. For the two complexes this tool places
well, that reading is fair. For the two it gets wrong it is not — several placements score within a hair of
each other, the search picks whichever won by a rounding error, and a sorted table presents that as a
result.

So the surviving poses are grouped into **binding modes** by leader clustering at a cutoff coarser than the
1.5 Å de-duplication, and the top two modes are compared. If the gap between them is below a stated margin,
the workspace says so directly: *the next-best sits N Å away and only M behind, so this ranking is not a
preference.* It goes in the toast, and it goes into the provenance record next to the score.

**The margin is a convention, not a measured resolution.** Calibrating it means running the re-docking
benchmark and asking how large a score gap has to be before the better-scoring pose is reliably the closer
one to the crystal. That benchmark needs the network, so the default is a cautious round number, every
caller can override it, and the sentence the workspace produces admits the margin is uncalibrated rather
than implying a rigour it does not have.

This does not improve the score. It makes an existing weakness legible instead of hiding it behind a sort
order, which is the most useful thing available while the weakness cannot be fixed.

## Verifying this page

```bash
node --test tests/refine.test.mjs tests/torsion.test.mjs tests/poses.test.mjs
.venv/bin/python -m pytest tests/test_vina_score_port.py tests/test_dock_seeding.py -q
```

The JavaScript suites test the search and refinement on synthetic geometry — receptors and ligands built so
the right answer is known by construction. The Python suites check the scoring port term by term against
reference values. See [Testing](Testing).
