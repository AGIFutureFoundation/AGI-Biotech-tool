# Getting Started

## Install and run

```bash
git clone https://github.com/AGIFutureFoundation/AGI-Biotech-tool.git
cd AGI-Biotech-tool
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
make serve
```

Then open <http://localhost:8000>. SOD1 — the first gene linked to ALS — loads on open, so there is a real
structure on screen before you touch anything.

There is no build step and no `npm install`. The client is ES modules and an import map; three.js is
fetched from a CDN at the version pinned in the page. Editing a file in `js/` and reloading is the whole
development loop.

## What needs what

| You want | You need |
| --- | --- |
| The viewport, docking, in-browser MD, analysis | A browser. Nothing else. |
| Public database lookups, known drugs, evidence | Outbound network |
| All-atom MD, RDKit conformers, SDF export | The Python server (`make serve`) |
| Hand tracking, room-scale, the wrist panel | A WebXR headset, or `?emulate=quest3` |
| Agent control from outside the browser | The MCP server, `server/mcp_server.py` |

The Python server is optional for the core loop. It exists for the things a browser cannot do: OpenMM,
RDKit conformer generation, and acting as an allowlisted proxy for databases that refuse cross-origin
requests.

## Without a headset

`?emulate=quest3` puts the headset interface on screen in a desktop browser — the wrist panel, the
controller rays, the room-scale layout — driven by mouse and keyboard. It is how most of the XR work in
this repository was built and reviewed. See [XR and Hand Tracking](XR-and-Hand-Tracking).

## First five minutes

1. **Find pockets.** The ranked list is by volume and enclosure; the top one is selected.
2. **Load a compound.** A SMILES string, an AGI compound identifier, or a name the library knows.
3. **Dock.** Twelve Monte Carlo runs, then rigid-body and torsional refinement. Poses arrive ranked.
4. **Analyse the pose.** Every contact classified by residue. This is the part to trust most.
5. **Verify the ledger.** Everything above is now in a hash chain you can re-verify or export.

Read [Docking and Scoring](Docking-and-Scoring) before you believe step 3's number.

## Every check, one command

| Command | What it proves |
| --- | --- |
| `.venv/bin/python -m pytest tests/ -q` | The Python suite |
| `node --test tests/*.test.mjs` | The JavaScript suites — scoring geometry, voice, agent tools, refinement, this wiki |
| `make imports` | Every module under `server/` and `scripts/` imports cleanly |
| `make reachable` | No orphaned JS module |
| `make egress` | No undeclared outbound host |
| `node evals/redock.mjs` | The re-docking benchmark. **Needs the network.** |

Current measured counts are on [Testing](Testing), each with the date it was measured.
