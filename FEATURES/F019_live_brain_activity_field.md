---
id: F019
title: Live brain activity field (FlyWire BRAIN MAP propagation)
status: implemented
phase: UI / comparison
pairs_with: [F012, F011, F018]
updated: 2026-09-13
source: https://github.com/dealer1943/FlyBrains
---

## Purpose
When FlyWire is loaded in the operator console, the biology pane must show **propagating neural activity**, not a frozen region atlas or a `/focus` highlight.

Spikes (or spike-like events) land on soma positions in a 2D BRAIN MAP. Energy spreads to neighbors, decays over sample ticks, and paints region glyphs where activity is alive. A quiet brain shows only a dim silhouette; a stimulated brain lights and moves.

This is the difference between “a labeled diagram of neuropils” and “watching the connectome think.”

## Why it is fundamental
Offline biological comparison only persuades if the fly substrate feels **alive under drive**. Static labels and cosmetic sine pulses cannot show:

- that sensory drive reaches early visual / antennal territory first  
- that activity can recruit central / mushroom / descending populations  
- that silence returns the map to silhouette  

Those are the observable contracts of a connectome monitor. Without them, FlyWire in DSC is a file browser with a logo.

Design and behavior for this field follow the live monitor approach documented in [FlyBrains](https://github.com/dealer1943/FlyBrains).

## Relationship to F018
F018 shipped the biology column and a compact BRAIN MAP **geometry** (glyph legend L/R optic, V, C, S, K MB, X CX, N AL, G taste, A/D/M).

F019 **replaces static paint** on FlyWire with a live activity field:

| Mode | F018 | F019 |
|------|------|------|
| FlyWire | Atlas silhouette + optional focus dim | Energy field + region glyph paint from spikes |
| OpenWorm | Geometric wiring map + focus | Unchanged in this feature (optional later) |
| DSC | Biology hidden | Unchanged |

`/focus` remains: dim non-matching glyphs, but it must not be the only motion.

## Core model (activity field)

Keep a fixed grid (e.g. ~44×16 for the left biology pane):

- `occupancy[y,x]` — static soma density (silhouette when quiet)  
- `energy[y,x]` — decaying activity intensity  
- `hit[y,x]` — region id of the last neuron that stamped that cell  

Each sample tick:

1. `energy *= decay` (e.g. ~0.84)  
2. Clear `hit` where energy falls below a floor  
3. For each active neuron index in the tick: add energy at its projected `(x,y)`, set `hit` to that neuron’s region id, and bleed a fraction to 4-neighbors  
4. Clip energy to a max so the map stays readable  

Render:

- If `energy` high and `hit` set → paint that region’s **letter glyph** in its region color (brighter when hotter)  
- Else if `occupancy` > ε → dim silhouette shade  
- Else → empty  

Legend stays the FlyBrains-style string:  
`L/R optic  V vis  C central  S sense  K MB  X CX  N AL  G taste  A/D/M`

## Spike source (offline-first)

DSC must not require an online service. Preferred ladder (implement the thinnest that still *propagates*):

1. **Offline tick engine** on the local FlyWire pack (or a cached adjacency / rate proxy aligned to Completeness order) producing per-tick neuron indices.  
2. **Sensory drive hooks** in the console (e.g. optic-biased rates, taste/antennal seed set) so `/see`-class or simpler `/pulse` / `/stim` commands inject drive and the map responds.  
3. Optional later: deeper Brian2 / full FlyBrains runtime as an adapter behind the same `tick(indices)` interface.

The biology pane depends only on: `(indices_this_tick) → field.tick → paint`. Simulation details stay behind the FlyWire adapter.

## Operator console contract

- Mid-row: **biology (left) | canvas | signals** (already F018 layout).  
- Biology pane for FlyWire is driven every `/sample` frame from the activity field, not from a static string.  
- Status / banner may show `spikes/tick` and sim time when the engine is running.  
- Refuse claims of language understanding; this is sensorimotor-style drive into a connectome field.

### Suggested slash commands (minimal set)

| Command | Effect |
|---------|--------|
| `/stim [ms]` or `/pulse <region>` | Inject drive into a region / seed set for one or more ticks |
| `/rest` | Clear sensory drive; let energy decay to silhouette |
| `/focus <region\|off>` | Dim other glyphs (overlay on live field) |

Exact verbs can align with FlyBrains naming where it helps operators who already know that monitor.

## Non-goals (this feature)

- Porting the full SEES | BRAIN MAP | FLY three-pane Jazz chrome into DSC  
- Requiring GPU or online FlyWire auth  
- Claiming DSC synthetic cells are biological neurons  
- Replacing OpenWorm’s geometric map in the same slice  

## Acceptance

1. `/load flywire` → biology pane shows dim silhouette at rest.  
2. After stimulation (or continuous sensory drive), **glyphs appear and move** across the map over successive sample frames; energy visibly decays when drive stops.  
3. Neighbor bleed is observable (activity is not a single static pixel stamp).  
4. Region colors / letters match the legend; no absolute filesystem paths in the UI.  
5. Feature doc cites [FlyBrains](https://github.com/dealer1943/FlyBrains) as the behavioral source of truth.

## Implementation slice (later)

Suggested id: `S008_live_brain_activity_field` — field datatype + FlyWire adapter `tick` + biology paint + thin stim/rest commands.

## First principles

- **Geometry is not dynamics.** An atlas without energy is documentation.  
- **Decay + bleed** are what make propagation readable in ASCII.  
- **One interface:** anything that can emit neuron indices per tick can drive the same field.  
- **Offline first:** ship or cache what the tick needs; document obtain paths like F011.
