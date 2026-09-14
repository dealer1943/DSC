---
id: F018
title: Biology identity pane (fly image · worm ASCII map)
status: implemented
phase: UI / comparison
pairs_with: [F012, F011, F017]
updated: 2026-09-13
---

## Purpose
When the operator console is showing a **biological** substrate (FlyWire / OpenWorm), put a **top-middle identity pane** so a human (or a recording for Twitter) instantly sees *which animal* they are looking at — not only abstract nodes and edges.

DSC mode keeps the existing synthetic canvas (no animal portrait).

## Why it is fundamental
Comparison substrates are easy to confuse once the TUI is hypnotic. A fly pack and a worm pack can both look like “glowing dots.” An identity pane anchors the session in biology: **this is a fly brain** / **this is a nematode nervous system**. That is part of trust and demo clarity, not decoration.

## Layout (operator console)

Today’s main row is roughly:

```
│ canvas (left, ~3fr) │ signals + summary (right, ~2fr) │
```

F018 inserts a **biology pane in the top-middle** of the main row when mode ∈ `{FLYWIRE, OPENWORM}`:

```
│ canvas │ BIOLOGY PANE │ signals │
│        │  (top mid)   │ summary │
```

Suggested Textual structure (implementation later):

- Keep `#canvas` on the left (grid / activity).
- Add `#biology` Static (or RichLog/Image) docked or laid out between canvas and the side column, **top** of the main band (height ~8–14 rows or a fixed fraction).
- `#signals` / `#summary` stay on the right.
- When mode is `DSC` or `EMPTY`, `#biology` is hidden (`display: none`) so the synthetic MVP keeps max canvas space.

Exact CSS proportions are free as long as the pane is visibly **top-middle** and does not bury slash commands.

## Mode → content

| Mode | Pane content | Notes |
|------|----------------|-------|
| `FLYWIRE` | Compact **BRAIN MAP** mid-pane (iLandsAI `flywire_layout` atlas: L/R/V/C/S/K/X/N/G/A/D/M); sits between neuron list and signal graphs; `/focus` dims non-hits | Same row as canvas + signals — not a separate band. |
| `OPENWORM` | **Geometric wiring map** (amphids → nerve ring → command interneurons → dorsal/ventral cords → tail); `/focus` lights named cells | Not an earthworm plate. See accuracy note below. |
| `DSC` / `EMPTY` | Hidden | Synthetic connectome — no animal portrait. |

Optional later: pulse/highlight the ASCII region or fly silhouette when `/focus` hits a named cell (e.g. `AVAL`).

## Fly image asset (implementation contract)

1. Source of truth: the same visual used in the fruitfly demo (candidate on disk: `~/Source/repos/flyworld/test-results/flyworld.png` — verify with the operator before freezing).
2. Copy into DSC as `UI/assets/biology/fly.png` (or `.webp`) so the console is self-contained after clone.
3. Document obtain path in `UI/assets/biology/README.md` if the binary is gitignored for size; otherwise track a modest compressed still.
4. Textual rendering: prefer a terminal-friendly preview (half-block / sixel / Kitty image protocol if available) **or** a short caption + “open external” if the TUI cannot show pixels — but the **intent** is that recordings show the fly brain in-frame. Pick one approach in the implementation slice and stick to it.

## Worm ASCII (C. elegans — not earthworm)

### Accuracy note (important)
The reference image supplied in chat is **Encyclopædia Britannica: “Nervous system of the annelid (earthworm)”** — cerebral ganglia, circumesophageal connectives, ventral nerve cord with segmental nerves around a gut. That anatomy is **annelid**, not nematode.

OpenWorm / F017 loads ***C. elegans*** (~300 neurons). Nematodes do **not** have a segmental earthworm-style ladder; they have:

- a **nerve ring** (circumpharyngeal) around the pharynx  
- **dorsal / ventral / lateral nerve cords**  
- named neurons (e.g. `AVAL`/`AVAR`, `AVBL`/`AVBR`, sensory amphids, motor VBs/DBs, …)

F018’s worm pane must use a **C. elegans schematic**, not a copy of the earthworm Britannica plate. The earthworm figure may live in `UI/assets/biology/reference_earthworm_annelid.png` as *contrast / do-not-use-for-OpenWorm* documentation only.

### Suggested ASCII v0 (placeholder — refine in build slice)

Keep it compact (~12–16 lines) so it fits the top-middle pane:

```text
  C. elegans  ·  OpenWorm / c302
         ┌─ nerve ring ─┐
    amphid ─( ○○○○○○○ )─ amphid
              │ pharynx │
    ┌─────────┴────┴─────────┐
    │  ventral cord          │
    │  ·· AVAL AVAR ··       │
    │  ·· AVBL AVBR ··       │
    │  motor pool (VB/DB…)   │
    └────────────────────────┘
  /focus <name> highlights a label
```

When `/focus AVAL` (etc.) is active, mark that token (e.g. bold / signal-color) in the ASCII.

Chemical vs electrical edge mix from the pack can stay in `#summary`; the biology pane is **identity + map**, not a second stats column.

## DSC

No biology pane. Optionally a one-line caption in summary: `substrate: synthetic DSC` — already covered by mode banner.

## Non-goals (this feature)

- Full 3D worm browser / Geppetto embed  
- Replacing the 12×12 DSC grid  
- Claiming the earthworm Britannica diagram is OpenWorm-accurate  
- Online fetches of images at runtime (offline-first: ship or document local assets)

## Acceptance (when built)

1. `/load flywire` → top-middle shows fly brain identity (image or agreed TUI stand-in) with pack name only (no path leak).  
2. `/load openworm` → top-middle shows *C. elegans* ASCII map; `/focus AVAL` visibly marks `AVAL`.  
3. `/load dsc` → biology pane hidden; layout does not leave a blank hole.  
4. Feature doc + `UI/assets/biology/README.md` explain fly asset provenance and the earthworm-vs-nematode distinction.

## Implementation slice (later)

Suggested id: `S007_biology_identity_pane` — assets + layout + focus highlight; no new evolution logic.

## Live dynamics
FlyWire and OpenWorm biology panes use the F019 activity field (propagating spikes). See `FEATURES/F019_live_brain_activity_field.md`.

## S007 note
Build uses **ASCII maps for both fly and worm** in the TUI (reliable in Textual recordings). Fly map is the dense MaleCNS letter silhouette (not sparse neuropil tiles). Raster fly still remains optional later under `UI/assets/biology/`.


## Worm map (2026-09-14)
OpenWorm mid-pane twin of FlyWire `BRAIN MAP`: glyph atlas `WORM_BODY_MAP` in `UI/console/biology.py` (S/N/P/C/V/D/T/`.`) shaped as an elongated S-curve nervous system — dense nerve ring at anterior, longitudinal cord glyphs, tapering tail — not a labeled schematic of individual neuron names.

## Live atlas paint (2026-09-14)
Curated `BRAIN MAP` / `WORM MAP` glyph atlases are painted from **live region EMA** (`glyph_levels`) driven by the activity engines (FlyWire kNN recruit · OpenWorm White-edge synapses). Default load enables sensory drive (fly: optic+AL+sense; worm: amphid+ring). `/rest` clears drive; `/stim` / `/pulse` retarget.
