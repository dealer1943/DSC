# Dynamic State Connectome (DSC)

Offline-first research codebase for a **dynamic state connectome**: evolving state cells on a sparse directed substrate, with biological packs (FlyWire, …) as comparison graphs — not the bootstrap.

Work is sliced and documented (`HANDOFF.md`, `SLICES/`, `FEATURES/`, `BENCHMARKS/`) so successors can continue from files alone.

## Quick layout

| Path | Role |
|------|------|
| `FEATURES/` | Capability stubs (F001–F012…) |
| `BENCHMARKS/` | Paired + system benches (B001–B015…) |
| `MODEL/active/` | **DSC checkpoint under development** (small; runtime weights gitignored) |
| `MODELS/` | **Biological** packs (FlyWire, MaleCNS, hemibrain) — **data gitignored** |
| `UI/` | Optional operator console (monitor/dialog; not required for correctness) |
| `HANDOFF.md` | Current status / next slice |
| `design_doc.md` | MVP blueprint |

`MODEL/` ≠ `MODELS/`. Active DSC lives in `MODEL/`. Published connectomes live in `MODELS/`.

## Getting started (clone)

```bash
git clone <your-fork-or-org>/DSC.git
cd DSC
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .                 # register `dsc` package (needed for `python -m dsc`)
```

Requires **Python 3.9+**. Dependencies live in root [`requirements.txt`](requirements.txt) (NumPy for `dsc/`; Textual/pandas/pyarrow for the UI + FlyWire load).

Large connectome files are **not** in git. Follow **Getting biological packs** below before `/load flywire` in the UI.

### Build / refresh active DSC checkpoint

```bash
# from repo root (or any cwd after `pip install -e .`)
python -m dsc    # writes MODEL/active (progress bar in terminal)
# equivalent: dsc
```

### Operator console (optional)

```bash
cd UI
python -m console
```

(`UI/requirements.txt` redirects to the root file if you install from `UI/`.)

Default smoke path:

```text
/load dsc
/tick 8
/load flywire
/status
/focus AL
/signal degree
```

## Getting biological packs

### FlyWire v783 (primary offline comparison — F011)

**Where files go:** `MODELS/fly/flywire_v783/`

**Source:** Zenodo record [10676866](https://zenodo.org/records/10676866) (DOI `10.5281/zenodo.10676866`)

**Files to download** (into that folder):

| File | Approx size | Role |
|------|-------------|------|
| `proofread_connections_783.feather` | ~852 MB | Main edge table (UI + most comps) |
| `proofread_root_ids_783.npy` | ~1 MB | Proofread neuron ids |
| `per_neuron_neuropil_count_pre_783.feather` | ~17 MB | Pre neuropil counts |
| `per_neuron_neuropil_count_post_783.feather` | ~234 MB | Post neuropil counts |
| `flywire_synapses_783.feather` | ~9.5 GB | Full synapses (optional for UI; needed for some analyses) |

How-to load / adjacency notes: `MODELS/fly/flywire_v783/README.md`  
Pack overview: `MODELS/README.md` and `MODELS/fly/README.md`

**Minimal UI test** only needs `proofread_connections_783.feather` (+ optional neuropil tables). The ~9.5 GB synapses file can wait.

Example (curl continue; verify MD5s against `manifest.json` when present):

```bash
mkdir -p MODELS/fly/flywire_v783
cd MODELS/fly/flywire_v783
# Example URL pattern — prefer links from the Zenodo record page:
# https://zenodo.org/records/10676866
curl -L -C - -o proofread_connections_783.feather \
  "https://zenodo.org/api/records/10676866/files/proofread_connections_783.feather/content"
```

### MaleCNS / Hemibrain (optional fly baselines)

| Pack | Path | Notes |
|------|------|--------|
| MaleCNS v1.0 | `MODELS/fly/male_cns_v1.0/` | ~1 GB feathers (weights, NT, annotations) |
| Hemibrain v1.2.1 | `MODELS/fly/hemibrain_v1.2.1/` | ~100 MB edgelist + meta |

Keep `manifest.json` / README in each pack folder; git ignores the binary data.

## Active DSC model

Runtime state for the system under development:

- Tip: `MODEL/active/` (see `MODEL/README.md`)
- `manifest.json` is tracked; large tensors/checkpoints are gitignored

## Design notes

- Offline-first: no CAVE auth for MVP comparison (zebrafish/Fish1 path dropped — see F011).
- UI is an **instrument rack** (F012), not part of the evolution loop.
- Reserved self-assay idea: `RESEARCH/R001_connectome_meta_manager.md`.

## License / citation

Biological data retain their upstream licenses and citation requirements (FlyWire / Zenodo, Janelia MaleCNS, hemibrain). Cite those sources when publishing results that use the packs.
