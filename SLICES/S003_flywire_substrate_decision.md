---
slice: S003
title: Decide FlyWire offline comparison; remove zebrafish path
status: done
owner: New Bot (DSC Design)
started: 2026-09-13
updated: 2026-09-13
depends_on: [S002]
produces:
  - FEATURES/F011_offline_flywire_comparison_substrate.md
  - deletion of MODELS/zebrafish/
---

## Goal
Record why DSC uses FlyWire (not zebrafish/Fish1) as the offline biological comparison substrate, and delete local zebrafish assets.

## Acceptance
F011 exists with tradeoff table; `MODELS/zebrafish` gone; HANDOFF/MODELS README aligned.
