"""F010 — temporal task harness (lag-1 scalar prediction)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from dsc import defaults
from dsc.progress import ProgressCb, emit


@dataclass
class HarnessState:
    name: str
    lag: int
    noise: float
    seed: int
    t: int
    history: list  # recent targets
    last_x: float
    last_y: float
    last_y_hat: float
    last_err: float
    rng_state: Optional[dict] = None


class TemporalHarness:
    """Reproducible temporal objective: predict next scalar in a smooth walk."""

    def __init__(
        self,
        seed: int = defaults.SEED,
        lag: int = defaults.TASK_LAG,
        noise: float = defaults.TASK_NOISE,
    ):
        self.seed = seed
        self.lag = lag
        self.noise = noise
        self.rng = np.random.default_rng(seed + 99)
        self.t = 0
        self._x = 0.0
        self.history = []
        self.last_y = 0.0
        self.last_y_hat = 0.0
        self.last_err = 0.0

    def reset(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.seed = seed
        self.rng = np.random.default_rng(self.seed + 99)
        self.t = 0
        self._x = 0.0
        self.history = []
        self.last_y = self.last_y_hat = self.last_err = 0.0

    def next_input_target(self) -> Tuple[float, float]:
        """Advance latent walk; return (x_t, y_t) with y = future value at lag."""
        # Ornstein-ish walk
        self._x = 0.92 * self._x + self.noise * float(self.rng.normal())
        self.history.append(self._x)
        self.t += 1
        x_t = self._x
        # target is value lag steps ahead — for lag=1 we peek one step then roll back feel:
        # simpler: y_t = x_t (predict current from previous hidden) using previous x as input
        if len(self.history) == 1:
            return 0.0, x_t
        x_in = self.history[-2]
        y = x_t
        return float(x_in), float(y)

    def score(self, y_hat: float, y: float) -> float:
        err = (y_hat - y) ** 2
        self.last_y, self.last_y_hat, self.last_err = y, y_hat, float(err)
        return float(err)

    def state_dict(self) -> dict:
        return {
            "name": defaults.TASK_NAME,
            "lag": self.lag,
            "noise": self.noise,
            "seed": self.seed,
            "t": self.t,
            "x": self._x,
            "history": self.history[-64:],
            "last_y": self.last_y,
            "last_y_hat": self.last_y_hat,
            "last_err": self.last_err,
        }

    def load_state(self, d: dict) -> None:
        self.lag = int(d.get("lag", self.lag))
        self.noise = float(d.get("noise", self.noise))
        self.seed = int(d.get("seed", self.seed))
        self.t = int(d.get("t", 0))
        self._x = float(d.get("x", 0.0))
        self.history = list(d.get("history") or [])
        self.last_y = float(d.get("last_y", 0.0))
        self.last_y_hat = float(d.get("last_y_hat", 0.0))
        self.last_err = float(d.get("last_err", 0.0))
        self.rng = np.random.default_rng(self.seed + 99 + self.t)


def build_harness(progress: Optional[ProgressCb] = None) -> TemporalHarness:
    emit(progress, 0.5, f"harness: {defaults.TASK_NAME}")
    h = TemporalHarness()
    emit(progress, 1.0, "harness: ready")
    return h
