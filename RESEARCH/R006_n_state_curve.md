# R006 — n-state curve + consolidation

**Status:** open assay (B018 tooling_v0)  
**Parent context:** Profile D is cold. Missing piece = **make states**, then
**consolidate** redundant rows (without consolidation, footprint dies).

## Hypothesis

1. Alphabet size K has a usable band before sparsity hurts next-state prediction.
2. Consolidating near-duplicate outgoing rows (`k_eff << K`) preserves hit rate
   while cutting footprint — the lever that matters for established-state agents.

## Method

B018: ME_R N=512 sheet_hub vs fly_adj; one trajectory / seed / arm; rebin K=10/50/100;
PC1 quantile states; Laplace table; consolidate when same modal next + L1≤0.25.

## Results (B018_20260914T154812Z)

ME_R N=512 sheet_hub vs fly_adj · seeds 17,22,46 · warm64 evolve2 collect800

| arm | K | version | hit | surprisal | k_eff | compression | task_error |
|-----|---:|---------|-----:|----------:|------:|------------:|-----------:|
| dsc | 10 | raw | 0.582 | 1.138 | 10.0 | 1.00 | 0.01653 |
| dsc | 10 | consolidated | 0.582 | 1.138 | 10.0 | 1.00 | 0.01653 |
| dsc | 50 | raw | 0.149 | 3.401 | 50.0 | 1.00 | 0.01653 |
| dsc | 50 | consolidated | 0.230 | 2.992 | 41.0 | 0.82 | 0.01653 |
| dsc | 100 | raw | 0.053 | 4.434 | 100.0 | 1.00 | 0.01653 |
| dsc | 100 | consolidated | 0.232 | 3.705 | 68.7 | 0.69 | 0.01653 |
| fly_adj | 10 | raw | 0.536 | 1.311 | 10.0 | 1.00 | 0.01652 |
| fly_adj | 10 | consolidated | 0.536 | 1.311 | 10.0 | 1.00 | 0.01652 |
| fly_adj | 50 | raw | 0.144 | 3.501 | 50.0 | 1.00 | 0.01652 |
| fly_adj | 50 | consolidated | 0.183 | 3.286 | 44.7 | 0.89 | 0.01652 |
| fly_adj | 100 | raw | 0.066 | 4.457 | 100.0 | 1.00 | 0.01652 |
| fly_adj | 100 | consolidated | 0.170 | 3.894 | 71.3 | 0.71 | 0.01652 |

Shape note: raw hit falls as K grows (sparser table); consolidation lifts hit and cuts k_eff, especially at K=100.

Artifact: `BENCHMARKS/runs/B018_20260914T154812Z_n512_ME_R.json`

## Fine sweep K=2..10 (DSC-only)

Artifact: `BENCHMARKS/runs/B018_fine_20260914T164922Z_n512_ME_R_dsc.json`

FlyWire is exam tape only — state alphabet design applies to DSC.

| K | hit (raw) | surprisal |
|---:|----------:|----------:|
| 2 | 0.932 | 0.25 |
| 3 | 0.895 | 0.37 |
| 4 | 0.828 | 0.55 |
| 5 | 0.784 | 0.66 |
| 6 | 0.746 | 0.75 |
| 7 | 0.736 | 0.80 |
| 8 | 0.671 | 0.95 |
| 9 | 0.662 | 0.99 |
| 10 | 0.582 | 1.14 |

Monotone: finer K → lower next-state hit (sparser counts). Consolidation is a no-op below ~10 on this panel. Caveat: K=2 is an easy prediction problem (coarse bins); hit alone is not “more useful for the agent.”

## K=2 × 30 random seeds (DSC-only)

Artifact: `B018_k2_n30_20260914T165426Z_n512_ME_R_dsc.json`

seeds=[1, 14, 15, 21, 25, 27, 29, 31, 34, 45, 47, 49, 51, 57, 58, 61, 64, 66, 67, 68, 69, 72, 75, 78, 81, 87, 89, 94, 95, 98]

- next_state_hit: **0.938** ± 0.033 (min 0.879 · max 0.992)
- surprisal: 0.230 ± 0.089
- task_error: 0.01598 ± 0.00374

## K=2 × 30 head-to-head (DSC vs fly exam tape)

Artifact: `B018_k2_n30_h2h_20260914T181007Z_n512_ME_R.json` · draw_seed=271828

- next-state hit: DSC **0.926** ± 0.026 vs fly **0.924** ± 0.040
- paired Δ hit (DSC−fly): +0.0021 · scoreboard 16/14/0
- task_error: DSC 0.01759 vs fly 0.01759 · scoreboard 18/12/0

