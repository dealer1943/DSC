"""F001 — synthetic sparse directed substrate."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from dsc import defaults
from dsc.progress import ProgressCb, emit


@dataclass
class Substrate:
    adj: np.ndarray          # (N,N) uint8, directed, no self-loops
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


def generate_substrate(
    n: int = defaults.N_NODES,
    p: float = defaults.EDGE_PROB,
    seed: int = defaults.SEED,
    progress: Optional[ProgressCb] = None,
) -> Substrate:
    emit(progress, 0.05, "substrate: seeding RNG")
    rng = np.random.default_rng(seed)
    emit(progress, 0.25, f"substrate: sampling ER directed N={n} p={p}")
    adj = (rng.random((n, n)) < p).astype(np.uint8)
    np.fill_diagonal(adj, 0)
    emit(progress, 0.7, "substrate: enforcing invariants")
    dens = float(adj.sum() / (n * (n - 1)))
    if dens >= 0.10:
        # rare with p=0.08; thin randomly if needed
        edges = np.argwhere(adj)
        keep = int(0.09 * n * (n - 1))
        if len(edges) > keep:
            pick = rng.choice(len(edges), size=keep, replace=False)
            new = np.zeros_like(adj)
            for i, j in edges[pick]:
                new[i, j] = 1
            adj = new
            dens = float(adj.sum() / (n * (n - 1)))
    meta = {
        "family": defaults.GRAPH_FAMILY,
        "n": n,
        "p": p,
        "seed": seed,
        "directed": True,
        "density": dens,
        "n_edges": int(adj.sum()),
    }
    emit(progress, 1.0, f"substrate: done · edges={meta['n_edges']} density={dens:.4f}")
    return Substrate(adj=adj, meta=meta)


def assert_invariants(sub: Substrate) -> None:
    assert sub.adj.ndim == 2 and sub.adj.shape[0] == sub.adj.shape[1]
    assert np.all(np.diag(sub.adj) == 0)
    assert sub.density < 0.10
    assert sub.density > 0.0
