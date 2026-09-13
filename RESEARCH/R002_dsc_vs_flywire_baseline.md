---
id: R002
title: DSC vs FlyWire — baseline side-by-side (no training)
status: snapshot
updated: 2026-09-13
related: [F001, F002, F003, F005, F010, F011, F012]
---

## Question
At **baseline** — current DSC MVP checkpoint vs offline FlyWire v783 pack, **with no further training, evolution, or pruning** — how do the two “brains” compare on size, topology, and role?

## Snapshot provenance
| Side | Artifact | When |
|------|----------|------|
| DSC | `MODEL/active` revision **`r1-n128-e1276`** (F001–F003, F005, F010 MVP) | 2026-09-13 |
| FlyWire | `MODELS/fly/flywire_v783` proofread connections (+ full pack on disk) | Zenodo 10676866 / local pack |

**Baseline means:** DSC after initial build + 16 warm ticks only (not trained to convergence). FlyWire is a **static biological graph** (no DSC dynamics on it). This is an apples-to-oranges *substrate & footprint* comparison, not a claim that DSC matches fly intelligence.

## Side-by-side

| Axis | DSC (active MVP) | FlyWire v783 |
|------|------------------|--------------|
| **Role in project** | Evolving synthetic connectome under development | Offline **biological comparison** pack (F011) |
| **What “brain” means** | State cells on a generated sparse digraph | Proofread neuron connectivity (adult fly) |
| **Nodes** | **128** | **138,639** |
| **Directed edges** | **1,276** | **16,847,997** |
| **Node scale ratio** | 1× | ~**1,083×** more nodes |
| **Edge scale ratio** | 1× | ~**13,204×** more edges |
| **Density** (edges / N(N−1)) | **7.85%** | **0.088%** |
| **Mean degree** (in+out) | **19.9** | **243.0** |
| **Median degree** | **20** | **164** |
| **Max degree** | **30** | **27,492** |
| **Degree shape** | Narrow (ER-like) | Heavy-tailed / hubby |
| **Directed?** | Yes | Yes |
| **Self-loops** | None | Not used in UI edge table |
| **Weakly connected components** (undirected view) | **1** | (not computed here; whole-brain pack is large) |
| **Spatial / neuropil structure** | None (abstract graph) | **79** neuropil labels in edge table |
| **Synapse weight signal** | Binary edge (1) in MVP | `syn_count` mean **~3.23** |
| **Dynamics** | Yes — STEM cells, type gating, lag-1 task, multi-term utility | No (static anatomy) |
| **Learned types / differentiation** | Soft mixture; **100% STEM-labeled** at baseline (diff&lt;0.35) | Biological types exist upstream; not loaded as DSC types |
| **Task harness** | `lag1_scalar_predict` | N/A |
| **On-disk footprint** | **~65 KiB** (`checkpoint.npz` + harness + manifest) | **~9.9 GB** pack folder (~**10.6 GB** Zenodo set); edges-only feather **~813 MB** |
| **UI load target** | `/load dsc` → pack name `active` | `/load flywire` → pack name `flywire_v783` |
| **Online auth required** | No | No (offline Zenodo pack) |

### Footprint at a glance

| | DSC | FlyWire (full pack) | FlyWire (edges feather only) |
|--|-----|---------------------|------------------------------|
| Disk | ~65 KiB | ~9.9 GB | ~813 MB |
| vs DSC | 1× | ~**160,000×** | ~**12,500×** |

## How to read this (first principles)
1. **DSC is mechanism-first.** It is small on purpose: sparse, directed, reproducible, watchable in the operator console while evolution features land.  
2. **FlyWire is biology-first.** It is large, sparse at whole-brain scale, and hub-structured — a stress test / comparison substrate, not the DSC bootstrap.  
3. **Density looks “higher” on DSC** only because N is tiny; absolute wiring complexity is overwhelmingly on FlyWire.  
4. **Baseline ≠ trained.** DSC utilities/activity exist after warm ticks; there is no claim of task mastery or type commitment yet (F004+ still ahead).  
5. **Fair future comps** should hold protocols fixed (B001 topology invariants, null models, later swap-in of bio graphs) rather than raw node count contests.

## Ratios worth remembering
- Nodes: FlyWire / DSC ≈ **1.08×10³**  
- Edges: FlyWire / DSC ≈ **1.32×10⁴**  
- Disk (full pack / DSC): ≈ **1.6×10⁵**  

## Non-goals of this note
- Training curves, evolution, pruning efficacy  
- Claiming DSC “matches” or “beats” FlyWire  
- Loading full FlyWire synapses (~9.5 GB) into the runtime

## Benchmark blueprint
Automated efficiency claims over these axes: **[B016](../BENCHMARKS/B016_flywire_efficiency_parity.md)** (future tool).

## Next measurements (optional)
- Degree histogram overlay (log) after null-model rewiring on DSC  
- Same harness metrics before/after F006 evolution  
- Neuropil-focused FlyWire subgraphs sized closer to DSC N for controlled swaps  

## One-line takeaway
**At baseline, DSC is a 128-node, ~65 KiB dynamical sketch; FlyWire is a ~139k-node, multi-GB static fly brain — same project shelf, radically different jobs.**
