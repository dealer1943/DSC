# FlyWire FAFB v783 — offline connectivity pack

Whole-brain **female adult fly** connectome connectivity (FlyWire / FAFB), downloaded from Zenodo for offline DSC comparison work (`FEATURES/F011`).

**Source:** [Zenodo 10676866](https://zenodo.org/records/10676866) — *FlyWire Whole-brain Connectome Connectivity Data*, version **783**  
**Explorer (optional, online):** https://codex.flywire.ai  
**Scale (Codex FAFB v783):** ~139k neurons, ~3.7M neuron–neuron connections  

This folder is the **graph tables**, not the EM imagery.

---

## What’s in the pack

| File | Approx size | Role |
|------|-------------|------|
| `proofread_connections_783.feather` | ~852 MB | **Start here.** Proofread synapses aggregated to neuron→neuron (per neuropil) edges with synapse counts + NT probability averages |
| `proofread_root_ids_783.npy` | ~1 MB | Array of proofread neuron root IDs |
| `per_neuron_neuropil_count_pre_783.feather` | ~17 MB | Per-neuron presynapse counts by neuropil |
| `per_neuron_neuropil_count_post_783.feather` | ~234 MB | Per-neuron postsynapse counts by neuropil |
| `flywire_synapses_783.feather` | ~9.5 GB | Individual synapse points (full detail; heavy) |
| `manifest.json` | small | Local download manifest (sizes / checksums) |

Pack total ≈ **10.6 GB**.

---

## How to use (Python)

Needs: `pandas`, `pyarrow` (or `fastparquet`), `numpy`. Optional: `scipy` / `networkx` for graph builds.

### 1. Load the edge table (usual path)

```python
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(".../DSC/MODELS/fly/flywire_v783")

edges = pd.read_feather(ROOT / "proofread_connections_783.feather")
# Typical columns include:
#   pre_pt_root_id, post_pt_root_id, neuropil, syn_count,
#   gaba_avg, ach_avg, glut_avg, ... (NT averages over synapses in that neuropil)

roots = np.load(ROOT / "proofread_root_ids_783.npy")
```

### 2. Build a directed weighted adjacency (neuron → neuron)

Collapse neuropil rows if you want a single edge per pair:

```python
pair = (
    edges.groupby(["pre_pt_root_id", "post_pt_root_id"], as_index=False)["syn_count"]
    .sum()
)
# pair columns: pre_pt_root_id, post_pt_root_id, syn_count
```

Map IDs to dense indices only when you need a matrix; prefer sparse COO for DSC substrate work:

```python
import scipy.sparse as sp

nodes = np.unique(np.concatenate([pair.pre_pt_root_id, pair.post_pt_root_id]))
index = {int(n): i for i, n in enumerate(nodes)}
rows = pair.pre_pt_root_id.map(index)
cols = pair.post_pt_root_id.map(index)
W = sp.coo_matrix(
    (pair.syn_count.to_numpy(dtype=float), (rows, cols)),
    shape=(len(nodes), len(nodes)),
).tocsr()
# W[i, j] = synapse count from nodes[i] -> nodes[j]
```

### 3. Sparsity / directedness checks (aligns with F001 / B001 spirit)

```python
n = W.shape[0]
nnz = W.nnz
density = nnz / (n * n)
assert density < 0.10  # DSC guardrail for synthetic; biological may differ — report, don't invent
is_directed = (W != W.T).nnz > 0 or True  # FlyWire edges are directed by construction
print(dict(n=n, nnz=nnz, density=density))
```

### 4. Optional: neuropil-conditioned subgraphs

Filter `edges` on `neuropil` before the groupby when comparing region-local dynamics.

### 5. Optional: full synapse table

Only load `flywire_synapses_783.feather` when you need per-synapse coordinates / cleft-level detail. Prefer chunked reads; do not hold the full 9.5 GB frame unless necessary.

```python
# Example: column peek without loading everything into RAM depends on pyarrow dataset APIs;
# for most DSC comparison work, proofread_connections is enough.
```

### 6. Neurotransmitter-aware weights (optional)

`proofread_connections_783.feather` carries average NT class probabilities per aggregated edge. A simple signed policy (document any choice you make):

```python
# Illustrative only — freeze policy in code/docs before experiments
# e.g. excitatory ~ acetylcholine, inhibitory ~ GABA / glutamate (fly conventions vary by paper)
```

Do not invent signs for missing NT; prefer explicit “unknown → zero or unsigned weight” policies (same honesty bar as MaleCNS fruitfly preprocessing).

---

## Role in DSC

1. Develop / evolve DSC on **synthetic** sparse directed graphs (F001+).  
2. Swap substrate to **FlyWire** for biological comparison (this pack).  
3. Report task + footprint metrics on both; use degree-preserving rewires as nulls when claiming topology effects (`design_doc` Part 2).

MaleCNS (`../male_cns_v1.0/`) and hemibrain (`../hemibrain_v1.2.1/`) remain secondary fly baselines.

---

## Provenance

- Dataset: FlyWire consortium / Dorkenwald et al. connectivity release v783  
- Zenodo record: 10676866  
- Decision: `FEATURES/F011_offline_flywire_comparison_substrate.md`  
- Offline-only: no CAVE token required for these files  

Cite the FlyWire / FAFB papers appropriate to your writeup when publishing results.
