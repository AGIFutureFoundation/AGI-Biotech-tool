# Agent Training System

**Last verified:** 2026-09-22
**Status of this subsystem:** a working reinforcement-learning scaffold trained against a
synthetic environment. It has never been trained on real molecular results.

---

## Read this first

This document previously reported learning curves — "Optimizer expertise 0% → 78%",
"Analyst accuracy 60% → 92%", "Orchestrator success rate 70% → 95%" — as though agents had
been trained and measured.

They had not. `server/agent_training_system.py` generates its own rewards:

```python
success_rate    = 0.7 + (0.3 * random.random())
best_score      = -8.0 - (random.random() * 2)   # "-10 to -8 kcal/mol"
hotspot_count   = random.randint(2, 5)
analysis_quality = 0.8 + (0.2 * random.random())
```

The environment simulator invents the outcome of every action. An agent that learns from
this learns the shape of a random number generator, not molecular chemistry. The
"binding energies" in the reward signal are drawn from a uniform distribution and given
kcal/mol units.

Every performance table and learning curve has been removed from this document rather than
restated with different numbers. There is nothing measured to replace them with.

Also removed: references to `js/agent_training_interface.js` and
`js/immersive-xr-enhanced.js`, which do not exist in this repository. The real front-end
modules are `js/agent.js`, `js/xr.js`, `js/hands.js` and `js/voice.js`.

---

## What actually exists

### `server/agent_training_system.py`

| Component | What it does |
|---|---|
| `EnvironmentSimulator` | Holds scenario state, applies actions, emits **synthetic** rewards. |
| `AgentBrain` | Per-agent value estimates, TD updates, 10,000-entry experience replay buffer, batch size 32, learning rate 0.01. |
| `MultiAgentTrainer` | Runs episodes across the three agents, tracks per-episode metrics. |
| `TrainingCoordinator` | Drives a four-phase curriculum and records milestones. |

The learning machinery is real code: temporal-difference value updates, experience replay
with random batch sampling, and a difficulty curriculum (0.3 → 0.6 → 0.8 → 1.0). What is
synthetic is everything it learns *from*.

### `server/agent_specialization_modules.py`

Three role modules, also partly driven by `random`:

- **`OptimizerModule`** — suggests docking parameters (box size, exhaustiveness, num_modes),
  updates an expertise score from returned binding scores, keeps per-target history.
- **`AnalystModule`** — pose diversity and clustering, frequency-based scaffold detection,
  synthesis-difficulty estimates.
- **`OrchestratorModule`** — workflow planning, load distribution across agents, efficiency
  tracking and contingency planning.

Expertise scores start at 0.0 and move in response to whatever scores they are fed. Fed
synthetic scores, they produce synthetic expertise.

---

## The curriculum

Four phases of increasing difficulty. This is the design, not a record of training that
happened:

```
Phase 1  BASIC        (difficulty 0.3)  simple docking, single-compound analysis
Phase 2  INTERMEDIATE (difficulty 0.6)  multi-agent coordination, 5-10 compounds
Phase 3  ADVANCED     (difficulty 0.8)  complex workflows, 20+ compound screening
Phase 4  EXPERT       (difficulty 1.0)  unknown scenarios, adaptive learning
```

Reward structure:

| Event | Reward |
|---|---|
| Successful docking | 5–10 |
| Analysis completion | 5–20 |
| Parameter exploration | 3 |
| Workflow completion | 20 |
| Poor binding score | 0–5 |

---

## Using it

```python
from agent_training_system import MultiAgentTrainer

trainer = MultiAgentTrainer()
perf = trainer.get_agent_performance('optimizer')
# episodes_trained, avg_reward, improvement_rate
```

Any number that comes back is a property of the simulator. Do not report it as a capability
of the platform.

---

## What would make this real

The scaffold is worth keeping — the learning machinery is sound and the integration points
are in place. What it needs is a real reward signal.

1. **Replace `EnvironmentSimulator`'s synthetic outcomes** with real ones. The real docking
   path is `js/dock.js`; the real dynamics path is the OpenMM `/api/md` endpoint. Neither
   is currently wired to the trainer.
2. **Route through the real engines, not `molecular_research_pipeline.py`.** That module
   also returns `[SYNTHETIC]`-labelled placeholders, so training against it would change
   nothing.
3. **Then measure.** Once the reward signal is real, expertise curves become meaningful and
   can be reported — with the run that produced them.
4. **Adopt the synthetic-provenance discipline.** `server/synthetic_provenance.py` already
   marks placeholder values with `[SYNTHETIC]`, attaches a `provenance` field and raises
   `SyntheticResultWarning`. The training system predates that convention and should use
   it, so its outputs cannot be mistaken for measurements.

---

## Verified state of the wider repository

As of 2026-09-22, and run in CI on every push:

| Check | Result |
|---|---|
| `make test` | 708 passed, 1 xfailed |
| `make reachable` | 22 of 22 JS modules reachable |
| Panel citations | 910/910 across four panels |
| Repurposing recall | 5 of 7 documented cases, both misses explained |

---

## Research focus

The workspace is built to serve research into ALS, Parkinson's, paediatric oncology and
paediatric skeletal and neuromuscular conditions. That describes design intent.
**No partnership, agreement, sponsorship or endorsement exists with any organisation
working in these areas.**
