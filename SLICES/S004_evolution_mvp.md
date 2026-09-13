# S004 — Evolution MVP (F004 light + F006 + F009 light)

**Status:** complete (2026-09-13)  
**Goal:** Closed evaluate→select→clone→mutate loop with differentiation pressure and auto-rollback, operable from the console.

## In scope
- **F004 light** — per-cell `differentiation ∈ [0,1]` EMA’d from utility stability (STEM label &lt; 0.35).
- **F006** — `/evolve [n]`: top-K keep, replace bottom fraction with mutated clones, rare type-logit nudge.
- **F009 light** — pre-cycle snapshot; rollback on NaN/Inf, footprint collapse, or utility cliff; `/rollback` restores last-good.
- Console wiring (DSC only); FlyWire refuses.

## Out of scope
- Full F007 latent prune pool, F008 coverage absorption, `/bench` runner, hybridization beyond clone+mutate.

## Defaults
See `dsc/defaults.py`: `EVOLVE_TOP_K=16`, `EVOLVE_REPLACE_FRAC=0.25`, `EVOLVE_MUTATE_SIGMA=0.05`, `EVOLVE_TYPE_MUTATE_RATE=0.05`, rollback cliff/footprint thresholds.

## Acceptance
1. `/load dsc` → `/tick 32` → `/evolve 3` prints cycle lines; state stays finite.
2. Forced instability path auto-rollbacks (unit smoke).
3. `/rollback` restores last-good after a successful evolve.
4. FlyWire `/evolve` / `/rollback` refuse.
5. `/save` round-trips `differentiation`.
