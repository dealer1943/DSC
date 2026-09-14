"""F003 — differentiable type gating (STEM = soft mixture; committed = sharper)."""
from __future__ import annotations

from typing import Optional, Union

import numpy as np

from dsc import defaults


def softmax(logits: np.ndarray, temperature: Union[float, np.ndarray] = 1.0) -> np.ndarray:
    """temperature: scalar or (N,1)/(N,) broadcast against (N,T) logits."""
    z = np.asarray(logits, dtype=np.float64)
    t = np.asarray(temperature, dtype=np.float64)
    if t.ndim == 0:
        t = max(1e-6, float(t))
        z = z / t
    else:
        t = np.clip(t.reshape(-1, 1), 1e-6, None)
        z = z / t
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-12, None)


def temperatures_from_diff(differentiation: np.ndarray) -> np.ndarray:
    """Lower temperature as commitment rises → peaked type mixture."""
    d = np.clip(np.asarray(differentiation, dtype=np.float64), 0.0, 1.0)
    return defaults.STEM_TEMPERATURE * (1.0 - defaults.DIFF_TEMP_FLOOR * d)


def type_mixture(
    gate_logits: np.ndarray,
    temperature: Union[float, np.ndarray] = defaults.STEM_TEMPERATURE,
) -> np.ndarray:
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


def mixture_entropy(mixture: np.ndarray) -> np.ndarray:
    """Per-cell entropy of type mixture (nats). Low = peaked/committed."""
    m = np.clip(mixture, 1e-12, 1.0)
    return -(m * np.log(m)).sum(axis=-1)
