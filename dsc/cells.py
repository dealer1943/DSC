"""F002 — state cell population (STEM-initialized)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from dsc import defaults
from dsc.gating import gated_response, type_mixture
from dsc.progress import ProgressCb, emit
from dsc.substrate import Substrate


@dataclass
class Population:
    """One cell per substrate node; all start STEM (soft type mixture)."""

    gate_logits: np.ndarray       # (N, T)
    type_weights: np.ndarray      # (N, T, H) — per-type local kernels
    bias: np.ndarray              # (N, H)
    readout: np.ndarray           # (H,) system readout
    utility: np.ndarray           # (N,) EMA utility
    age: np.ndarray               # (N,) int
    differentiation: np.ndarray   # (N,) 0=plastic STEM … 1=committed (F004)
    activity: np.ndarray          # (N,) last activity magnitude
    hidden: np.ndarray            # (N, H) last hidden state
    fail_streak: np.ndarray       # (N,) F007 sustained low-utility count

    @property
    def n(self) -> int:
        return int(self.gate_logits.shape[0])

    @property
    def n_types(self) -> int:
        return int(self.gate_logits.shape[1])

    def mixture(self) -> np.ndarray:
        return type_mixture(self.gate_logits)

    def dominant_type_indices(self) -> np.ndarray:
        return self.mixture().argmax(axis=1)

    def type_labels(self) -> list:
        idx = self.dominant_type_indices()
        # Still STEM-labeled until differentiation rises (F004); for UI show mixture winner as soft type
        names = defaults.TYPE_NAMES
        labels = []
        mix = self.mixture()
        for i, ti in enumerate(idx):
            if self.differentiation[i] < defaults.DIFF_STEM_LABEL:
                labels.append("STEM")
            else:
                labels.append(names[int(ti)])
        return labels


def init_population(
    sub: Substrate,
    seed: int = defaults.SEED,
    progress: Optional[ProgressCb] = None,
) -> Population:
    emit(progress, 0.1, "cells: allocating STEM population")
    rng = np.random.default_rng(seed + 7)
    n = sub.n
    t = len(defaults.TYPE_NAMES)
    h = defaults.HIDDEN
    # near-uniform gates → STEM
    gate = rng.normal(0.0, 0.05, size=(n, t))
    type_w = rng.normal(0.0, 0.1, size=(n, t, h))
    bias = rng.normal(0.0, 0.05, size=(n, h))
    readout = rng.normal(0.0, 0.1, size=(h,))
    emit(progress, 0.8, "cells: STEM init complete")
    pop = Population(
        gate_logits=gate.astype(np.float64),
        type_weights=type_w.astype(np.float64),
        bias=bias.astype(np.float64),
        readout=readout.astype(np.float64),
        utility=np.zeros(n, dtype=np.float64),
        age=np.zeros(n, dtype=np.int32),
        differentiation=np.zeros(n, dtype=np.float64),
        activity=np.zeros(n, dtype=np.float64),
        hidden=np.zeros((n, h), dtype=np.float64),
        fail_streak=np.zeros(n, dtype=np.int32),
    )
    emit(progress, 1.0, f"cells: n={n} types={t} hidden={h}")
    return pop


def step_population(
    pop: Population,
    sub: Substrate,
    inp: float,
) -> float:
    """
    One message-passing + gated type step.
    Returns scalar system readout prediction.
    """
    n, h = pop.n, defaults.HIDDEN
    t = pop.n_types
    # inject input into all cells lightly + neighbor mix
    inject = np.tanh(inp) * 0.5
    A = sub.adj.astype(np.float64)
    h = np.nan_to_num(pop.hidden, nan=0.0, posinf=0.0, neginf=0.0)
    messages = np.einsum("ji,jh->ih", A, h)  # gather from sources (avoids spurious np2 matmul warns)
    deg = np.clip(A.sum(axis=0), 1.0, None)[:, None]
    messages = messages / deg
    base = np.tanh(np.nan_to_num(messages + pop.bias + inject))

    # per-type responses
    type_resp = np.tanh(pop.type_weights * base[:, None, :] + pop.gate_logits[:, :, None] * 0.05)
    mix = pop.mixture()
    hidden = gated_response(type_resp, mix)
    hidden = np.nan_to_num(hidden, nan=0.0, posinf=0.0, neginf=0.0)
    pop.hidden = hidden
    pop.activity = np.linalg.norm(hidden, axis=1)
    pop.age += 1
    y_hat = float(np.tanh(hidden.mean(axis=0) @ pop.readout))
    if not np.isfinite(y_hat):
        y_hat = 0.0
    return y_hat
