---
id: F007
title: Pruning with latent retention
status: implemented
phase: 4
pairs_with: [B007]
updated: 2026-09-13
slice: S005
---

## Purpose
Remove low-utility cells from the **active** set while **moving parameters into a dormant/latent pool** instead of destroying them.

## Algorithm
On each `/evolve` replacement (`dsc/latent.py` + `dsc/evolve.py`):
1. Update `fail_streak` (ticks below utility quantile).
2. Prefer high-streak cells among the bottom replace set.
3. `LatentPool.push_from_pop` archives gate/weights/bias/hidden/utility.
4. Pool capped at `LATENT_POOL_MAX` (FIFO overflow).
5. With `REACTIVATE_RATE`, a victim slot may revive the best *older* latent entry.

Persisted inside `checkpoint.npz` as `latent_*` arrays.
