---
id: F013
title: Load progress bar (operator console)
status: implemented
phase: interface
priority: P1
updated: 2026-09-13
pairs_with: [F012]
---

## Purpose
Show a **visible progress bar + stage message** whenever a substrate is loading (`/load dsc`, `/load flywire`, …) so long reads never look frozen—especially during public demos.

## Why it is fundamental (for the console)
A silent multi-second load reads as a crash. Progress makes the instrument rack honest: fraction complete, current stage, no path leaks (pack **name** only).

## Behavior
- Bar spans 0–100% with blue→purple→red fill (same signal language as F012).
- Stage text under/beside the bar (`substrate: sampling…`, `load: reading checkpoint…`).
- Hidden when idle; appears on load; clears at 100% after a short beat.
- Adapters accept an optional `progress(frac, message)` callback.

## Non-goals
- Progress for `/tick` micro-steps (too noisy)
- Network download manager (root README covers Zenodo fetch)
