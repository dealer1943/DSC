---
id: I001
title: FlyWire 48-node canvas breathes on ambient noise, not stim/field
status: fixed
severity: medium
area: UI / FlyWire + OpenWorm + DSC adapters
pairs_with: [F012, F018, F019]
reported: 2026-09-14
updated: 2026-09-14
---

## Layman
The curated BRAIN MAP can sit on real sensory drive, but the **list of 48 sampled neurons** used to wiggle from a fake “breathing” animation. Tracked neurons should tell the **same story** everywhere they’re shown. `/rest` means quiet; `/stim` means wake.

## Symptom (was)
- FlyWire / OpenWorm: 48-list + charts ambient-sine independent of stim.
- `/rest` left residual glow (`base × 0.18`) and charts that went blank (sparkline mapped flats to space) and looked dead forever.
- FlyWire `/load` UI froze during ~800MB feather because the canvas sample loop kept pounding the main thread.

## Fix (shipped)
1. `live_activity(..., breathe=)` gated from `status.stim` in `app._paint` (FLYWIRE / OPENWORM / DSC).
2. Adapters sync canvas from activity EMA while driven; **hard zero** activity + EMA/volt/recruit on `/rest`.
3. Sparklines: flat zero → dim `▁`; flat nonzero → mid `▄`; troughs never render as blank space.
4. DSC `sample_frame` gated on `_live_drive`; rest pushes quiet zeros; stim reseeds charts.
5. FlyWire `/load` on Textual worker thread; sampler paused during load; at rest skip heavy spike tick + BRAIN MAP rebuild.
6. OpenWorm mirrored (rest/stim/sync/charts).

## Acceptance
- [x] `/load flywire` sensory on: map + list correlated (EMA), not per-bar sine only.
- [x] `/rest` → list hard quiet; charts quiet dim line (not blackout).
- [x] `/stim` → list + charts wake; unknown regions still refuse (fly).
- [x] No second ambient neuron story in charts while stim off.
- [x] `stim: on|off` matches eye on list/map/charts (fly, worm, DSC smoke).

## Non-goals
- Not expanding canvas beyond the 48-sample demo budget.
- Not mapping every root_id to a soma in the layout pack.
- Not changing DSC grid semantics (real `pop.activity` remains source of truth there).
