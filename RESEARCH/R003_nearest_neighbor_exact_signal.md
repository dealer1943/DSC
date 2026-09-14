---
id: R003
title: Nearest-neighbor exact signal (no per-cell full is_signal stack)
status: open
updated: 2026-09-14
related: [F002, F015, F023, F026, F027, F028, F029, F030, R002]
---

## Question
Today every state cell carries its **own** local book (hidden, gates, type kernels, …) and then **blends** many neighbors into a message vector. Can we instead treat “what’s on the wire” as **exact nearest-neighbor signal** — e.g. on a 3×3 sheet, each seat only sees the **verbatim** signal of its closest neighbor(s) — instead of each cell holding / reconstructing a copy of a full shared `is_signal` stack?

This is research, not a feature commitment. Promote to F0xx only after a cheap A/B on Profile D (sheet / ME_R first).

## Layman

Picture a **3×3 neighborhood grid** of seats.

**Current DSC habit (stack-per-seat):**  
Every desk keeps its own full blotter *and* averages shouts from everyone wired to it. If the building also has a “who’s talking” board (F030) or a “one floor up” glance (F029), that is *extra* channels — but the core tick still **mixes** neighbor hiddens into a new local vector. Each seat ends up with a **processed copy** of the room, not a live peek at the person next to them.

**Proposed habit (exact nearest signal):**  
Your blotter stays yours. For *incoming signal*, you don’t rebuild the whole room. You only take the **exact** tape from the seat closest to you (or the few nearest). No average, no second full stack per cell for “what everyone is saying.” If the middle desk shouts `0.73`, the desks that list it as nearest **read `0.73`** — same number, not a muddy blend.

Intuition: markets often price the **adjacent** print, not a soup of the whole pit. Sheets (optic) already want local retinotopy; this asks whether **local exact read** beats **global-ish mix** for task under matched wiring.

## Technical status quo (what we actually store / move)

Per cell (F002), roughly:

| Field | Shape | Role |
|-------|-------|------|
| `hidden` | `(N, H)` | last local state (`H=8` default) |
| `gate_logits`, `type_weights`, `bias` | per-cell | type mixture / local kernels |
| `activity` | `(N,)` | ‖hidden‖ |
| messages (ephemeral) | `(N, H)` | **gather** of neighbor `hidden` via adj (F023/F026) |

Tick path (`dsc/cells.py` → `step_population`):

1. Gather: `messages[i] = mean` (or hub-weighted) of `hidden[j]` for edges `j→i`.
2. Optional F029: add elevated partner hidden (index-fold).
3. Optional F030: edge-masked glance from talking in-neighbors + light global talk frac.
4. `hidden' = gated_response(tanh(messages + bias + inject))`.

So we do **not** literally allocate `N` copies of a global `is_signal` tensor today — but each cell **materializes an H-dim message that is a compressed copy/blend of many neighbors’ stacks**. Cost scales with edges (sparse gather) or `N²` (dense). Memory stays `O(N·H)` for hidden, but **information** is “everyone’s mix,” not “nearest exact.”

User framing “each cell has a copy of the entire is_signal stack” = that **effective** duplication: every seat carries a full local channel *as if* it owned the whole signal story, instead of a **pointer-like** read of the nearest source.

## Proposal — nearest-neighbor exact signal (NNES)

### Core idea
Define a **signal owner** relation `nn[i] ∈ {0..N-1}` (or a small set `nn_k[i]`):

- **Exact read:** `signal_in[i] = hidden[nn[i]]` (or concat of k nearest) — **no** degree-normalized sum.
- **Local write:** cell `i` still updates only `hidden[i]` from `signal_in[i]` + own bias/gates/inject.
- **Optional shared board:** keep F030-style **bit** presence separate; do not expand it into a full H stack per cell.

### 3×3 grid example

```
0 1 2
3 4 5
6 7 8
```

Example `nn` (4-neighbor, pick one canonical “nearest” — e.g. prefer W then N then E then S; center uses W):

| cell | nearest | exact signal_in |
|------|---------|-----------------|
| 4 (center) | 3 | `hidden[3]` |
| 5 | 4 | `hidden[4]` |
| 0 (corner) | 1 or 3 | `hidden[1]` (tie-break rule) |

On a **graph** substrate (preferential / FlyWire-adj / sheet_hub): define nearest as

1. **Spatial** (if coords exist): argmin Euclidean among in-neighbors, or  
2. **Structural:** among in-neighbors, argmax edge weight / syn_count, or argmin hop via a fixed layout index (sheet), or  
3. **Procedural sheet index:** same fold math as F028/F029 but **replace mix with exact assign**.

### What this is not
- Not “delete hidden” — each cell still has local state.
- Not full broadcast of one global vector to all cells (that’s closer to a single shared stack).
- Not F030 alone — talk board is a **bool**; NNES is **exact H-vector (or scalar channel) from one peer**.

### Memory / compute sketch

| Scheme | Message work / tick | “Copy” semantics |
|--------|---------------------|------------------|
| Dense gather | `O(N²·H)` | blend of all in-neighbors |
| Sparse gather (F026) | `O(E·H)` | blend of in-neighbors |
| Talk glance (F030) | `O(E·H)` masked | blend of talking in-neighbors |
| **NNES (1-nearest)** | **`O(N·H)`** gather | **exact** one peer |
| NNES (k-nearest, k≪deg) | `O(N·k·H)` | exact k peers (concat or gated pick) |

If we later add multi-channel `is_signal` (task / type / talk / bilayer), NNES says: **don’t replicate the full channel pack on every cell** — store channels once on the owner, readers **index** the nearest owner’s pack.

## Why it might help DSC (hypotheses)

1. **Sheet / ME_R:** retinotopy wants crisp local copy, not soup; exact nearest may shrink task_error gaps that stay fly-favored under mix (standings: ME/LO contested).  
2. **Anti-overfit:** one procedural `nn[i]` rule (index/spatial) — no neuropil hardcodes (same discipline as F028/F029).  
3. **Cheaper tick** on hubby graphs: `O(N)` vs `O(E)` when E ≫ N.  
4. **Clearer ablations:** “exact vs mean” is a single switch; scoreboard-readable.

## Risks / adversarial notes

- **Hub starvation:** leaves that only point at a quiet nearest peer never see hub signal — may need k=2 or “nearest *talking*” (compose with F030).  
- **Directed graphs:** in-nearest ≠ out-nearest; fix convention (in-edge only).  
- **Dag / DAG latency:** exact copy of prev-tick hidden (already true for gather) — document one-tick lag.  
- **GNG win regression:** preferential+hub-aware **won** with mean gather; NNES must be **regime-opt-in**, never default that kills GNG (lesson from F028: sheet_hub ≠ GNG).  
- **Scoreboard noise:** tiny task gaps already flip wins; require multi-seed before promoting.

## Proposed experiments (when promoted toward a feature)

Flags (sketch): `NEAREST_EXACT=False`, `NEAREST_K=1`, `NEAREST_RULE=sheet|spatial|inweight`.

1. **ME_R sheet_hub** N=512 hard harness, seed 42 + multi-seed 42–48: baseline gather vs NNES k=1 vs k=3.  
2. **GNG sanity:** preferential + hub-aware with NNES must not wipe the 6–0 (or document regime gate).  
3. **AVLP modular ± bilayer:** does exact nearest substitute for bilayer mix?  
4. Report task_error, E_tick, scoreboard wins — same Profile D protocol as F021.

Success bar (draft): multi-seed mean task gap vs fly improves on ME_R **without** GNG collapse; else keep as failed opt-in note in this R003.

## Relation to existing knobs

| Knob | Relationship |
|------|----------------|
| F023 hub-aware | Orthogonal: can weight *which* peer is “nearest” by out-degree. |
| F026 sparse gather | NNES can skip gather entirely when k=1. |
| F027/F028 sheet | Natural geometry for `nn[i]`. |
| F029 bilayer | Special case of exact partner read — NNES generalizes “one partner” without EMA mix (or keeps EMA on that single peer). |
| F030 talk board | Presence bits stay shared; exact signal still from nearest *talking* peer if desired. |

## Wiring status (2026-09-14)
Default-off flag `NEAREST_EXACT` in `dsc/cells.py` + `--nearest-exact` on `tools.flywire_stress`.
- Isolated / no in-edge → self-hidden (open decision #3 closed).
- `NEAREST_RULE=sheet` is **index** `|i-j|` among in-neighbors — procedural proxy, **not** anatomical nearest. Prefer `inweight` when comparing on fly-adj arms.
- Replaces mean/hub gather; F029/F030 still layer on if enabled — keep them **off** for a pure nearest A/B (report `nearest_note`).
- ME_R sheet_hub seed-42: scoreboard improved on cost axes, **task_error worsened** vs baseline gather — keep opt-in / research.

## Open decisions

1. Scalar channel vs full `hidden[H]` exact copy?  
2. Same-tick vs prev-tick read (race on update order)?  
3. Fallback when cell has **no** in-neighbors?  
4. Promote as F031 only after ME_R multi-seed + GNG sanity green?

## Non-goals (this research doc)

- No implementation in this file.  
- No claim that NNES beats FlyWire.  
- No neuropil-specific wiring tables.

## Successor LLM note
If implementing: touch `dsc/cells.py` `step_population` behind a default-off flag; wire `--nearest-exact` in `tools/flywire_stress.py`; add FEATURES/F031 only after the experiment table exists under `BENCHMARKS/runs/`. Keep dual-layer writeup in the feature doc. Regime-select with preferential for GNG — do not `if neuropil == "ME_R"`.
