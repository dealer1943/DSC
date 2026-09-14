---
id: F027
title: Laminar substrate family (optic / ME–LO prior)
status: implemented
phase: DSC core
pairs_with: [F001, F021, F022, F023]
updated: 2026-09-14
---

## Layman
For the “eye-brain” fight, change the street map to **stacked floors**: lots of local traffic on a floor, fewer stairs between floors. Every cell on that run uses this map. We do **not** force cells to become an “optic type.”

## Technical
Family `laminar_directed` (`--dsc-family laminar|optic|sheets`):
- Partition N nodes into L sheets (~√N/2, clipped 4–16)
- ~75% edges: local within-layer digraph
- ~25% edges: adjacent-layer bridges (mostly feed-forward)
- `target_edges` matched to FlyWire subgraph budget (Profile D)

## Eval
```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --dsc-family laminar --experiment F027_exp6_laminar_ME_R
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil LO_R --dsc-family laminar --experiment F027_exp6_laminar_LO_R
```

Preferential stack remains default for GNG/AVLP.

## Results (N=512 hard harness, hub-aware on)

| neuropil | family | fly wins | dsc wins | dsc task_err | fly task_err |
|----------|--------|----------|----------|--------------|--------------|
| ME_R | laminar | 3 | 3 | 0.10132 | 0.10118 |
| LO_R | laminar | 5 | 1 | 0.10129 | 0.10124 |

ME_R: **tie** on scoreboard (was a fly win under preferential panel). LO_R still fly-favored.
