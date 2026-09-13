"""F003 — differentiable type gating (STEM = soft mixture)."""
from __future__ import annotations

from typing import Tuple

import numpy as np

from dsc import defaults


def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    t = max(1e-6, float(temperature))
    z = logits / t
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-12, None)


def type_mixture(gate_logits: np.ndarray, temperature: float = defaults.STEM_TEMPERATURE) -> np.ndarray:
    """(N, T) logits → (N, T) mixture weights."""
    return softmax(gate_logits, temperature)


def gated_response(
    type_responses: np.ndarray,
    mixture: np.ndarray,
) -> np.ndarray:
    """
    type_responses: (N, T, H)
    mixture: (N, T)
    returns: (N, H)
    """
    w = mixture[..., None]  # (N,T,1)
    return (type_responses * w).sum(axis=1)
