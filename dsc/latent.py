"""F007 — dormant/latent retention pool for pruned cells."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from dsc import defaults
from dsc.cells import Population


@dataclass
class LatentEntry:
    gate_logits: np.ndarray
    type_weights: np.ndarray
    bias: np.ndarray
    utility: float
    differentiation: float
    activity: float
    hidden: np.ndarray
    source_id: int
    age_at_prune: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "source_id": int(self.source_id),
            "age_at_prune": int(self.age_at_prune),
            "utility": float(self.utility),
            "differentiation": float(self.differentiation),
        }


@dataclass
class LatentPool:
    entries: List[LatentEntry] = field(default_factory=list)
    max_size: int = defaults.LATENT_POOL_MAX

    def __len__(self) -> int:
        return len(self.entries)

    def push_from_pop(self, pop: Population, idx: int) -> LatentEntry:
        e = LatentEntry(
            gate_logits=pop.gate_logits[idx].copy(),
            type_weights=pop.type_weights[idx].copy(),
            bias=pop.bias[idx].copy(),
            utility=float(pop.utility[idx]),
            differentiation=float(pop.differentiation[idx]),
            activity=float(pop.activity[idx]),
            hidden=pop.hidden[idx].copy(),
            source_id=int(idx),
            age_at_prune=int(pop.age[idx]),
        )
        self.entries.append(e)
        # FIFO if over capacity (oldest forgotten last — still better than hard delete of all)
        while len(self.entries) > self.max_size:
            self.entries.pop(0)
        return e

    def pop_best(self) -> Optional[LatentEntry]:
        if not self.entries:
            return None
        i = int(np.argmax([e.utility for e in self.entries]))
        return self.entries.pop(i)

    def install(self, pop: Population, idx: int, entry: LatentEntry) -> None:
        pop.gate_logits[idx] = entry.gate_logits.copy()
        pop.type_weights[idx] = entry.type_weights.copy()
        pop.bias[idx] = entry.bias.copy()
        pop.hidden[idx] = entry.hidden.copy()
        pop.utility[idx] = entry.utility * 0.75  # slightly cooled
        pop.differentiation[idx] = min(entry.differentiation, 0.5)
        pop.activity[idx] = entry.activity
        pop.age[idx] = 0

    def copy(self) -> "LatentPool":
        out = LatentPool(max_size=self.max_size)
        for e in self.entries:
            out.entries.append(
                LatentEntry(
                    gate_logits=e.gate_logits.copy(),
                    type_weights=e.type_weights.copy(),
                    bias=e.bias.copy(),
                    utility=e.utility,
                    differentiation=e.differentiation,
                    activity=e.activity,
                    hidden=e.hidden.copy(),
                    source_id=e.source_id,
                    age_at_prune=e.age_at_prune,
                )
            )
        return out

    def to_npz(self) -> Dict[str, np.ndarray]:
        if not self.entries:
            return {
                "latent_count": np.array([0], dtype=np.int32),
            }
        return {
            "latent_count": np.array([len(self.entries)], dtype=np.int32),
            "latent_gate_logits": np.stack([e.gate_logits for e in self.entries]),
            "latent_type_weights": np.stack([e.type_weights for e in self.entries]),
            "latent_bias": np.stack([e.bias for e in self.entries]),
            "latent_hidden": np.stack([e.hidden for e in self.entries]),
            "latent_utility": np.array([e.utility for e in self.entries], dtype=np.float64),
            "latent_differentiation": np.array(
                [e.differentiation for e in self.entries], dtype=np.float64
            ),
            "latent_activity": np.array([e.activity for e in self.entries], dtype=np.float64),
            "latent_source_id": np.array([e.source_id for e in self.entries], dtype=np.int32),
            "latent_age": np.array([e.age_at_prune for e in self.entries], dtype=np.int32),
        }

    @classmethod
    def from_npz(cls, data: Any) -> "LatentPool":
        pool = cls()
        if "latent_count" not in data:
            return pool
        n = int(np.asarray(data["latent_count"]).reshape(-1)[0])
        if n <= 0:
            return pool
        for i in range(n):
            pool.entries.append(
                LatentEntry(
                    gate_logits=np.asarray(data["latent_gate_logits"][i]).copy(),
                    type_weights=np.asarray(data["latent_type_weights"][i]).copy(),
                    bias=np.asarray(data["latent_bias"][i]).copy(),
                    hidden=np.asarray(data["latent_hidden"][i]).copy(),
                    utility=float(data["latent_utility"][i]),
                    differentiation=float(data["latent_differentiation"][i]),
                    activity=float(data["latent_activity"][i]),
                    source_id=int(data["latent_source_id"][i]),
                    age_at_prune=int(data["latent_age"][i]),
                )
            )
        return pool
