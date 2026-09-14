---
id: R004
title: ME_R microscope (fly vs DSC contributors)
status: open
updated: 2026-09-14
related: [F021, F027, F028, B017]
priority_note: User priority — ME_R first, then LO_R.
---

## Question
What **measurable contributors** differ between FlyWire-derived ME_R wiring and DSC’s procedural family (default `sheet_hub`) under a matched N/edge budget — so we can improve ME_R without neuropil hardcodes?

## Tool (retooling only)
```bash
PYTHONPATH=. python -m tools.me_r_microscope --n 512 --seed 42 --dsc-family sheet_hub
# optional dynamics slide:
PYTHONPATH=. python -m tools.me_r_microscope --n 512 --seed 42 --with-stress
```

Emits `BENCHMARKS/runs/ME_R_micro_*.json` + `.md`.

## Slides under the glass
**Topology (always):** degree mean/median/max/p95, in/out skew, reciprocity, mutual-edge rate, local clustering proxy, rich-club / hub share (top 5% out-degree edge fraction), sheet-index distance of edges (index proxy for local vs long-range).

**Dynamics (opt-in `--with-stress`):** Profile D hard harness one seed — task_error, utility, coverage, E_tick, E_edge, tick_wall — same as F021 gaps.

## Discipline
- No `if neuropil` in `dsc/`.
- Microscope may *measure* ME_R; it must not *bake* ME_R constants into generators.
- After ME_R is addressed, reuse the same tool with `--neuropil LO_R`.

## First slide (recorded) — fly better here

Artifact: `BENCHMARKS/runs/ME_R_micro_20260914T132946Z.{json,md}`

- N=512 · seed=42 · DSC family `sheet_hub` · matched 3565 edges
- **Topology:** fly peakier (degree_skew 4.78 vs 1.88, max 175 vs 91), more ultra-local (`local_index_edge_frac` 0.36 vs 0.20), higher hub_out_share (27% vs 20%), recip 0.30 vs 0.25, clustering 0.108 vs 0.088
- **Dynamics (Profile D hard):** scoreboard **fly 6 – dsc 0**; task photo-finish (dsc 0.101191 · fly 0.101176)

This is the clear “fly still wins ME_R” microscope readout that motivated R005 (regime/gather from stats, not fly constants).

Also multi-seed: **B017** ME_R `sheet_hub` (8 seeds from 1–100) — mean task gap still fly-leaning; task wins fly **5–3** (artifact `BENCHMARKS/runs/B017_20260914T130910Z.*`).

