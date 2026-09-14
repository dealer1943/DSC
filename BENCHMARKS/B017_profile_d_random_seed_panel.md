---
id: B017
title: Profile D random-seed panel (honest multi-seed standing)
status: implemented
tier: system / comparison
measures: [F021, F022, F023, B016]
tool: `PYTHONPATH=. python -m tools.b017_random_seed_panel`
updated: 2026-09-14
---

## Purpose
**Retooling / assay** — not a DSC core feature. Reveal whether Profile D scoreboard wins survive **random seeds drawn from 1–100** (no hand-picked 42–48 list).

Single-seed photo-finishes (bilayer, talk board, nearest-exact) lied about stability. B017 is the truth panel.

## Protocol
1. Draw `n_seeds` distinct integers uniformly from `[seed_lo, seed_hi]` (default 1–100) using a recorded `draw_seed` (or OS entropy if omitted).
2. For each drawn seed × each panel cell (neuropil + dsc-family), run existing `tools.flywire_stress.run_stress` Profile D hard harness (lag=2, noise=0.20) — **no changes to `dsc/`**.
3. Aggregate: mean±std task_error (DSC and fly), mean task gap (dsc−fly), scoreboard win totals, per-seed rows.
4. Write `BENCHMARKS/runs/B017_*.json` + `.md`.

## Default panel cells (best-known family per neuropil)
| neuropil | dsc-family |
|----------|------------|
| GNG | preferential |
| AVLP_R | preferential |
| ME_R | sheet_hub |
| LO_R | laminar |

Override with `--cells GNG:preferential,ME_R:sheet_hub`.

## Pass / claim language
- **Informational** by default (exit 0 even if fly-led) — this is a reveal tool.
- Optional `--require-gng-lead`: fail if GNG mean task gap (dsc−fly) ≥ 0 under the draw.
- Safe claim: only after B017 — never from one seed.

## Non-goals
- No new message-passing / substrate code in `dsc/`
- No neuropil hardcodes inside the runtime
- Not a substitute for B011–B015 LLM-analog benches
