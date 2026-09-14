---
id: F017
title: Offline OpenWorm (*C. elegans*) comparison substrate
status: implemented
phase: comparison
pairs_with: [F011, F012, B016]
updated: 2026-09-13
---

## Purpose
Add a **third offline biological graph** — OpenWorm / c302 White 1986 *C. elegans* connectivity — so DSC can be compared against a small real nervous system (~300 neurons) as well as FlyWire-scale fly anatomy.

## Why it belongs
FlyWire stresses scale. OpenWorm stresses **compact biology**: known cell names, chemical vs electrical edges, instantly loadable. Together with DSC they form a three-point ladder: synthetic dynamics (DSC) → small bio graph (worm) → large bio graph (fly).

## Layout
`MODELS/worm/openworm_c302/` — CSV edges + `manifest.json` (see pack README).

## Console
`/load openworm` (aliases: `worm`, `celegans`, `c302`). Static adapter — `/tick` / `/evolve` refuse.

## Source
https://openworm.org/ · https://github.com/openworm/c302
