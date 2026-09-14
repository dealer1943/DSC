---
id: F024
title: Prune + coverage under degree skew
status: implemented
phase: DSC core
pairs_with: [F007, F008, F021, F022, F023]
updated: 2026-09-14
---

## Purpose
Stress F007/F008 on preferential (+ hub-aware) vs FlyWire-adj at N=512 with aggressive evolve/prune so coverage and task do not collapse on hub-heavy graphs.

## Eval
`tools.flywire_stress --dsc-family preferential --prune-stress --experiment F024_exp4_prune_coverage`

## Fix (2026-09-14)
Hub-aware absorb: neighbor bonus, hub penalty, wider absorb set on sparse graphs. Substrate threaded into `run_cycle`.
## Shipped
`--prune-stress` overrides + hub-aware absorb; exercised on preferential Profile D.
