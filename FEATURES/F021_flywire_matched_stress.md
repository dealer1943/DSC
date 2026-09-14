---
id: F021
title: FlyWire matched-topology stress test (Profile D path)
status: implemented
phase: comparison
pairs_with: [F011, F020, B016, R002]
updated: 2026-09-14
---

## Purpose
Find **where DSC must grow** to beat FlyWire on a *fair* efficiency fight — same DSC software and harness, different wiring: synthetic ER vs a FlyWire-derived subgraph of matched size.

This is the stress test behind B016 **Profile D**. Profiles A–C alone cannot claim “better than FlyWire wiring.”

## Stress question
Holding `N`, harness, seed protocol, and population init fixed:

> Does FlyWire-shaped connectivity yield better task utility per tick / per edge than DSC’s ER substrate — and if so, on which metrics?

Gaps (fly better OR DSC failing absolute gates on fly wiring) become the development backlog.

## Protocol `stress_d_v0`

| Step | Action |
|------|--------|
| 1 | Extract FlyWire subgraph `N∈{128,512}` (neuropil-focused or degree-seeded BFS) → `MODELS/fly/subgraphs/` |
| 2 | Build two runtimes: (A) ER substrate `generate_substrate(N)` (B) `Substrate(fly_adj)` |
| 3 | Identical `init_population` seed, harness, warm `T_warm`, optional evolve `E`, eval ticks `T_eval` |
| 4 | Record task_error, utility terms, tick_wall_us, edges, density, E_* |
| 5 | Emit gap table: metric → winner → delta → **dev hint** |

## Development targets the stress is designed to expose

| If fly wiring wins on… | Likely DSC growth area |
|------------------------|------------------------|
| `task_error` (lower) | Spatial inductive bias / motif structure (F001 family beyond ER) |
| `E_tick` | Cheaper message passing; sparse gather; typed routing |
| `E_edge` | Prune / latent (F007) while keeping coverage (F008) |
| `utility` vector | F005 term balance; type emergence (F004) under biological degree skew |
| Stability / NaNs | F009 rollback; numerical guards on hub-heavy graphs |
| Scale-up N=512 fails | Memory layout; batching; offline pack streaming |

## CLI

```bash
PYTHONPATH=. python -m tools.flywire_stress --n 128 --neuropil GNG --seed 42 --ticks 256
```


## Shipped
`tools/flywire_stress.py` Profile D runner + subgraph extractor + ledger; used for F022–F030 A/Bs and standings sweeps.
## Non-goals
- Claiming biological equivalence
- Training on full 16M-edge FlyWire as DSC substrate
- Replacing R002 baseline snapshot

## Acceptance
1. Subgraph extractor offline, path-safe names
2. Profile D report with side-by-side ER vs fly-adj + gap/dev hints
3. Documented link from B016 Profile D → this feature
