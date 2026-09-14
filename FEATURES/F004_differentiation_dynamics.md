---
id: F004
title: Differentiation dynamics
status: implemented (light)
phase: 2
pairs_with: [B004]
updated: 2026-09-13
slice: S004 / S006
---

## Purpose
Drive continuous `differentiation ∈ [0,1]` per cell from **utility stability**: rise when contribution is stable/high, fall toward STEM when utility drops.

## Why it is fundamental
Static type labels freeze early mistakes. Plasticity coupled to measured usefulness lets the population repair itself under shifting tasks. Commitment without an escape hatch is brittle; pure perpetual STEM never specializes.

## Algorithm (light)
After each utility EMA update (`dsc/differentiation.py`):
- `stable` if `|Δu| ≤ DIFF_STABILITY_EPS`
- rise `DIFF_RISE` when stable (stronger if above median utility)
- fall `DIFF_FALL` when utility drops
- low-utility cells gently decay toward STEM
- EMA blend with `DIFF_EMA_ALPHA`; clip to `[0,1]`

UI: cells with `differentiation < DIFF_STEM_LABEL` (0.35) display as `STEM`; otherwise mixture-argmax type name.

## Persistence
Stored in `checkpoint.npz` as `differentiation` (already in F001 persist path).

## S006 emergence
- `DIFF_PEAK_BONUS` when mixture entropy is low
- Per-cell softmax temperature ↓ with differentiation (`DIFF_TEMP_FLOOR`)
- `emerge_elites` after successful `/evolve` (boost + gate sharpen)
- STEM label threshold `DIFF_STEM_LABEL = 0.30`
