---
id: F006
title: Evolution loop
status: implemented (MVP)
phase: 3
pairs_with: [B006]
updated: 2026-09-13
slice: S004
---

## Purpose
Periodic population update: evaluate → select/prune slots → clone top-K → mutate parameters (rarely type logits).

## Why it is fundamental
Dynamic states are not a fixed network trained once. Generational pressure is how the connectome discovers and refreshes its repertoire.

## Algorithm (MVP)
`dsc/evolve.py` · `/evolve [n]` (default 1, max 32):
1. Rank by multi-term utility (F005).
2. Keep top `EVOLVE_TOP_K`; replace bottom `EVOLVE_REPLACE_FRAC` slots.
3. Each victim ← clone of random elite + Gaussian param noise (`EVOLVE_MUTATE_SIGMA`).
4. With `EVOLVE_TYPE_MUTATE_RATE`, nudge gate logits (`EVOLVE_TYPE_MUTATE_SIGMA`).
5. Children start at half differentiation (more plastic).
6. F009 light checks; on failure restore pre-cycle snapshot.

Does **not** yet: latent pool (F007), absorption (F008), explicit hybridization crossover.

## Console
- DSC: `/evolve` / `/evolve 3`
- FlyWire: refuse
