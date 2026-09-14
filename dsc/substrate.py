"""F001 / F022 — synthetic sparse directed substrates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from dsc import defaults
from dsc.progress import ProgressCb, emit

FAMILIES = ("erdos_renyi_directed", "preferential_directed", "modular_directed", "laminar_directed")


@dataclass
class Substrate:
    adj: np.ndarray  # (N,N) uint8, directed, no self-loops
    meta: Dict[str, Any]

    @property
    def n(self) -> int:
        return int(self.adj.shape[0])

    @property
    def n_edges(self) -> int:
        return int(self.adj.sum())

    @property
    def density(self) -> float:
        n = self.n
        denom = n * (n - 1)
        return float(self.n_edges / denom) if denom else 0.0

    def edge_index(self) -> tuple:
        """Cached (src, dst) nonzero coords for sparse message passing (F026)."""
        key = id(self.adj)
        cache = getattr(self, "_edge_cache", None)
        if cache is None or cache[0] != key:
            src, dst = np.nonzero(self.adj)
            self._edge_cache = (key, src.astype(np.int32), dst.astype(np.int32))
        return self._edge_cache[1], self._edge_cache[2]


def _cap_density(adj: np.ndarray, rng: np.random.Generator, max_dens: float = 0.09) -> np.ndarray:
    n = adj.shape[0]
    dens = float(adj.sum() / max(1, n * (n - 1)))
    if dens < 0.10:
        return adj
    edges = np.argwhere(adj)
    keep = int(max_dens * n * (n - 1))
    if len(edges) > keep:
        pick = rng.choice(len(edges), size=keep, replace=False)
        new = np.zeros_like(adj)
        for i, j in edges[pick]:
            new[i, j] = 1
        adj = new
    return adj


def _er(n: int, p: float, rng: np.random.Generator) -> np.ndarray:
    adj = (rng.random((n, n)) < p).astype(np.uint8)
    np.fill_diagonal(adj, 0)
    return _cap_density(adj, rng)


def _preferential(n: int, target_edges: int, rng: np.random.Generator) -> np.ndarray:
    """Directed preferential attachment toward a sparse heavy-tailed digraph."""
    adj = np.zeros((n, n), dtype=np.uint8)
    # seed a small cycle so degrees start nonzero
    m0 = min(8, n)
    for i in range(m0):
        adj[i, (i + 1) % m0] = 1
    in_deg = adj.sum(axis=0).astype(np.float64) + 1.0
    out_deg = adj.sum(axis=1).astype(np.float64) + 1.0
    edges = int(adj.sum())
    target_edges = int(max(edges + 1, min(target_edges, int(0.09 * n * (n - 1)))))
    guard = 0
    while edges < target_edges and guard < target_edges * 40:
        guard += 1
        src = int(rng.choice(n, p=out_deg / out_deg.sum()))
        dst = int(rng.choice(n, p=in_deg / in_deg.sum()))
        if src == dst or adj[src, dst]:
            continue
        adj[src, dst] = 1
        out_deg[src] += 1.0
        in_deg[dst] += 1.0
        edges += 1
    return _cap_density(adj, rng)


def _modular(n: int, target_edges: int, rng: np.random.Generator, n_blocks: int = 8) -> np.ndarray:
    """Stochastic block digraph: dense within blocks, sparse between."""
    adj = np.zeros((n, n), dtype=np.uint8)
    blocks = np.array_split(np.arange(n), n_blocks)
    # probabilities scaled to hit target roughly
    n_pairs = n * (n - 1)
    # within vs between mix ~ 70/30 of edges
    within_budget = int(0.7 * target_edges)
    between_budget = max(1, target_edges - within_budget)
    # place within
    placed = 0
    guard = 0
    while placed < within_budget and guard < within_budget * 50:
        guard += 1
        b = blocks[int(rng.integers(0, len(blocks)))]
        if len(b) < 2:
            continue
        i, j = rng.choice(b, size=2, replace=False)
        if adj[i, j]:
            continue
        adj[i, j] = 1
        placed += 1
    placed_b = 0
    guard = 0
    while placed_b < between_budget and guard < between_budget * 50:
        guard += 1
        i = int(rng.integers(0, n))
        j = int(rng.integers(0, n))
        if i == j or adj[i, j]:
            continue
        # prefer different blocks
        if (i * n_blocks) // n == (j * n_blocks) // n and rng.random() < 0.7:
            continue
        adj[i, j] = 1
        placed_b += 1
    return _cap_density(adj, rng)


def _laminar(n: int, target_edges: int, rng: np.random.Generator, n_layers: int | None = None) -> np.ndarray:
    """Stacked sheets: dense local in-layer edges, sparser adjacent-layer bridges.

    Layman: floors in a building — lots of walking on your floor, fewer stairs.
    Tech: cells partitioned into L layers; local digraph within layer;
    light interlayer coupling. Fills to target_edges with widening locality.
    """
    adj = np.zeros((n, n), dtype=np.uint8)
    if n_layers is None:
        n_layers = int(np.clip(round(np.sqrt(n) / 2), 4, 16))
    layers = np.array_split(np.arange(n), n_layers)
    within_budget = int(0.75 * target_edges)
    between_budget = max(1, target_edges - within_budget)

    def _add_edge(a: int, b: int) -> bool:
        if a == b or adj[a, b]:
            return False
        adj[a, b] = 1
        return True

    placed = 0
    # pass 1: tight local
    # pass 2: wider local
    # pass 3: any within-layer
    for radius_frac in (1 / 8, 1 / 3, 1.0):
        guard = 0
        while placed < within_budget and guard < within_budget * 100:
            guard += 1
            li = int(rng.integers(0, n_layers))
            idxs = layers[li]
            if len(idxs) < 2:
                continue
            a_pos = int(rng.integers(0, len(idxs)))
            a = int(idxs[a_pos])
            rad = max(1, int(len(idxs) * radius_frac))
            lo = max(0, a_pos - rad)
            hi = min(len(idxs), a_pos + rad + 1)
            neighborhood = idxs[lo:hi]
            b = int(rng.choice(neighborhood))
            if _add_edge(a, b):
                placed += 1

    placed_b = 0
    guard = 0
    while placed_b < between_budget and guard < between_budget * 120:
        guard += 1
        li = int(rng.integers(0, max(1, n_layers - 1)))
        a_layer = layers[li]
        b_layer = layers[min(li + 1, n_layers - 1)]
        if len(a_layer) == 0 or len(b_layer) == 0:
            continue
        pa = int(rng.integers(0, len(a_layer)))
        pb = int(np.clip(
            int(pa * len(b_layer) / max(1, len(a_layer))) + int(rng.integers(-3, 4)),
            0,
            len(b_layer) - 1,
        ))
        a, b = int(a_layer[pa]), int(b_layer[pb])
        src, dst = (a, b) if rng.random() < 0.8 else (b, a)
        if _add_edge(src, dst):
            placed_b += 1

    # final fill: any missing edges preferentially within-layer then anywhere
    guard = 0
    while int(adj.sum()) < target_edges and guard < target_edges * 50:
        guard += 1
        if rng.random() < 0.7:
            li = int(rng.integers(0, n_layers))
            idxs = layers[li]
            if len(idxs) < 2:
                continue
            a, b = (int(x) for x in rng.choice(idxs, size=2, replace=False))
        else:
            a = int(rng.integers(0, n))
            b = int(rng.integers(0, n))
        _add_edge(a, b)

    return _cap_density(adj, rng)



def generate_substrate(
    n: int = defaults.N_NODES,
    p: float = defaults.EDGE_PROB,
    seed: int = defaults.SEED,
    progress: Optional[ProgressCb] = None,
    family: str = "erdos_renyi_directed",
    target_edges: Optional[int] = None,
) -> Substrate:
    """Build a sparse directed substrate.

    Families (F022 / F027):
      - erdos_renyi_directed (default MVP)
      - preferential_directed (heavy-tailed hubs)
      - modular_directed (block / neuropil-ish modules)
      - laminar_directed (stacked sheets — optic/ME-LO prior)
    """
    emit(progress, 0.05, "substrate: seeding RNG")
    rng = np.random.default_rng(seed)
    fam = (family or defaults.GRAPH_FAMILY).strip().lower()
    aliases = {
        "er": "erdos_renyi_directed",
        "erdos": "erdos_renyi_directed",
        "erdos_renyi": "erdos_renyi_directed",
        "preferential": "preferential_directed",
        "pa": "preferential_directed",
        "modular": "modular_directed",
        "sbm": "modular_directed",
        "block": "modular_directed",
        "laminar": "laminar_directed",
        "optic": "laminar_directed",
        "sheets": "laminar_directed",
    }
    fam = aliases.get(fam, fam)
    if fam not in (
        "erdos_renyi_directed",
        "preferential_directed",
        "modular_directed",
        "laminar_directed",
    ):
        raise ValueError(f"unknown substrate family: {family}")

    # default sparse target ~ fly-like 5% when not ER-p driven
    if target_edges is None:
        target_edges = int(0.05 * n * (n - 1))

    emit(progress, 0.25, f"substrate: sampling {fam} N={n}")
    if fam == "erdos_renyi_directed":
        adj = _er(n, p, rng)
    elif fam == "preferential_directed":
        adj = _preferential(n, int(target_edges), rng)
    elif fam == "modular_directed":
        adj = _modular(n, int(target_edges), rng)
    else:
        adj = _laminar(n, int(target_edges), rng)

    emit(progress, 0.7, "substrate: enforcing invariants")
    dens = float(adj.sum() / max(1, n * (n - 1)))
    meta = {
        "family": fam,
        "n": n,
        "p": p if fam == "erdos_renyi_directed" else None,
        "target_edges": int(target_edges) if fam != "erdos_renyi_directed" else None,
        "seed": seed,
        "directed": True,
        "density": dens,
        "n_edges": int(adj.sum()),
    }
    if fam == "laminar_directed":
        meta["n_layers"] = int(np.clip(round(np.sqrt(n) / 2), 4, 16))
    emit(progress, 1.0, f"substrate: done · edges={meta['n_edges']} density={dens:.4f}")
    return Substrate(adj=adj, meta=meta)


def assert_invariants(sub: Substrate) -> None:
    assert sub.adj.ndim == 2 and sub.adj.shape[0] == sub.adj.shape[1]
    assert np.all(np.diag(sub.adj) == 0)
    assert sub.density < 0.10
    assert sub.density > 0.0
