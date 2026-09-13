# S005 — Latent prune, coverage absorption, crossover

**Status:** complete (2026-09-13)  
**Goal:** Evolve replacements archive into a latent pool (F007), hand coverage to survivors (F008), and optionally blend two elites (crossover).

## In scope
- F007 latent pool (max 64), persist in checkpoint, rare reactivation
- F008 absorb pruned cell params into top similar survivors
- Fancy crossover (~35% of replacements): uniform gate mix + soft weight blend
- Console lines show `xover`, `latent+`, `revive`, `pool`, `absorb`

## Out of scope
- Full B007/B008 harnesses, meta-manager (R001), `/bench`

## Try
`/load dsc` → `/tick 64` → `/evolve 3` — look for `latent+=` and `xover=` in the terminal.
