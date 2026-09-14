# B018 — n-state curve (discrete state-table cardinality)

**Tier:** system / established-state assay  
**Related:** F010 temporal harness · F021 Profile D · drawing-board: cold vs established state  
**Status:** tooling_v0 (assay)

## Purpose

Ask whether a **discrete next-state table** gets better or worse as alphabet size grows:
**K ∈ {10, 50, 100}**.

More regime bins = finer state resolution, but thinner transition counts (sparser table).
We want the **shape** of that resolution/sparsity tradeoff on ME_R exam tape
(DSC `sheet_hub` vs FlyWire matched adj), not a fly-fit.

## What “state table” means here

Not TYPE_NAMES count and not N_nodes. After warm/evolve, each tick emits a compact
fingerprint `(y_hat, err, utility, activity, stem_frac, diff_mean, type_mixture_mean)`.
Train (70%) fits z-score → PC1 → equal-mass quantile bins to K labels. An empirical
Laplace-smoothed `P(s'|s)` is scored on the held-out 30% (`next_state_hit`,
`mean_surprisal`). Same trajectory is rebinned at each K (one warm cost).

## Protocol

```bash
python3 -m tools.n_state_curve \
  --neuropil ME_R --n 512 --dsc-family sheet_hub \
  --ks 10,50,100 --seeds 17,22,46 \
  --warm 64 --evolve 2 --collect 800
```

- Matched N/edges via Profile D subgraph extract.
- ME_R is **exam tape only** (no neuropil ifs in generators).
- Metrics per (seed, arm, K): `next_state_hit`, `mean_surprisal`, `occupied_frac`, `task_error`.

## Consolidation (F032)

After minting K states, merge source rows whose outgoing distributions are
near-duplicates (same modal next + L1 ≤ 0.25). Report `k_eff`, compression,
and next-state hit before/after — footprint without throwing away the table.

## Non-goals

- Promoting K into runtime defaults.
- Fitting bins to FlyWire labels.
- Replacing Profile D task scoreboard (this is a parallel lens on history→next-state).

## Artifacts

`BENCHMARKS/runs/B018_*_{n}_{neuropil}.json` (+ `.md` summary).

## Fine sweep (DSC-only)

K=2..10 on DSC; FlyWire not a designed state alphabet. See R006 + `BENCHMARKS/runs/B018_fine_*_dsc.json`.
