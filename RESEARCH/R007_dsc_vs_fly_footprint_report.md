# R007 — DSC vs FlyWire: procedural connectome, small state, thinner wire

**Status:** complete  
**Audience:** public technical note (Twitter-shareable)  
**Date:** 2026-09-14  
**Repo:** https://github.com/dealer1943/DSC  
**Panel artifact:** `R007_thin_wire_k2_n30_20260914T191352Z.json`

> This document uses only connectome / DSC terms. Methods are described as
> procedural graph generation, soft-typed cells, and discrete state tables.
> Neuropil labels select exam tapes — they are not hardcoded into generators.

---

## Executive summary

On the FlyWire **ME_R** exam tape (N=512, Profile D), a **procedural** DSC
`sheet_hub` graph with a **K=2 discrete state prior** and **half the wires**
of the biological adjacency:

- **beats fly on task** across 30 random seeds (**25–5** seed scoreboard),
- runs at **~parity or slightly faster** wall-clock (~0.98×),
- uses **0.50× edges** (wire footprint cut in half).

Matched-edge DSC without the state table was a **coin-flip** (15–15). Adding
K=2 at matched edges already flipped the scoreboard to **22–8**. Thinning wires
to 75% or 50% **held** the win (**25–5** both).

That is the innovation: **fly-class (better) exam scores from a regenerable,
thinner procedural connectome + small state table** — not a copy of FlyWire
constants.

---

## What DSC is

**Dynamic State Connectome (DSC)** is an offline-capable matrix connectome stack:

1. **Substrate** — sparse directed graph from procedural families (`sheet_hub`, preferential, modular, …), scaled by N and target edge count only.
2. **Cells** — soft mixture-of-types state cells (STEM → differentiated), hidden state, utility, evolution/prune/absorb.
3. **Harness** — lag-1 scalar prediction task with warm / evolve / tick protocol.
4. **State table (F032, opt-in)** — mint K discrete regimes from a compact fingerprint; maintain next-state counts + per-state mean target; blend a table prior into the readout; consolidate near-duplicate rows when K is large.

Docs are sliced for handoff (`FEATURES/`, `RESEARCH/`, `BENCHMARKS/`).

## What FlyWire is here

[FlyWire](https://flywire.ai/) provides an offline whole-brain synapse pack. For **Profile D** we extract a matched-N subgraph (here ME_R, N=512). The biological adjacency is the **exam tape**: same software dynamics run on fly wiring vs DSC wiring. FlyWire is **not** the blueprint for DSC constants.

---

## Benchmarks used

| ID | What it measures |
|----|------------------|
| **Profile D** (`tools/flywire_stress`) | Task error, wall-clock, metric scoreboard; matched or intentionally thinner DSC edges |
| **B018 / R006** | Discrete next-state table curve (K=2…100); make + consolidate |
| **R007 panel** (this report) | 30-seed ME_R: matched ± K=2; 0.75× / 0.50× edges + K=2 vs fly |
| **F031** (prior) | Hub-formation governor (topology honesty) |
| **B016** | Efficiency language vs static anatomy — still demo, not a trophy |

### R007 panel protocol

- N=512, neuropil=`ME_R`, family=`sheet_hub`
- warm=64, evolve=2, ticks=256
- 30 seeds from 1…100 (`draw_seed=161803`): `[3, 7, 8, 13, 14, 16, 18, 19, 22, 24, 25, 28, 30, 37, 40, 41, 45, 48, 52, 54, 58, 59, 63, 64, 65, 85, 89, 91, 93, 95]`
- Fly adj always full matched edges; only DSC is thinned / state-augmented

| arm | edge_frac | state-table K |
|-----|----------:|--------------:|
| matched_k0 | 1.00 | 0 (off) |
| matched_k2 | 1.00 | 2 |
| thin75_k2 | 0.75 | 2 |
| thin50_k2 | 0.50 | 2 |

---

## Results — Profile D task vs fly (30 seeds)

| arm | wire vs fly | DSC task↓ | fly task↓ | mean gap (DSC−fly) | seed wins D/F | wall DSC/fly |
|-----|------------:|----------:|----------:|-------------------:|--------------:|-------------:|
| matched, no state | 1.00× | 0.01659 | 0.01659 | +4.359e-07 | 15/15 | 1.009 |
| matched + K=2 | 1.00× | 0.01552 | 0.01659 | -1.065e-03 | 22/8 | 1.086 |
| 75% wires + K=2 | 0.75× | 0.01550 | 0.01659 | -1.087e-03 | 25/5 | 1.019 |
| **50% wires + K=2** | 0.50× | 0.01549 | 0.01659 | -1.098e-03 | 25/5 | 0.981 |

Gap < 0 means DSC better on mean task_error.

**Read:**

- **Matched, no state:** photo-finish / coin-flip (15–15).
- **+ K=2 state prior:** clear seed lead (22–8); small mean-gap win.
- **75% or 50% wires + K=2:** lead holds on seeds (25–5); at 50% wires wall-clock ratio **0.981** (DSC slightly faster on this panel).

### Wire footprint

| arm | mean DSC edges | mean fly edges | ratio |
|-----|---------------:|---------------:|------:|
| matched_k0 | 3599 | 3599 | 1.00 |
| thin75_k2 | 2699 | 3599 | 0.75 |
| thin50_k2 | 1800 | 3599 | 0.50 |

---

## Results — discrete state tables (B018, prior)

Separate assay: mint K states from run history; score next-state prediction.

- **K=2 × 30 seeds (DSC-only):** next-state hit **~0.938 ± 0.033**
- **K=2 × 30 head-to-head:** DSC **0.926** vs fly **0.924** (16–14) — coin-flip on that lens
- **K=2…10:** coarser K → higher hit (monotone)
- **K=10/50/100 + consolidate:** raw hit falls with K; consolidate cuts footprint and lifts hit mainly above ~10

State tables are a **DSC capability**. Fly trajectories can be scored as exam tape; FlyWire itself has no designed state alphabet.

---

## How DSC scores against the fly connectome (claim language)

| Claim | Status |
|-------|--------|
| Procedural DSC ≈ fly on ME_R task at matched edges | **Supported** (coin-flip without K; win with K=2) |
| Half-wire DSC + K=2 beats fly on ME_R task (30 seeds) | **Supported** (25–5, mean gap < 0, wall ≤ 1) |
| DSC faster than fly always | **Not claimed** — ~parity; 50% wire arm slightly faster here |
| DSC beats fly on all neuropils | **Not claimed** — re-run LO/AVLP/GNG before global claims |
| Efficiency trophy vs static FlyWire anatomy (B016) | **Not claimed** — still demo |

**Safe public sentence:**

> On FlyWire ME_R exam tape (N=512, 30 seeds), DSC’s procedural sheet+hub graph
> with a K=2 state prior and 50% of the biological edge budget beat the fly
> adjacency on task (25–5) at ~parity wall-clock — without copying FlyWire wiring
> constants.

---

## Limits

- Profile D is still a **short** warm/evolve protocol (not a long established-state agent).
- ME_R-focused panel; re-run other neuropils before global claims.
- K=2 is a coarse prior blended into readout — not a full symbolic controller.
- Generators stay procedural; no neuropil hardcodes.

---

## Repro

```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R \
  --dsc-family sheet_hub --edge-frac 0.5 --state-table-k 2 --state-table-mix 0.25
```

Panel: `BENCHMARKS/runs/R007_thin_wire_k2_n30_20260914T191352Z.json`

Related: `FEATURES/F032_state_make_and_consolidate.md`, `RESEARCH/R006_n_state_curve.md`, `BENCHMARKS/B018_n_state_curve.md`.

---

## Changelog

- 2026-09-14: F032 opt-in state table + `--edge-frac`; R007 30-seed thin-wire panel; this report.
