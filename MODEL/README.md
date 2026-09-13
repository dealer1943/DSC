# MODEL — active DSC under development

**This is not `MODELS/`.**  
- `MODEL/` → the **DSC runtime / checkpoint you are building** (synthetic population, evolution state, operator-facing “active model”).  
- `MODELS/` → **published biological connectomes** (FlyWire, MaleCNS, hemibrain) used for comparison.

## Layout
```
MODEL/
  README.md          # this file
  active/            # current working checkpoint (default /load target)
    manifest.json    # revision, created, schema version, notes
    # later: graph, cells, signals, RNG, evolution metadata, …
  archive/           # optional dated snapshots (create when first needed)
```

## Conventions
1. **One active tip** — `active/` is what the operator console loads by default (`/load dsc`).  
2. **Manifest required** — every save updates `active/manifest.json` (revision bumps, UTC timestamp, short note).  
3. **Handoff-friendly** — successors should restore from `active/` without chat history.  
4. **Non-essential UI** — the console monitors this folder; absence of `UI/` does not invalidate `MODEL/`.  
5. **Never store biological packs here** — those stay under `MODELS/`.

## Manifest schema (v0)
```json
{
  "schema": 0,
  "kind": "dsc_active",
  "revision": "r0-empty",
  "created_utc": "2026-09-13T00:00:00Z",
  "updated_utc": "2026-09-13T00:00:00Z",
  "note": "scaffold only — no runtime weights yet",
  "pairs_with_features": ["F001", "F002"],
  "ui_default": true
}
```
