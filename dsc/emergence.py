"""S006 — post-evolve / explicit emergence pressure for visible types."""
from __future__ import annotations

from typing import Dict, List

import numpy as np

from dsc import defaults
from dsc.cells import Population


def emerge_elites(pop: Population, top_k: Optional[int] = None) -> Dict[str, float]:
    """
    After evolution: boost differentiation on elites and sharpen their gate
    logits toward the current winner so UI labels leave STEM.
    """
    k = int(top_k or defaults.EVOLVE_TOP_K)
    k = min(k, pop.n)
    order = np.argsort(-pop.utility)
    elites = order[:k]

    boost = defaults.EMERGE_ELITE_BOOST
    pop.differentiation[elites] = np.clip(pop.differentiation[elites] + boost, 0.0, 1.0)

    sharp = defaults.EMERGE_GATE_SHARPEN
    winners = pop.gate_logits[elites].argmax(axis=1)
    for row, w in zip(elites, winners):
        # amplify winning logit, mildly suppress others
        logits = pop.gate_logits[row]
        peak = float(logits[w])
        logits = logits - sharp * 0.15 * (logits - logits.mean())
        logits[w] = peak + sharp
        pop.gate_logits[row] = logits

    labels = pop.type_labels()
    typed = sum(1 for x in labels if x != "STEM")
    return {
        "emerged_elites": float(k),
        "stem_frac": float((pop.differentiation < defaults.DIFF_STEM_LABEL).mean()),
        "typed_n": float(typed),
        "diff_mean": float(pop.differentiation.mean()),
    }


def type_histogram(pop: Population) -> Dict[str, int]:
    hist: Dict[str, int] = {}
    for lab in pop.type_labels():
        hist[lab] = hist.get(lab, 0) + 1
    return hist


def histogram_line(pop: Population) -> str:
    hist = type_histogram(pop)
    parts = [f"{k}:{v}" for k, v in sorted(hist.items(), key=lambda kv: (-kv[1], kv[0]))]
    return "types " + " ".join(parts)
