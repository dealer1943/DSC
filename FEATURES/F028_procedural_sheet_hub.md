---
id: F028
title: Procedural sheet+hub substrate (anti-overfit)
status: implemented
phase: DSC core
pairs_with: [F001, F021, F022, F027]
updated: 2026-09-14
---

## Layman (state-trading intuition)
Don’t hardcode the fly’s medulla order book. Ship **one microstructure rule** that still works when the venue changes: geometry (sheets on a cylinder) + preferential attachment + light two-way quotes scaled by density. Same generator for GNG, ME_R, LO_R — only `N` and `target_edges` change. Adaptation stays in **cell state** (utility, types, absorb), not in neuropil `if` branches.

## Non-goals (overfit guards)
- No constants copied from measured FlyWire ME_R (reciprocity ≈30%, max-deg 93, clustering 0.17, …).
- No `if neuropil == "ME_R"` wiring.
- No atlas-registered coordinates — embedding is index-derived and procedural.
- Profile D may *evaluate* on ME_R; it must not *fit* the prior to ME_R.

## Technical
Family `sheet_hub_directed` (`--dsc-family sheet_hub|hybrid|sheet_pa`):
1. Embed nodes on a cylinder `(θ, z)` from contiguous sheet blocks (`L ≈ clip(√N/2, 4..16)`).
2. Grow directed edges: source ∝ `(1+out)`, target ∝ spatial kernel × `(1+in)`.
3. Kernel: `exp(-Δθ/σ_θ) * exp(-Δz/σ_z)` with `σ` from `N`/`L` only.
4. Reciprocal completion with `p_recip = clip(1/(1+mean_deg), 0.05, 0.35)` — density-scaled, not fly-fitted.
5. Match `target_edges`, then density cap.

Future (state-adaptive, still procedural): evolve `α/β/σ` as substrate genes from task utility — still one rule family, parameters read from state, not from anatomy dumps.

## Eval
```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --dsc-family sheet_hub --experiment F028_ME_R
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil GNG --dsc-family sheet_hub --experiment F028_GNG_sanity
```

## Results (N=512 hard harness, hub-aware)

| neuropil | family | fly | dsc | dsc task | fly task | note |
|----------|--------|-----|-----|----------|----------|------|
| ME_R | sheet_hub | 4 | 2 | 0.101191 | 0.101176 | task ≈ preferential; better than pure laminar |
| ME_R | preferential (prior) | 6 | 0 | 0.101178 | 0.101176 | photo-finish task, 0–6 scoreboard |
| ME_R | laminar (prior) | 3–5 | 1–3 | 0.101320 | 0.101176 | utility up, task worse |
| GNG | sheet_hub | 5 | 1 | 0.101424 | 0.101335 | **sanity:** loses preferential’s 6–0 |
| LO_R | sheet_hub | 2 | 4 | 0.101399 | 0.101243 | scoreboard DSC; task still fly |

### Anti-overfit read
Sheet-hub is a better *ME-shaped* procedural prior than pure laminar, but **not a universal champion**. Preferential remains the GNG map. That matches state-trading: one procedural rule family is fine; **which family is active should be regime/state-selected** (future), not hardwired to a neuropil name.
