"""F008 / F024 — coverage absorption when pruning active cells."""
from __future__ import annotations

from typing import List, Optional

import numpy as np

from dsc import defaults
from dsc.cells import Population
from dsc.substrate import Substrate


def absorb_coverage(
    pop: Population,
    victim: int,
    survivors: List[int],
    sub: Optional[Substrate] = None,
) -> List[int]:
    """
    Bleed victim params into top surviving responders so their basins widen.

    F024: on skewed graphs prefer niche-similar *neighbors* and mildly penalize
    extreme hubs so coverage does not collapse into a few high-degree cells.
    """
    if not survivors:
        return []
    v_gate = pop.gate_logits[victim]
    v_norm = float(np.linalg.norm(v_gate) + 1e-9)

    # graph neighborhood bonus
    nbr: set[int] = set()
    hub_pen = np.zeros(pop.n, dtype=np.float64)
    if sub is not None:
        A = sub.adj
        # undirected neighborhood of victim
        nbr = set(np.flatnonzero(A[victim]).tolist()) | set(np.flatnonzero(A[:, victim]).tolist())
        out_deg = A.sum(axis=1).astype(np.float64)
        # penalty grows for top-heavy out-degree
        med = float(np.median(out_deg[out_deg > 0])) if np.any(out_deg > 0) else 1.0
        hub_pen = np.clip((out_deg - med) / (med + 1e-9), 0.0, 3.0) * 0.15

    scores = []
    for s in survivors:
        sim = float(np.dot(pop.gate_logits[s], v_gate) / (np.linalg.norm(pop.gate_logits[s]) * v_norm + 1e-9))
        act = float(pop.activity[s])
        score = sim * 0.55 + act * 0.35
        if s in nbr:
            score += 0.25
        score -= float(hub_pen[s])
        scores.append((score, s))
    scores.sort(reverse=True)
    top_n = int(getattr(defaults, "ABSORB_TOP", 3))
    # under skew, absorb into slightly more survivors
    if sub is not None and float(sub.density) < 0.06:
        top_n = max(top_n, min(5, len(survivors)))
    top = [s for _, s in scores[:top_n]]
    blend = float(defaults.ABSORB_BLEND)
    # slightly stronger handoff when neighbors absorb
    for s in top:
        b = blend * (1.15 if s in nbr else 1.0)
        b = min(0.6, b)
        pop.type_weights[s] = (1 - b) * pop.type_weights[s] + b * pop.type_weights[victim]
        pop.bias[s] = (1 - b) * pop.bias[s] + b * pop.bias[victim]
        pop.gate_logits[s] = (1 - b * 0.5) * pop.gate_logits[s] + (b * 0.5) * v_gate
    return top
