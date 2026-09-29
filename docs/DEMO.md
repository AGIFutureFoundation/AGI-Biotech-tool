# Demo guide

Three ways to show biodao.blockchain, depending on how much time you have.

## 1. The video (2 minutes 8 seconds)

`docs/biodao-walkthrough.mp4` — 1920x1080, H.264, no audio, captions burned in.
Not committed: the renders are gitignored build output, and a 210 MB master cannot be pushed to
GitHub at all (100 MB per-file cap). Render it before a demo rather than expecting it in a clone.

It is not a screen recording. The app renders the film itself: the scene is drawn to an offscreen
1080p buffer, captions and live readouts are composited on top, and frames are encoded with WebCodecs
on a fixed clock. Every number on screen comes from that run, not from a script.

To regenerate it after changing anything:

```bash
open "http://localhost:8000/?record=1"
```

The page runs the real pipeline first (loads structures, gathers evidence, docks, screens), then renders
the film and posts it to `docs/walkthrough.mp4`. Compress for sharing with:

```bash
ffmpeg -i docs/walkthrough.mp4 -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -movflags +faststart docs/biodao-walkthrough.mp4
```

## 2. The guided demo in the app (about 90 seconds)

Press **▶ Demo** in the top bar. The app drives itself through the same story with captions over the
viewport, and stops at any point if you press it again. Use this when someone is watching live and may
want to interrupt and ask questions.

## 3. Driving it yourself (5 to 20 minutes)

A running order that always works:

| Time | Do this | What to point out |
| --- | --- | --- |
| 0:30 | Targets tab, pick SOD1 | 60 curated targets, every accession checked against UniProt |
| 1:00 | Colour menu, choose `missense` | AlphaMissense: red where mutations are damaging, ALS hotspots stand out |
| 2:00 | Evidence tab, Gather evidence | nine databases at once: domains, pathways, partners, expression, constraint, trials, papers |
| 3:00 | Search `2YXJ` | BCL-XL with ABT-737, straight from the Protein Data Bank |
| 3:30 | Known drugs tab, click the ligand `N3C` | lifts the drug out with correct bond orders |
| 4:00 | Dock ligand | recovers the crystal pose, about 1.5 Å, in roughly 30 seconds |
| 5:00 | Start MD, untick rigid protein | flexible ligand, elastic-network backbone, live score |
| 6:00 | Compounds tab, Quick screen | ranks the library against the open site |
| 7:00 | Session tab, Verify chain | SHA-256 provenance, then Export to anchor it |
| 8:00 | Enter VR (or `?emulate=quest3`) | grip to move, two grips to scale, trigger to grab the ligand |

## Talking points that hold up to questions

- **The docking is validated, once.** Re-docking safinamide into its own MAO-B crystal structure recovers
  the experimental pose to 1.0 Å, scoring −9.98 against the crystal's −9.62. One favourable case, not a
  benchmark.
- **Nothing needs an API key.** Fourteen public databases, all free, no accounts.
- **AlphaFold 3 has no public API.** The app exports jobs in both input dialects and reads predictions back.
- **The interactive physics is deliberately coarse.** Use the OpenMM backend, which reached 27 ns/day on
  this Mac's GPU, for anything you would publish.
