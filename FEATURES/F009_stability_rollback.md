---
id: F009
title: Stability checks and cycle rollback
status: implemented (light)
phase: 4
pairs_with: [B009]
updated: 2026-09-13
slice: S004
---

## Purpose
After each evolution cycle, verify the population remains viable; **rollback** if checks fail. Expose `/rollback` to restore last-good.

## Why it is fundamental
Evolutionary updates can destroy controllability or collapse diversity. Guardrailed rollback keeps search inside a viable regime.

## Light checks (`check_stability`)
Fail if:
- any NaN/Inf in population tensors
- mean `|activity|` &lt; `ROLLBACK_FOOTPRINT_MIN`
- activity &lt; `ROLLBACK_FOOTPRINT_REL` × pre-cycle activity
- mean utility drops by more than `ROLLBACK_UTIL_CLIFF` vs pre-cycle (when pre &gt; 0)

## Snapshots
- Pre-cycle automatic snapshot inside `run_cycle`
- `DscRuntime.last_good` refreshed before each `/evolve` batch and after each successful cycle
- `/rollback` restores `last_good` (harness + pop + signal hist)
