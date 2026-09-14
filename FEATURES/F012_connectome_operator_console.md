---
id: F012
title: Connectome operator console (universal ASCII / TUI)
status: implemented
phase: interface
priority: P1
updated: 2026-09-14
pairs_with: [B001, B005, B009, B010, B015]
related: [F001, F002, F005, F006, F009, F011, R001]
audience: operator + public demo (e.g. Twitter clips)
---

## Purpose
Give a **single, substrate-agnostic operator console** that can load either:

1. a **DSC runtime** (synthetic / evolved state-cell population), or  
2. a **biological connectome pack** (starting with offline FlyWire v783 under `MODELS/fly/flywire_v783/`, also MaleCNS / hemibrain),

and present the same interaction surface: **see structure + signal**, **watch a scrolling diagnostic narrative**, and **drive the system with slash commands**.

The console is an *instrument rack*, not a second brain. It reads and commands; it does not become the evolution loop.

## Why it is fundamental
A connectome you cannot see is hard to trust and impossible to demo. Public sharing needs a legible live view of *states*, not only loss curves. Internally, the same view is how operators notice utility collapse, prune regressions, and rollback events before they become silent failures. Making the UI **universal** forces a clean adapter boundary: DSC dynamics and FlyWire graphs share a **view model** (nodes, edges, signals, events) so neither path gets a one-off snowflake UI.

## Design principles
1. **One console, many substrates** — load path chooses an adapter; panels stay the same.  
2. **Honest mode banner** — always show `DSC` vs `FLYWIRE` vs `MALECNS` / etc., plus data revision / checkpoint.  
3. **Read path first** — visualization and diagnostics work on static graphs before live evolution is wired.  
4. **Commands are verbs on the view model** — `/load`, `/signal`, `/bench` mean the same shape on every substrate; adapters implement what they can and refuse clearly what they cannot.  
5. **Demo-grade, not toy** — layout should read well in a screen recording (high-contrast panels, stable regions, no flashing chaos).  
6. **Assay ≠ act** — console can *request* benches / rollbacks; reserved meta-manager / evolution (R001, F006, F009) still own integrity rules.

## Layout (target)
```
┌─ MODE · SUBSTRATE · TICK / t ──────────────────────────────┐
│  Graph / population canvas (ASCII or dense braille/block)  │
│  (DSC: cells+types · Fly: neurons/neuropil focus)          │
├────────────────────────────┬───────────────────────────────┤
│  Signal charts             │  Coverage / footprint /       │
│  (sparklines / bar strips) │  type-mix / degree summary    │
├────────────────────────────┴───────────────────────────────┤
│  State / diagnostic terminal (scrollback)                  │
│  …                                                         │
├─ /command palette (appears when input starts with /) ──────┤
│  /load  /focus  /signal  /tick  /bench  /rollback  …       │
├────────────────────────────────────────────────────────────┤
│  > /█                                                      │
└────────────────────────────────────────────────────────────┘
```

### Panel notes
- **Canvas** — overview of active structure. DSC: STEM vs differentiated types, active vs latent. FlyWire: degree-ranked or neuropil-filtered subgraph (full ~10.6 GB never drawn raw).  
- **Signal charts** — time-aligned strips: utility terms, sparsity, active footprint, novelty, error/task score; on FlyWire mode, analogous graph stats (degree entropy, component count, selected neuropil activity proxy if available).  
- **Terminal** — append-only narrative of state transitions and diagnostic events (“cell 412 STEM→sensor”, “B007 prune retention ok”, “FlyWire: focused AL, n=1200”).  
- **Slash bar** — text input at bottom. On first `/`, a **palette strip appears immediately above the input** listing all commands (filter-as-you-type). Enter runs; Esc dismisses palette.

## Universal load model
```
Console
  └─ SubstrateAdapter
        ├─ DscRuntimeAdapter      # checkpoints / live sim
        ├─ FlyWirePackAdapter     # MODELS/fly/flywire_v783
        ├─ MaleCnsAdapter         # MODELS/fly/male_cns_v1.0
        └─ HemibrainAdapter       # MODELS/fly/hemibrain_v1.2.1
```

Shared view-model fields (minimum):
- `nodes[]` — id, label, kind/type, activity, utility (nullable on bio-only loads)  
- `edges[]` — src, dst, weight, sign/NT if known  
- `signals{}` — named float series for charts  
- `events[]` — timestamped terminal lines  
- `capabilities{}` — which slash commands this adapter supports

`/load dsc <path|checkpoint>` and `/load flywire [pack_dir]` (and aliases) swap adapters without restarting the console process when possible.

## Slash command surface (v0 proposal)
| Command | Intent | DSC | FlyWire |
|---------|--------|-----|---------|
| `/help` | list commands | ✓ | ✓ |
| `/load <adapter> …` | swap substrate | ✓ | ✓ |
| `/status` | mode, n, e, tick, footprint | ✓ | ✓ |
| `/focus <id|neuropil|type>` | canvas focus | ✓ | ✓ |
| `/signal <name>` | pin chart series | ✓ | ✓ (graph stats) |
| `/tick [n]` | advance DSC n steps | ✓ | refuse / no-op |
| `/evolve [n]` | evolution cycles (F006+F009) | ✓ | refuse |
| `/bench <id>` | run named benchmark | ✓ | topology-only subset |
| `/rollback` | restore pre-/evolve snapshot (F009) | ✓ | refuse |
| `/export <png|log>` | capture for sharing | ✓ | ✓ |
| `/clear` | clear terminal | ✓ | ✓ |

Palette behavior: typing `/` opens the list; further characters fuzzy-filter; Tab completes; unknown commands print a one-line refusal in the terminal (never crash).

## Public / Twitter demo constraints
- Stable 80–120 column layout (or fixed window) so recordings don’t reflow mid-clip.  
- `/export` or a hotkey dumps a frame + last N terminal lines.  
- Default FlyWire view is a **sampled / focused** subgraph with clear “showing k of N” caption — never pretend the whole brain is on screen.  
- DSC default view emphasizes **type mix + signal strips** (the story), not every edge.


## Shipped
Operator console is live (`UI/console`): Textual TUI, adapters for DSC / FlyWire / OpenWorm, slash palette, live sample, stim/rest, progress bar, BRAIN MAP. Status was stale `stub`.
## Non-goals (this feature)
- Full GUI IDE / web dashboard (ASCII/TUI first; rich GUI later if needed)  
- Editing FlyWire ground truth  
- Replacing HANDOFF / BENCHMARKS docs  
- Auto-posting to Twitter

## Acceptance (doc → later build)
- [x] Feature stub reviewed (this file)  
- [x] Adapter interface sketched in `UI/README.md` (+ `UI/adapters/` stubs)  
- [x] Slash palette UX specified (open on `/`, filter, refuse unknown)  
- [x] DSC and at least one fly pack load through the same console entrypoint (`python -m console`)  
- [x] Signal charts + scrolling terminal + bottom command line present in v0  
- [x] Mode banner always visible  

## Related folders
- `UI/` — console scaffold (non-essential monitor/dialog)
- `MODEL/active/` — DSC checkpoint under development (default `/load dsc`)
- `MODELS/` — biological packs only

## Later (not this stub)
TUI toolkit choice (e.g. Textual / rich / ratatui), live WebSocket feed, braille canvas density, neuropil color legend, pairing with R001 meta-manager event stream.
