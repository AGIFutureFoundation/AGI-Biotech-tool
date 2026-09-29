# Optimization & Scaling Guide

**Last verified:** 2026-09-22
**Status of this subsystem:** design scaffolding. Nothing described here is deployed, and
no figure in this document is a measurement.

---

## Read this first

This document previously presented tables of latency, throughput, uptime and ML accuracy
figures under headings like "Performance Metrics (All Verified ✅)", with a "Current"
column implying each number had been measured against a running system.

**None of them had been.** Two modules produced those numbers, and both measure themselves:

- `server/load_testing.py` awaits `asyncio.sleep(random.uniform(0.01, 0.1))` in place of
  doing work. Every throughput and latency figure in the old tables — 596 ops/second,
  p50 45ms, p95 157ms, p99 165ms, 245 ops/sec at p50 — came from timing those sleeps.
- `server/ml_enhanced_recognition.py` returns `random.choice(gestures)` with a
  `random.gauss(model['accuracy'], 0.05)` confidence. The "94% gesture accuracy", "89%
  voice accuracy", "95%+ entity extraction", "96% via active learning" and "82% → 94%
  transfer learning" figures describe a hardcoded constant fed through a random number
  generator.

The "99.5% uptime" figure was never measured by anything at all — nothing in the repository
tracks availability, and there is no deployment to be available.

Those tables have been removed rather than restated with different numbers. There is no
benchmark in this repository, so there is no performance figure to report.

---

## What actually exists

Two modules of in-process Python objects. They are reasonable designs. Nothing is deployed
behind them: there is no Kubernetes cluster, no Redis instance, no PostgreSQL server, no
load balancer and no auto-scaler running anywhere.

### `server/performance_optimization.py`

| Component | What it is |
|---|---|
| `QueryCache` | In-memory dict cache with TTL and max size. Defaults: 1000 entries, 300s. |
| `ConnectionPool` | Async acquire/release over a fixed set of connection objects. Default max 20. |
| `BatchProcessor` | Groups operations, flushes on batch-full or timeout. Defaults: 100 ops, 1000ms. |
| `QueryOptimizer` | Records query durations and emits index suggestions. |
| `MemoryOptimizer` | Tracks registered object sizes against warning/critical thresholds. |

These are unit-tested as data structures. They have never run against a production workload,
so the old claims — "80% reduction in database hits", "90% faster connection acquisition",
"3–5x throughput improvement", "50–90% faster query execution" — describe intent, not
outcome. Where a target is worth keeping as a design goal it is written as a target below,
never as an achieved result.

### `server/scaling_infrastructure.py`

| Component | What it is |
|---|---|
| `LoadBalancer` | Least-loaded instance selection over registered `ServiceInstance` objects. |
| `AutoScaler` | Threshold logic returning scale-up/scale-down decisions. |
| `DistributedCache` | Consistent-hashing key distribution across named nodes. |
| `ServiceMesh` | Per-route timeout, retry and circuit-breaker policy lookup. |
| `ClusterConfig` | Emits Kubernetes manifests as text. |

The Kubernetes manifests are generated text. They have not been applied to a cluster.

---

## Design targets

If this system is ever deployed, these are the targets the modules were written against.
They are goals to measure, not results:

**Scaling policies**

| Service | Scale up at | Scale down at | Min | Max |
|---|---|---|---|---|
| API server | 70% load | 20% load | 3 | 20 |
| Workflow executor | 80% load | 30% load | 2 | 10 |
| Agent orchestrator | 75% load | 25% load | 2 | 8 |

**Cache and pool defaults**

- Query cache: 1000 entries, 300s TTL
- Connection pool: 5 min, 20 max, 300s idle timeout
- Batch processor: 100 operations, 1000ms timeout

**Database indexes** worth creating on a PostgreSQL deployment:

```sql
CREATE INDEX idx_workflows_user_id     ON workflows(user_id);
CREATE INDEX idx_workflows_status      ON workflows(status);
CREATE INDEX idx_workflows_created_at  ON workflows(created_at DESC);
CREATE INDEX idx_checkpoints_workflow_id ON checkpoints(workflow_id);
CREATE INDEX idx_agent_memory_agent_id ON agent_memory(agent_id);
```

`server/database_migration.py` contains a SQLite-to-PostgreSQL path. It has not been run
against a live PostgreSQL instance.

---

## What is actually measured

The repository does have real, reproducible checks — they just measure correctness rather
than performance. As of 2026-09-22:

| Check | Command | Result |
|---|---|---|
| Test suite | `make test` | 708 passed, 1 xfailed |
| Module imports | `make imports` | passes |
| JS reachability | `make reachable` | 22 of 22 modules reachable |
| Panel citations | `scripts/verify_panel_citations.py` | 910/910 across four panels |
| Repurposing recall | `scripts/validate_repurposing_recall.py` | 5 of 7 cases, both misses explained |

These run in CI on every push (`.github/workflows/ci.yml`, `citations.yml`).

The test suite completes in roughly 25 seconds on a development laptop. That is the only
timing figure in this document that comes from an actual run, and it measures the tests,
not the platform.

---

## If you want real performance numbers

Nothing in this repository will produce them. The work would be:

1. **Delete or rewrite `server/load_testing.py`.** As long as it sleeps instead of working,
   any number it produces is noise, and a plausible-looking number is worse than none.
2. **Drive the real endpoints** — `/api/embed`, `/api/extract`, `/api/md` — under
   concurrency, and measure wall-clock latency and throughput against them.
3. **Benchmark docking separately.** `js/dock.js` runs in the browser; measuring it means
   instrumenting the front end, not the server.
4. **Decide what uptime means** before claiming it. There is currently nothing to be up.

Until then, this platform has no measured performance characteristics, and documentation
should say exactly that.

---

## Research focus

The workspace is built to serve research into ALS, Parkinson's, paediatric oncology and
paediatric skeletal and neuromuscular conditions. That describes design intent and scope.
**No partnership, agreement, sponsorship or endorsement exists with any organisation
working in these areas.**

---

See `PROJECT_STATUS.md` for the verified state of each component and
`DEPLOYMENT_GUIDE.md` for what hosting would involve.
