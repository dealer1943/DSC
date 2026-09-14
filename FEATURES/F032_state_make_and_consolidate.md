# F032 — Make states + consolidate (footprint)

**Status:** implemented (opt-in assay)  
**Related:** B018 n-state curve · R006 · R007 thin-wire · F010 harness

## Purpose

Give DSC the ability to **mint discrete state-table entries from experience**, then
**consolidate duplicates** so the table stays small. Pair with **reduced edge budgets**
(`--edge-frac`) to test whether a thinner wire + small state prior still holds the
FlyWire exam-tape score.

## Non-goals

- Replacing continuous cell state (`HIDDEN`, type mixture).
- Hardcoding neuropil labels into the state alphabet.
- Claiming fly-fit; FlyWire adj is exam tape only.

## Design

1. **Make:** online fingerprint → K regimes (PC1 / quantile bins).
2. **Table:** empirical `P(s'|s)` + per-state mean target.
3. **Consolidate:** merge near-duplicate outgoing rows (same modal next + L1 ≤ ε) when K≥10.
4. **Blend:** `y_hat ← (1-mix)*y_hat + mix*table_prior` (DSC only).
5. **Thin wire:** `target_edges = edge_frac * fly_edges` on the DSC generator only.

## CLI

```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R \
  --dsc-family sheet_hub --edge-frac 0.75 --state-table-k 2 --state-table-mix 0.25
```

Defaults: `STATE_TABLE_K=0` (off).

## Acceptance

- Opt-in only; fly exam path unchanged unless K set (DSC rebuild only).
- Reports `edge_frac`, `dsc_edges`/`fly_edges`, `state_table` summary.
- Multi-seed thin-wire panel recorded under `BENCHMARKS/runs/R007_*` / `RESEARCH/R007_*`.
