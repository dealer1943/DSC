---
id: F025
title: Harder temporal harness (stress mode)
status: in_progress
phase: DSC core
pairs_with: [F010, F021]
updated: 2026-09-14
---

## Purpose
Widen the task gap on Profile D by raising lag/noise so structure and messaging differences show up beyond ~0.006 lag-1 MSE.

## Eval
`tools.flywire_stress --dsc-family preferential --task-lag 2 --task-noise 0.20 --experiment F025_exp5_hard_harness`
