# DSC Handoff (read first)

## Stack win 2026-09-14 — F024/F025/F026

Best Profile D stack: `preferential_directed` + `HUB_AWARE` + hub-aware absorb + `SPARSE_GATHER`; stress defaults lag=2/noise=0.20 (`--easy-harness` to opt out).

- F024b prune-stress: **4–2 DSC** (was 5–1 fly) — `stressD_20260914T013207Z_n512_GNG_preferential`
- F025b hard default stack: **6–0 DSC** — `stressD_20260914T013209Z_n512_GNG_preferential`
- Ledger: `BENCHMARKS/runs/stress_ledger.jsonl`

---

## Stress path 2026-09-14 — F021 Profile D

- Feature: `FEATURES/F021_flywire_matched_stress.md`
- Tools: `python -m tools.flywire_subgraph`, `python -m tools.flywire_stress`
- First run: `BENCHMARKS/runs/stressD_20260914T005930Z_n128_GNG.md` — fly_adj 3 / ER 2 at N=128 GNG (margins thin; task nearly tied)
- Dev targets when fly wins: non-ER motifs (F001), F007/F008 under degree skew, F005/type emergence on hubs
- Next stress knobs: N=512, denser/skewed neuropil (e.g. ME_*), longer evolve, harder harness

---

## Adversarial resolution 2026-09-14 (benches)

Review: `RESEARCH/ADVERSARIAL_REVIEW_2026-09-14_benches.md`

Patches applied:
- **B016** `pass` false under A/B/C/E; `pass_kind=static_null_demo`; null-opponent winners `na_static_null`; proxy floor; isolate tip; scrub paths
- **B006** temp copy; post-tick re-score; (mean|elite)↑δ + typed non-decrease; fail no-op
- **B010** pass aligned to G1 (`task_error<=0.05`); temp copy
- **F020** G3 real byte cap; G4/G5 fail on `--skip-b016`; path-leak scan; assert `save_named` refreshed active
- **R001** stronger path/hostname scrub + Path-safe JSON default

Still open: **Profile D** (matched FlyWire subgraph) required before any true `efficiency_vs_flywire` pass.

---

## Slice 2026-09-14 — F020 / B016 / B006 / B010 / R001-light

Shipped runnable development + efficiency stack (local Mac, not cloud):

- **F020** `FEATURES/F020_dsc_development_run.md` + `python -m tools.dev_run` (`dev_run_v0` gates G1–G5)
- **B016** `tools/flywire_efficiency_bench` — profiles A,B,C,E → JSON+MD; honesty note: static-null asymmetry
- **B006 / B010** `tools/benches/`
- **R001 light** `dsc/meta/manager.py` → `BENCHMARKS/meta/r001_assay_log.jsonl`
- Sample pass: short `dev_run` checkpoint `dsc_dev_*`, B016 4/4 E wins vs Profile C null

Next: Profile D matched subgraph; harden B016 pass rule so C-null alone cannot overclaim; adversarial follow-ups.

---

**Project:** Dynamic State Connectome (DSC)  
**Root:** `~/Source/repos/DSC`
**Authority order:** `HANDOFF.md` → active slice in `SLICES/` → `design_doc.md` → folder docs

## Current status (2026-09-13, check-in)

| Field | Value |
|--------|--------|
| Phase | S008 live BRAIN MAP (local) |
| Last completed slice | S008 live FlyWire BRAIN MAP activity field |
| Prior completed | `S000` continuity scaffold |
| Active slice | none |
| Next | Check-in S008/F019 + prior local slices |
| Packs | FlyWire + OpenWorm (`MODELS/worm/openworm_c302`) + DSC active |
| Code | `dsc/` + evolve/differentiation; UI `/evolve` `/rollback`; MODEL/active tip |
| Blockers | None |

## What exists

- `design_doc.md` — MVP + benchmarking theory (intent source)
- `HANDOFF.md`, `SLICES/` — continuity protocol
- `BLUEPRINT/00_mvp_overview.md` — condensed MVP
- `FEATURES/` — **F001–F010** purpose stubs + README (fundamental capabilities)
- `BENCHMARKS/` — **B001–B010** feature-paired integrity stubs; **B011–B015** LLM-analog system stubs + README
- `MODELS/fly/male_cns_v1.0/` — MaleCNS v1.0 weights + NT + annotations (MD5 verified; fruitfly sources)
- `MODELS/fly/hemibrain_v1.2.1/` — Hemibrain edgelist + meta
- `FEATURES/F012_connectome_operator_console.md` — universal DSC/FlyWire operator TUI (slash cmds, signals, terminal)
- `UI/` — operator console scaffold (F012); non-essential monitor/dialog; adapters under `UI/adapters/`
- UI v0 runnable: `cd UI && .venv/bin/python -m console` — FlyWire smoke OK (`python -m console.smoke_flywire`); large packs gitignored; root README documents obtain path
- `MODEL/active/` — **active DSC under development** (not biological); distinct from `MODELS/`
- `RESEARCH/R001_connectome_meta_manager.md` — reserved self-benchmarking / own-state manager (open question)
- `RESEARCH/R002_dsc_vs_flywire_baseline.md` — DSC vs FlyWire baseline comparison table (no training)
- `BENCHMARKS/B016_flywire_efficiency_parity.md` — efficiency-vs-FlyWire bench spec (blueprint for future tool)
- `PAPERS/` — RSI survey PDF + layman cliff notes (`*_notes.md`); maps to F006/F009/R001 (verifier isolation, rollback, meta-improvement)
- `PAPERS/2609.10715v1_archpreview_techreport*` — NCP-ArchPreview cliff notes; dual-resolution (token+concept) + VQ interface lessons for F003/F007/F010/R001
- Empty / light: `ISSUES/`, `DIAGNOSTICS/` (UI + MODEL scaffolds present)

## Feature ↔ benchmark map (mechanism)

| Feature | Benchmark |
|---------|-----------|
| F001 substrate | B001 topology invariants |
| F002 state cell STEM | B002 stem modularity |
| F003 type gating | B003 gating gradient / mixture |
| F004 differentiation | B004 plasticity tracks utility |
| F005 utility | B005 multi-term non-degeneracy |
| F006 evolution loop | B006 selection signal |
| F007 prune + latent | B007 prune without forgetting |
| F008 absorption | B008 coverage conservation |
| F009 stability rollback | B009 rollback efficacy |
| F010 temporal harness | B010 task vs footprint |

## System / LLM-analog benchmarks

| ID | Focus |
|----|--------|
| B011 | Few-shot task shift |
| B012 | Multi-step temporal reasoning |
| B013 | Long-horizon dependency |
| B014 | OOD / noise robustness |
| B015 | Calibration + seed stability |

## Non-negotiable guardrails (from design_doc)

1. Do **not** hardcode state types — emergence only.
2. Start **synthetic**, sparse (<10%), **directed** substrate.
3. Utility is multi-term (task + coverage + novelty − cost).
4. Pruned states → **latent pool**, not hard delete.
5. Failed stability checks → **rollback** the evolution cycle.

## How to continue after a cutoff

1. Read this file and latest `SLICES/S*.md`.  
2. One slice only; finish and document before context dies.  
3. Update this status table before stop.  
4. Prefer files over chat for lasting decisions.
