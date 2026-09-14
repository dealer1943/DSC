---
id: R001
title: Connectome meta-manager (reserved self-benchmarking resource)
status: light_implemented
updated: 2026-09-13
related_features: [F005, F006, F009, F010]
related_benchmarks: [B005, B006, B009, B010, B015]
---

## Question
Do DSC **benchmarks improve** when the system reserves **one dedicated resource** whose job is not task performance, but:

1. **running benchmarks on the connectome itself**, and  
2. **managing its own states** (lifecycle, integrity, measurement schedule)?

Call that resource a **meta-manager** (working name). It is part of the population geometry in spirit, but **quarantined** from ordinary task utility so measurement does not collapse into the thing being measured.

## Why this is a first-principles issue
Benchmarks that are computed *by* the same evolutionary pressure they evaluate are easy to game: the population can optimize for the meter. Separating **act** from **assay** is how experimental science keeps instruments honest. A reserved meta-manager is the architectural analog of a lab instrument rack that is not also a subject in the trial.

Self-state management matters for the same reason: pruning, latent retention, rollback, and footprint reporting need a locus that tracks population integrity **without** competing for the same utility score as task specialists. Otherwise “management” becomes just another niche that gets pruned when task reward spikes.

## Hypothesis
A DSC with a reserved meta-manager will show, relative to an otherwise identical population with no reserved assay resource:

- **More stable** B010 task-vs-footprint Pareto over evolution (fewer silent footprint regressions).  
- **Higher integrity** on B005 / B007 / B008 / B009 (utility non-degeneracy, prune-without-forgetting, coverage conservation, rollback efficacy) because assay signal is not drowned by task specialists.  
- **Better B015** seed/calibration stability: the manager’s schedule and metrics are reproducible across seeds when its parameters are held out of free mutation (or mutated under a separate, slower clock).  
- Possible **task cost**: slightly lower peak task score if the reserved capacity would have helped the task—acceptable if compactness and integrity gains dominate MVP success criteria.

## Proposed role (design sketch, not implementation)

| Concern | Meta-manager responsibility |
|---------|-----------------------------|
| Assay | Trigger B001–B010 (and later B011–B015) on a fixed schedule or after each evolution cycle |
| Self-state | Maintain a small, typed state: last assay vector, integrity flags, rollback pointers, dormant-pool census |
| Isolation | Does **not** enter the main task-utility ranking; cannot be pruned by task utility alone |
| Coupling | May *read* population activations / utilities; write-back limited to assay logs, integrity flags, and optional pause/rollback **requests** consumed by F009 |
| Substrate | Lives on the same substrate graph or on a tiny side-channel; either way, its compute cost is reported in footprint |

## Experimental contrast (how to know if benches improve)
Hold synthetic substrate, task harness, and evolution hyperparameters fixed. Compare:

1. **Baseline** — no reserved manager; assays run externally (offline scripts) only.  
2. **External-only** — same as baseline (control for “we measured more carefully”).  
3. **Reserved meta-manager** — one (or fixed-K) resource(s) as above, assays in-loop.  
4. **Ablation** — manager present but **not** isolated (competes on task utility) — predicts gaming / collapse.

Primary outcomes: deltas on B005, B007–B010, B015; secondary: task accuracy, active footprint, assay wall-time.

## Open questions
1. Is the meta-manager a **state cell type**, a **side process**, or a **privileged STEM** that never differentiates into task types?  
2. How large is “reserved” (1 cell, fixed % of compute, fixed memory)?  
3. Can the manager mutate its *assay schedule* without mutating *assay definitions*? (Definitions should stay pinned to BENCHMARKS docs.)  
4. Does FlyWire comparison (F011) need a parallel meta-manager when the substrate is biological, or only on synthetic MVP?  
5. Risk: a manager that can request rollback becomes a single point of control—what dual-control or quorum keeps it from freezing evolution?

## Non-goals (for this note)
- Implementing the manager  
- Replacing BENCHMARKS docs with runtime code  
- Claiming the hypothesis is already true

## Promotion path
If experiments support the hypothesis, graduate to a feature stub (e.g. F012) paired with a dedicated benchmark (manager isolation + assay fidelity), and wire acceptance into the evolution-loop roadmap (phases 3–4).

## One-line claim to test
**A connectome that reserves capacity to measure and steward itself produces more trustworthy benchmark trajectories than one that only performs the task.**


## Light implementation (2026-09-14)
External assay logger only (not an in-loop cell): `dsc/meta/manager.py` appends JSONL rows to `BENCHMARKS/meta/r001_assay_log.jsonl` from `tools/dev_run`. Still **not** a reserved population resource — that remains the open architectural question above.
