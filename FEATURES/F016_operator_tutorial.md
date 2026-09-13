---
id: F016
title: Built-in operator tutorial (commands + training loop)
status: stub
phase: interface / docs
priority: P2
updated: 2026-09-13
pairs_with: [F012, F014]
---

## Purpose
A **first-run / on-demand tutorial** inside the operator console that teaches slash commands and the intended “train the brain” loop — so inspiration converts to correct use without reading the whole repo.

## Scope (doc only for now — not implementing)
Suggested beats:
1. Welcome + mode banner (`DSC` vs `FLYWIRE`)
2. `/load dsc` → progress bar (F013) → see pack name only
3. `/tick 32` twice — watch `err` move; note non-monotonicity is normal
4. `/sample 16` — color language blue→purple→red
5. `/save` — keep the session (F014)
6. `/load flywire` + `/focus AL` — comparison substrate; DSC-only cmds refuse
7. Where evolution fits later (`/evolve` when F006 lands) — no fake training claims

## Entry points (future)
- `/tutorial` or `/help tutorial`
- Optional first-launch flag in `MODEL/active` or UI settings

## Non-goals
- Replacing FEATURES/BENCHMARKS docs
- Auto-posting, voiceover, or LLM coach in v1

## Acceptance (when implemented)
- [ ] Runnable from cold console in &lt; 5 minutes
- [ ] Never shows filesystem paths
- [ ] Clear that warm ticks ≠ full evolution training
