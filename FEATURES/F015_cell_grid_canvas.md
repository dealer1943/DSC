---
id: F015
title: Full population cell grid (12×12 canvas)
status: implemented
phase: interface
priority: P1
updated: 2026-09-13
pairs_with: [F002, F003, F012]
---

## Purpose
Show **every** DSC state cell in the operator canvas — not only the top-48 activity bars — so the population feels like a whole brain, not a leaderboard.

## Layout
Under (or replacing) the dense STEM activity bars, render a **12×12 grid of equal-diameter circles**:

| Spec | Value |
|------|--------|
| Cells | 128 (indices 0…127) |
| Grid | 12×12 = 144 slots |
| Empty | **16** slots left blank (no circle) — corners or last row padding; fixed mapping documented in code |
| Circle size | **Constant** diameter for all cells (identity ≠ size) |
| Fill color | Blue→purple→red from activity / utility (same F012 scale) |
| Label | Optional tiny index on focus; default uncluttered |
| Empty slots | Dim placeholder or true void (prefer void for “not a cell”) |

### Mapping
Row-major: slot `r*12 + c` → cell `id` if `id < 128`, else empty.  
Slots 128…143 empty. Simple, stable, demo-friendly.

## Why it is fundamental (for demos + integrity)
Top-K bars hide quiet STEM cells. Emergence and later pruning only make sense if the full census is visible. Equal diameter prevents “bigger = more important” visual lies; color carries signal.

## Non-goals
- Geometric fly neuropil layout
- Variable-size bubbles
- Showing all FlyWire neurons (still sampled)

## Acceptance (when implemented)
- [x] All 128 cells visible each frame
- [x] Exactly 16 empty slots
- [x] Equal diameters; color = signal scale
- [x] Works at `/sample 8` and `/sample 16` without UI stall on N=128

## Layout note (post-impl)
Grid **left**; legacy top-activity bar list **right** (12 rows). Edge whisper stays under both.

## Implementation
- `UI/console/render.py` — `cell_grid_panel` / auto layout in `canvas_panel`
- `dsc/runtime.py` — `canvas_nodes(order="id")` returns full census
- Empty slots: true void (` `); glyph `●` constant size
