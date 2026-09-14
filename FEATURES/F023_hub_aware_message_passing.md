---
id: F023
title: Hub-aware message passing
status: implemented
phase: DSC core
pairs_with: [F002, F022, F021]
updated: 2026-09-14
---

## Purpose
On heavy-tailed / FlyWire-like graphs, high out-degree cells can dominate gathers. F023 damps senders by `out_deg**HUB_OUT_EXP` and normalizes receivers with `log1p(in_deg)` when `defaults.HUB_AWARE` is true.

## Eval
Profile D N=512 with best F022 family (`preferential`) → ledger `F023_exp3_hub_aware`.
## Shipped
`defaults.HUB_AWARE` (default on) damps high out-degree sources + log in-degree normalize in `step_population`.
