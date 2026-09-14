"""F032 — small discrete state table + consolidate (opt-in).

Mint K regimes from a compact fingerprint, maintain empirical next-state
counts and per-state mean target, optionally consolidate near-duplicate
outgoing rows. Blend table prior into y_hat. Neutral connectome language only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from dsc import defaults


def fingerprint_from_pop(pop, y_hat: float, err: float = 0.0) -> np.ndarray:
    mix = pop.mixture().mean(axis=0)
    util = float(pop.utility.mean())
    act = float(pop.activity.mean())
    stem = float((pop.differentiation < defaults.DIFF_STEM_LABEL).mean())
    diff = float(pop.differentiation.mean())
    return np.concatenate(
        [np.array([y_hat, err, util, act, stem, diff], dtype=np.float64), mix.astype(np.float64)]
    )


@dataclass
class StateTable:
    k: int
    mix: float = 0.25
    consolidate: bool = True
    l1_merge: float = 0.25
    # online quantizer (running mean/std + PC1 from reservoir)
    _mu: Optional[np.ndarray] = None
    _m2: Optional[np.ndarray] = None
    _n: int = 0
    _eig: Optional[np.ndarray] = None
    _edges: Optional[np.ndarray] = None
    _score_buf: list = field(default_factory=list)
    _feat_buf: list = field(default_factory=list)
    counts: Optional[np.ndarray] = None
    sum_y: Optional[np.ndarray] = None
    n_y: Optional[np.ndarray] = None
    last_s: Optional[int] = None
    k_eff: int = 0
    remap: Optional[np.ndarray] = None  # raw->eff after consolidate
    updates: int = 0

    def __post_init__(self) -> None:
        k = int(self.k)
        self.k = k
        self.k_eff = k
        self.counts = np.ones((k, k), dtype=np.float64)  # Laplace
        self.sum_y = np.zeros(k, dtype=np.float64)
        self.n_y = np.zeros(k, dtype=np.float64)
        self.remap = np.arange(k, dtype=np.int64)

    def _update_moments(self, feat: np.ndarray) -> None:
        self._n += 1
        if self._mu is None:
            self._mu = feat.copy()
            self._m2 = np.zeros_like(feat)
        else:
            d = feat - self._mu
            self._mu = self._mu + d / self._n
            self._m2 = self._m2 + d * (feat - self._mu)

    def _maybe_fit_bins(self) -> None:
        # refit quantile edges periodically from reservoir
        if len(self._score_buf) < max(20, 4 * self.k):
            return
        scores = np.asarray(self._score_buf[-400:], dtype=np.float64)
        qs = np.linspace(0.0, 1.0, self.k + 1)
        edges = np.quantile(scores, qs)
        for i in range(1, len(edges)):
            if edges[i] <= edges[i - 1]:
                edges[i] = edges[i - 1] + 1e-9
        self._edges = edges

    def _score(self, feat: np.ndarray) -> float:
        assert self._mu is not None and self._m2 is not None
        sd = np.sqrt(self._m2 / max(self._n - 1, 1))
        sd = np.where(sd < 1e-9, 1.0, sd)
        z = (feat - self._mu) / sd
        if self._eig is None:
            # bootstrap eig from buffer
            if len(self._feat_buf) >= max(16, self.k * 2):
                X = np.stack(self._feat_buf[-200:], axis=0)
                sd_x = X.std(axis=0)
                sd_x = np.where(sd_x < 1e-9, 1.0, sd_x)
                Z = (X - X.mean(axis=0)) / sd_x
                C = np.cov(Z, rowvar=False)
                w, V = np.linalg.eigh(C)
                self._eig = V[:, -1]
            else:
                # fallback: first dim
                return float(z[0])
        return float(z @ self._eig)

    def _assign(self, score: float) -> int:
        if self._edges is None:
            # cold: coarse hash into k bins by tanh
            u = 0.5 * (np.tanh(score) + 1.0)
            return int(np.clip(u * self.k, 0, self.k - 1))
        s = int(np.clip(np.digitize(score, self._edges[1:-1], right=False), 0, self.k - 1))
        return int(self.remap[s])

    def _consolidate(self) -> None:
        if not self.consolidate or self.k < 10:
            return
        probs = self.counts / self.counts.sum(axis=1, keepdims=True)
        modal = probs.argmax(axis=1)
        parent = list(range(self.k))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for i in range(self.k):
            for j in range(i + 1, self.k):
                if modal[i] != modal[j]:
                    continue
                if float(np.abs(probs[i] - probs[j]).sum()) <= self.l1_merge:
                    union(i, j)
        roots = [find(i) for i in range(self.k)]
        uniq = sorted(set(roots))
        remap = {r: idx for idx, r in enumerate(uniq)}
        self.remap = np.array([remap[find(i)] for i in range(self.k)], dtype=np.int64)
        self.k_eff = len(uniq)

    def prior_y(self, s: int) -> float:
        # expected next-state mean target under P(s'|s)
        row = self.counts[s]
        p = row / row.sum()
        # mean y of destination states (fallback 0)
        my = np.divide(self.sum_y, np.maximum(self.n_y, 1.0))
        return float(p @ my)

    def observe_and_blend(self, pop, y_hat: float, err: float = 0.0) -> float:
        feat = fingerprint_from_pop(pop, y_hat, err=err)
        self._update_moments(feat)
        self._feat_buf.append(feat)
        if len(self._feat_buf) > 500:
            self._feat_buf = self._feat_buf[-500:]
        score = self._score(feat)
        self._score_buf.append(score)
        if len(self._score_buf) > 500:
            self._score_buf = self._score_buf[-500:]
        if self._n % 32 == 0:
            self._maybe_fit_bins()
        if self._n % 64 == 0 and self.consolidate:
            self._consolidate()
        s = self._assign(score)
        # use raw index into counts (k x k); remap only for reporting k_eff
        # keep transitions in raw k for stability
        prior = self.prior_y(s)
        mix = float(self.mix)
        blended = (1.0 - mix) * float(y_hat) + mix * prior
        if not np.isfinite(blended):
            blended = float(y_hat)
        self.last_s = s
        self.updates += 1
        return float(blended)

    def update_outcome(self, y: float) -> None:
        if self.last_s is None:
            return
        s = int(self.last_s)
        self.sum_y[s] += float(y)
        self.n_y[s] += 1.0
        # transition: need previous state — store _prev
        prev = getattr(self, "_prev_s", None)
        if prev is not None:
            self.counts[int(prev), s] += 1.0
        self._prev_s = s

    def report(self) -> dict[str, Any]:
        return {
            "k": self.k,
            "k_eff": int(self.k_eff),
            "mix": float(self.mix),
            "consolidate": bool(self.consolidate),
            "updates": int(self.updates),
            "occupied": int((self.n_y > 0).sum()) if self.n_y is not None else 0,
        }


def maybe_make_state_table() -> Optional[StateTable]:
    k = int(getattr(defaults, "STATE_TABLE_K", 0) or 0)
    if k <= 0:
        return None
    return StateTable(
        k=k,
        mix=float(getattr(defaults, "STATE_TABLE_MIX", 0.25)),
        consolidate=bool(getattr(defaults, "STATE_TABLE_CONSOLIDATE", True)),
        l1_merge=float(getattr(defaults, "STATE_TABLE_L1_MERGE", 0.25)),
    )
