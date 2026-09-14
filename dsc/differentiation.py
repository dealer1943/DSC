"""F004 — differentiation ∈ [0,1] from utility stability + gate peak (emergence)."""
from __future__ import annotations

import numpy as np

from dsc import defaults
from dsc.cells import Population
from dsc.gating import mixture_entropy


def update_differentiation(
    pop: Population,
    prev_utility: np.ndarray,
) -> dict:
    """
    Rising commitment when utility is high/stable and gates are peaked;
    fall toward STEM when utility drops.
    """
    u = pop.utility
    prev = prev_utility
    delta = u - prev
    stable = np.abs(delta) <= defaults.DIFF_STABILITY_EPS
    high = u >= np.median(u)

    rise = defaults.DIFF_RISE * stable.astype(np.float64) * (0.5 + 0.5 * high.astype(np.float64))
    fell = delta < -defaults.DIFF_STABILITY_EPS
    fall = defaults.DIFF_FALL * fell.astype(np.float64)

    # Peak bonus: low mixture entropy → already leaning into a type
    mix = pop.mixture()
    ent = mixture_entropy(mix)
    ent_max = np.log(mix.shape[1])
    peaked = 1.0 - (ent / (ent_max + 1e-9))
    rise = rise + defaults.DIFF_PEAK_BONUS * peaked * high.astype(np.float64)

    target = pop.differentiation + rise - fall
    low = u < (u.mean() - u.std() + 1e-9)
    target = np.where(low, target * 0.92, target)

    alpha = defaults.DIFF_EMA_ALPHA
    pop.differentiation = np.clip(
        (1 - alpha) * pop.differentiation + alpha * np.clip(target, 0.0, 1.0),
        0.0,
        1.0,
    )
    labels = pop.type_labels()
    typed = sum(1 for x in labels if x != "STEM")
    return {
        "diff_mean": float(pop.differentiation.mean()),
        "diff_max": float(pop.differentiation.max()),
        "stem_frac": float((pop.differentiation < defaults.DIFF_STEM_LABEL).mean()),
        "typed_n": int(typed),
        "type_entropy_mean": float(ent.mean()),
    }
