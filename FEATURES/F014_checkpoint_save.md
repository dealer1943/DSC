---
id: F014
title: Checkpoint save (`/save`)
status: implemented
phase: interface / persistence
priority: P1
updated: 2026-09-13
pairs_with: [F012, F013]
related: [F001, F002, F003, F005, F010]
---

## Purpose
Persist the **current DSC runtime** (substrate, cells, harness, utilities) from the operator console without a full `python -m dsc` rebuild, so tick-session learning is not lost.

## Commands
| Input | Behavior |
|-------|----------|
| `/save` | Write `MODEL/saves/dsc_<YYYYMMDD>_<HHMMSS>.model` (UTC clock, special chars already absent) |
| `/save <name>` | Write `MODEL/saves/<sanitized>.model` — if the user omits `.model`, it is appended |

There is **no separate `/saveas`**: an optional filename after `/save` *is* save-as.

## Sanitization
Allowed in the basename: `A–Z a–z 0–9 . _ -`.  
All other characters → `_`. Empty after sanitize → fall back to the default timestamp name.  
Trailing `.model` enforced once (no `.model.model`).

## Artifact format
A **`.model` file** is a zip bundle containing:
- `checkpoint.npz`
- `harness.json`
- `manifest.json` (includes `display_name` = basename only — **no filesystem paths**)

Also refreshes `MODEL/active/` to the same bytes so `/load dsc` picks up the tip.

## Why it is fundamental
Without session save, every exciting `/tick` run dies at rebuild or process exit. Persistence is part of integrity (rollback / handoff), not a convenience.

## Non-goals
- FlyWire `/save` (read-only pack)
- Cloud upload
- Autosave every tick (too noisy; can be a later option)

## Acceptance
- [x] Feature documented
- [x] `/save` and `/save <name>` in slash palette (DSC-only)
- [x] Default timestamped `.model` under `MODEL/saves/`
- [x] Special-character scrub
- [x] Updates `MODEL/active` tip
