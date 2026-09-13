# DSC MVP Overview

Extracted from `design_doc.md` Part 1 for quick orientation. Part 2 (benchmarking) stays in `design_doc.md` until `BENCHMARKS/` is populated.

## Objective
A working Dynamic State Connectome that shows:

1. **State emergence** — undifferentiated STEM cells self-organize into functional types  
2. **Evolutionary dynamics** — selection, reproduction, mutation across generations  
3. **Pruning & absorption** — low-utility states removed; function absorbed by neighbors; parameters retained latently  

**Success:** solve a simple reproducible temporal task with a compact state footprint; pruning reduces active states without catastrophic performance loss.

## Core architecture

| Layer | Role | MVP choice |
|--------|------|------------|
| Substrate Graph | "Hardware" topology | Synthetic sparse directed graph (ER / WS / BA). Not full zebrafish yet. |
| State Cells | "Software" units | Modular cells; types emerge; STEM = gated mixture of type behaviors |

### StateCell (conceptual schema)

```
StateCell {
  id: UUID
  type: STEM | ATTRACTOR | LATENT | MODULATORY | MODULAR | METASTABLE
  parameters: Dict[str, float]
  utility: float          # EMA of task contribution
  age: int
  connections: List[UUID]
  differentiation: float  # 0 stem-plastic → 1 committed
}
```

## Evolution loop (every N task steps)

1. **Evaluation** — multi-term utility (task + coverage + novelty − compute)  
2. **Selection & pruning** — threshold for M cycles; absorb coverage; latent retention  
3. **Reproduction & mutation** — clone top-K; param noise; rare type mutate; rare hybridize  
4. **Stability guardrails** — reachability, interference (corr > 0.8), no transition collapse; else rollback  

## Phase roadmap

| # | Deliverable | Key guardrail |
|---|-------------|----------------|
| 1 | Substrate generator | Sparse, directed |
| 2 | Stem state cell | Differentiable type gating |
| 3 | Evolution loop | Tractable utility |
| 4 | Pruning & absorption | Rollback tested |
| 5 | Temporal task integration | Clear measurable objective |

## Deferred (post-MVP)
Swap synthetic substrate for zebrafish connectome; compare to fly; NeuroBench / null-model / ablation protocol from `design_doc.md` Part 2.
