# DSC Handoff (read first)

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
