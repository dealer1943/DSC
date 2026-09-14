---
id: F016
title: Built-in operator tutorial (commands + training loop)
status: implemented
phase: interface / docs
priority: P1
updated: 2026-09-14
pairs_with: [F012, F013, F014, F006, F011]
---

## Purpose
A **first-run / on-demand tutorial** inside the operator console that teaches slash commands and the intended “train the brain” loop — so inspiration converts to correct use without reading the whole repo.

## Entry points
- `/tutorial` — start or show current step
- `/tutorial next` — advance after you ran the suggested command (or skip ahead)
- `/tutorial skip` — same as next
- `/tutorial abort` — exit tutorial mode
- `/help` lists `tutorial`

## Beats (v1)
1. Welcome + mode banner (`DSC` vs `FLYWIRE` vs `OPENWORM`)
2. `/load dsc` — progress bar (F013); pack name only (no filesystem paths); advance only on **successful** load
3. `/tick 8` — watch `err` / activity; warm ticks differ from full evolution training
4. `/sample 16` — color language blue→purple→red
5. `/save` — keep the session (F014)
6. `/stim` — live display wake (I001); `/rest` optional
7. `/evolve 1` — training loop (DSC mode); before optional FlyWire
8. Optional FlyWire (~20–30s load) — hint only; manual `/tutorial next` (avoids racing background load)
9. Done

## Implementation
- `UI/console/tutorial.py` — step copy + match helpers
- `UI/console/app.py` — `/tutorial` dispatch + auto-advance when the operator runs the hinted verb
- `UI/console/slash.py` — palette entry

## Non-goals
- Replacing FEATURES/BENCHMARKS docs
- Auto-posting, voiceover, or LLM coach in v1
- Auto-loading the ~800MB FlyWire feather (hint only)

## Acceptance
- [x] Runnable from cold console via `/tutorial`
- [x] Never shows filesystem paths in tutorial copy
- [x] Clear that warm ticks ≠ full evolution training
