"""F004 light — differentiation ∈ [0,1] from utility stability."""
from __future__ import annotations

import numpy as np

from dsc import defaults
from dsc.cells import Population


def update_differentiation(
    pop: Population,
    prev_utility: np.ndarray,
) -> dict:
    """
    Rising commitment when utility is high and stable; fall toward STEM when it drops.
    `prev_utility` is the per-cell utility vector from *before* the latest EMA update
    (or a copy taken before update_utilities).
    """
    u = pop.utility
    prev = prev_utility
    delta = u - prev
    stable = np.abs(delta) <= defaults.DIFF_STABILITY_EPS
    high = u >= np.median(u)

    rise = defaults.DIFF_RISE * stable.astype(np.float64) * (0.5 + 0.5 * high.astype(np.float64))
    # fall when utility decreased meaningfully
    fell = delta < -defaults.DIFF_STABILITY_EPS
    fall = defaults.DIFF_FALL * fell.astype(np.float64)

    target = pop.differentiation + rise - fall
    # also gently pull unused (very low utility) cells toward STEM
    low = u < (u.mean() - u.std() + 1e-9)
    target = np.where(low, target * 0.9, target)

    alpha = defaults.DIFF_EMA_ALPHA
    pop.differentiation = np.clip(
        (1 - alpha) * pop.differentiation + alpha * np.clip(target, 0.0, 1.0),
        0.0,
        1.0,
    )
    return {
        "diff_mean": float(pop.differentiation.mean()),
        "diff_max": float(pop.differentiation.max()),
        "stem_frac": float((pop.differentiation < defaults.DIFF_STEM_LABEL).mean()),
    }
