"""F008 — coverage absorption when pruning active cells."""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from dsc import defaults
from dsc.cells import Population


def absorb_coverage(
    pop: Population,
    victim: int,
    survivors: List[int],
) -> List[int]:
    """
    Bleed victim params into top surviving responders so their basins widen.
    Returns absorber indices used.
    """
    if not survivors:
        return []
    # Prefer survivors with high activity *and* gate similarity (same niche)
    v_gate = pop.gate_logits[victim]
    scores = []
    for s in survivors:
        sim = float(
            np.dot(pop.gate_logits[s], v_gate)
            / (np.linalg.norm(pop.gate_logits[s]) * np.linalg.norm(v_gate) + 1e-9)
        )
        scores.append((sim * 0.6 + float(pop.activity[s]) * 0.4, s))
    scores.sort(reverse=True)
    top = [s for _, s in scores[: defaults.ABSORB_TOP]]
    blend = defaults.ABSORB_BLEND
    for s in top:
        pop.type_weights[s] = (1 - blend) * pop.type_weights[s] + blend * pop.type_weights[victim]
        pop.bias[s] = (1 - blend) * pop.bias[s] + blend * pop.bias[victim]
        # widen gate mixture slightly toward victim (coverage handoff)
        pop.gate_logits[s] = (1 - blend * 0.5) * pop.gate_logits[s] + (blend * 0.5) * v_gate
    return top
