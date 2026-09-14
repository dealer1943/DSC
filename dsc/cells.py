"""F002 — state cell population (STEM-initialized)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from dsc import defaults
from dsc.gating import gated_response, type_mixture, temperatures_from_diff
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
        return type_mixture(self.gate_logits, temperatures_from_diff(self.differentiation))

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
    use_sparse = bool(getattr(defaults, "SPARSE_GATHER", False)) and float(sub.density) <= float(
        getattr(defaults, "SPARSE_DENSITY_MAX", 0.085)
    )
    hub = bool(getattr(defaults, "HUB_AWARE", False))
    in_deg = np.clip(A.sum(axis=0), 1.0, None)
    out_deg = np.clip(A.sum(axis=1), 1.0, None)
    nearest_exact = bool(getattr(defaults, "NEAREST_EXACT", False))
    if nearest_exact:
        # R003: exact nearest in-neighbor hidden (no degree-mean soup).
        src, dst = sub.edge_index()
        k = max(1, int(getattr(defaults, "NEAREST_K", 1)))
        rule = str(getattr(defaults, "NEAREST_RULE", "sheet"))
        messages = np.zeros_like(h)
        if len(src) == 0:
            messages = h.copy()
        elif k == 1:
            best = np.full(n, -1, dtype=np.int32)
            best_score = np.full(n, np.inf, dtype=np.float64)
            for s, d in zip(src.tolist(), dst.tolist()):
                if rule == "inweight":
                    score = -float(A[s, d])
                else:
                    score = float(abs(int(s) - int(d)))
                if score < best_score[d]:
                    best_score[d] = score
                    best[d] = int(s)
            has = best >= 0
            messages[has] = h[best[has]]
            messages[~has] = h[~has]
        else:
            # mean of up to k nearest exact peers (still local, not full degree)
            buckets = {i: [] for i in range(n)}
            for s, d in zip(src.tolist(), dst.tolist()):
                if rule == "inweight":
                    score = -float(A[s, d])
                else:
                    score = float(abs(int(s) - int(d)))
                buckets[int(d)].append((score, int(s)))
            for i in range(n):
                peers = buckets[i]
                if not peers:
                    messages[i] = h[i]
                    continue
                peers.sort(key=lambda t: t[0])
                pick = [s for _, s in peers[:k]]
                messages[i] = h[pick].mean(axis=0)
    elif use_sparse:
        src, dst = sub.edge_index()  # A[src,dst]=1 ⇒ src→dst; einsum used A[j,i]=src→dst
        # align with einsum "ji": j=src, i=dst
        messages = np.zeros_like(h)
        if len(src):
            if hub:
                exp = float(getattr(defaults, "HUB_OUT_EXP", 0.5))
                w = (out_deg[src] ** exp) ** -1.0
                np.add.at(messages, dst, h[src] * w[:, None])
                messages = messages / np.log1p(in_deg)[:, None]
            else:
                np.add.at(messages, dst, h[src])
                messages = messages / in_deg[:, None]
    elif hub:
        exp = float(getattr(defaults, "HUB_OUT_EXP", 0.5))
        A_eff = A / (out_deg[:, None] ** exp)
        messages = np.einsum("ji,jh->ih", A_eff, h)
        messages = messages / np.log1p(in_deg)[:, None]
    else:
        messages = np.einsum("ji,jh->ih", A, h)
        messages = messages / in_deg[:, None]

    # F029 bilayer: fold sheet — each cell also sees an aligned "one layer up" state.
    # Layers from node index only (procedural); works on any adjacency family.
    if bool(getattr(defaults, "BILAYER", False)):
        n_layers = int(np.clip(round(np.sqrt(n) / 2), 4, 16))
        chunks = np.array_split(np.arange(n), n_layers)
        layer_of = np.empty(n, dtype=np.int32)
        pos_in_layer = np.empty(n, dtype=np.float64)
        for li, idxs in enumerate(chunks):
            layer_of[idxs] = li
            m = max(1, len(idxs))
            pos_in_layer[idxs] = np.arange(len(idxs)) / m
        # partner in layer+1 at same fractional position (fold contact)
        elevated = np.zeros_like(h)
        for li, idxs in enumerate(chunks[:-1]):
            above = chunks[li + 1]
            if len(above) == 0:
                continue
            for i in idxs:
                j = int(pos_in_layer[i] * len(above))
                j = min(j, len(above) - 1)
                elevated[i] = h[above[j]]
        # top sheet: wrap to layer 0 (fold over) — still procedural, not atlas
        top = chunks[-1]
        bottom = chunks[0]
        if len(top) and len(bottom):
            for i in top:
                j = int(pos_in_layer[i] * len(bottom))
                j = min(j, len(bottom) - 1)
                elevated[i] = h[bottom[j]]
        bilayer_mix = float(getattr(defaults, "BILAYER_MIX", 0.35))
        # EMA channel on population (creates lasting 2nd config)
        prev = getattr(pop, "elevated", None)
        alpha = float(getattr(defaults, "BILAYER_EMA", 0.25))
        if prev is None or getattr(prev, "shape", None) != elevated.shape:
            pop.elevated = elevated.copy()
        else:
            pop.elevated = (1.0 - alpha) * prev + alpha * elevated
        messages = messages + bilayer_mix * pop.elevated


    # F030 talk board: shared who's-talking presence + edge-masked glance.
    # Build once from prev-tick activity (shared buffer). Each cell only
    # mixes hidden from in-neighbors whose talk bit is on — O(edges), not O(N²).
    if bool(getattr(defaults, "TALK_BOARD", False)):
        thresh = float(getattr(defaults, "TALK_THRESH", 0.05))
        talking = np.nan_to_num(pop.activity) > thresh
        pop.talk_board = talking
        pop.talk_packed = np.packbits(talking.astype(np.uint8))
        talk_frac = float(talking.mean()) if n else 0.0
        inject = inject + float(getattr(defaults, "TALK_GLOBAL", 0.05)) * np.tanh(talk_frac * 3.0)
        talk_h = h * talking.astype(np.float64)[:, None]
        if use_sparse:
            src, dst = sub.edge_index()
            glance = np.zeros_like(h)
            talk_in = np.zeros(n, dtype=np.float64)
            if len(src):
                m = talking[src]
                if np.any(m):
                    s_m, d_m = src[m], dst[m]
                    np.add.at(glance, d_m, talk_h[s_m])
                    np.add.at(talk_in, d_m, 1.0)
            glance = glance / np.clip(talk_in, 1.0, None)[:, None]
        else:
            # A[j, i] = 1 ⇒ j→i (matches einsum "ji" used above)
            talk_in = (A * talking.astype(np.float64)[:, None]).sum(axis=0)
            glance = np.einsum("ji,jh->ih", A, talk_h)
            glance = glance / np.clip(talk_in, 1.0, None)[:, None]
        messages = messages + float(getattr(defaults, "TALK_MIX", 0.30)) * glance

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
