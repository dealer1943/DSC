---
id: B010
title: Task performance versus active footprint
status: implemented
tier: feature
measures: [F010]
updated: 2026-09-13
---

## Purpose
On the temporal harness, report accuracy (or task MSE) jointly with active cell count, dormant count, and simple compute proxies (e.g., synaptic ops / activation sparsity), including a pre/post-pruning Pareto comparison.

## What integrity looks like
MVP success is competence **with** compactness. Reporting either axis alone allows optimizing the wrong one; the benchmark always pairs them.


## Runnable
```bash
PYTHONPATH=. python -m tools.benches.b010_task_footprint --ticks 64 --seed 42
```
Reports `task_error` with `disk_bytes`, `n_edges`, sparsity, and E_disk / E_edge. Pass: `task_error<=0.05` (aligned with F020 G1). Temp copy of tip.
