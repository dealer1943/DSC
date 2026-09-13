"""F006 evolution loop + F009 light snapshot/rollback."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from dsc import defaults
from dsc.cells import Population
from dsc.harness import TemporalHarness
from dsc.substrate import Substrate


@dataclass
class PopSnapshot:
    """In-memory last-good (F009)."""

    gate_logits: np.ndarray
    type_weights: np.ndarray
    bias: np.ndarray
    readout: np.ndarray
    utility: np.ndarray
    age: np.ndarray
    differentiation: np.ndarray
    activity: np.ndarray
    hidden: np.ndarray
    harness_state: Dict[str, Any]
    signal_hist: Dict[str, List[float]] = field(default_factory=dict)
    note: str = ""

    @classmethod
    def capture(
        cls,
        pop: Population,
        harness: TemporalHarness,
        signal_hist: Optional[Dict[str, List[float]]] = None,
        note: str = "",
    ) -> "PopSnapshot":
        return cls(
            gate_logits=pop.gate_logits.copy(),
            type_weights=pop.type_weights.copy(),
            bias=pop.bias.copy(),
            readout=pop.readout.copy(),
            utility=pop.utility.copy(),
            age=pop.age.copy(),
            differentiation=pop.differentiation.copy(),
            activity=pop.activity.copy(),
            hidden=pop.hidden.copy(),
            harness_state=deepcopy(harness.state_dict()),
            signal_hist={k: list(v) for k, v in (signal_hist or {}).items()},
            note=note,
        )

    def restore(self, pop: Population, harness: TemporalHarness) -> None:
        pop.gate_logits[...] = self.gate_logits
        pop.type_weights[...] = self.type_weights
        pop.bias[...] = self.bias
        pop.readout[...] = self.readout
        pop.utility[...] = self.utility
        pop.age[...] = self.age
        pop.differentiation[...] = self.differentiation
        pop.activity[...] = self.activity
        pop.hidden[...] = self.hidden
        harness.load_state(deepcopy(self.harness_state))


@dataclass
class CycleReport:
    kept: List[int]
    replaced: List[int]
    cloned_from: List[int]
    type_nudged: List[int]
    util_before: float
    util_after: float
    activity_before: float
    activity_after: float
    rolled_back: bool = False
    fail_reason: str = ""

    def lines(self, cycle_i: int) -> List[str]:
        if self.rolled_back:
            return [
                f"evolve[{cycle_i}] ROLLBACK — {self.fail_reason}",
                f"  util {self.util_before:.4f}→{self.util_after:.4f}  "
                f"act {self.activity_before:.4f}→{self.activity_after:.4f}",
            ]
        return [
            f"evolve[{cycle_i}] keep={len(self.kept)} replace={len(self.replaced)} "
            f"type_nudge={len(self.type_nudged)}",
            f"  util {self.util_before:.4f}→{self.util_after:.4f}  "
            f"act {self.activity_before:.4f}→{self.activity_after:.4f}",
        ]


def _finite_pop(pop: Population) -> bool:
    arrays = (
        pop.gate_logits,
        pop.type_weights,
        pop.bias,
        pop.readout,
        pop.utility,
        pop.differentiation,
        pop.activity,
        pop.hidden,
    )
    return all(np.isfinite(a).all() for a in arrays)


def check_stability(
    pop: Population,
    util_before: float,
    activity_before: float,
) -> Tuple[bool, str]:
    """F009 light gates. True = ok."""
    if not _finite_pop(pop):
        return False, "NaN/Inf in population tensors"
    util_after = float(pop.utility.mean())
    act_after = float(np.mean(np.abs(pop.activity)))
    if act_after < defaults.ROLLBACK_FOOTPRINT_MIN:
        return False, f"footprint collapse act={act_after:.4f}"
    if activity_before > 1e-6 and act_after < defaults.ROLLBACK_FOOTPRINT_REL * activity_before:
        return False, (
            f"footprint cliff act {activity_before:.4f}→{act_after:.4f} "
            f"(<{defaults.ROLLBACK_FOOTPRINT_REL:.0%} pre)"
        )
    # utility cliff: only if we had positive mean utility to protect
    if util_before > 1e-6:
        if util_after < util_before * (1.0 - defaults.ROLLBACK_UTIL_CLIFF):
            return False, (
                f"utility cliff {util_before:.4f}→{util_after:.4f} "
                f"(>{defaults.ROLLBACK_UTIL_CLIFF:.0%} drop)"
            )
    return True, ""


def _mutate_clone(pop: Population, idx: int, rng: np.random.Generator) -> bool:
    """Perturb params at idx. Returns True if type logits were nudged."""
    sig = defaults.EVOLVE_MUTATE_SIGMA
    pop.type_weights[idx] += rng.normal(0.0, sig, size=pop.type_weights[idx].shape)
    pop.bias[idx] += rng.normal(0.0, sig, size=pop.bias[idx].shape)
    pop.gate_logits[idx] += rng.normal(0.0, sig * 0.5, size=pop.gate_logits[idx].shape)
    nudged = False
    if rng.random() < defaults.EVOLVE_TYPE_MUTATE_RATE:
        pop.gate_logits[idx] += rng.normal(
            0.0, defaults.EVOLVE_TYPE_MUTATE_SIGMA, size=pop.gate_logits[idx].shape
        )
        nudged = True
    # children start more plastic than parent
    pop.differentiation[idx] = float(pop.differentiation[idx]) * 0.5
    pop.age[idx] = 0
    pop.utility[idx] = float(pop.utility[idx]) * 0.5
    return nudged


def run_cycle(
    pop: Population,
    harness: TemporalHarness,
    rng: np.random.Generator,
) -> CycleReport:
    """One evaluate→select→clone→mutate cycle with automatic rollback on fail."""
    snap = PopSnapshot.capture(pop, harness, note="pre-cycle")
    util_before = float(pop.utility.mean())
    act_before = float(np.mean(np.abs(pop.activity)))

    n = pop.n
    k = min(defaults.EVOLVE_TOP_K, n)
    n_replace = max(1, int(round(n * defaults.EVOLVE_REPLACE_FRAC)))
    n_replace = min(n_replace, n - k) if n > k else max(1, n // 4)

    order = np.argsort(-pop.utility)
    elites = order[:k].tolist()
    # replace lowest-utility slots
    victims = order[-n_replace:].tolist()
    # don't replace an elite if overlap (tiny n edge case)
    elite_set = set(elites)
    victims = [v for v in victims if v not in elite_set] or order[-n_replace:].tolist()

    cloned_from: List[int] = []
    type_nudged: List[int] = []
    for v in victims:
        parent = int(rng.choice(elites))
        # clone tensors
        pop.gate_logits[v] = pop.gate_logits[parent].copy()
        pop.type_weights[v] = pop.type_weights[parent].copy()
        pop.bias[v] = pop.bias[parent].copy()
        pop.hidden[v] = pop.hidden[parent].copy()
        pop.activity[v] = pop.activity[parent]
        pop.utility[v] = pop.utility[parent]
        pop.differentiation[v] = pop.differentiation[parent]
        pop.age[v] = pop.age[parent]
        cloned_from.append(parent)
        if _mutate_clone(pop, v, rng):
            type_nudged.append(v)

    # light readout mutate (shared) — small
    pop.readout += rng.normal(0.0, defaults.EVOLVE_MUTATE_SIGMA * 0.25, size=pop.readout.shape)

    util_after = float(pop.utility.mean())
    act_after = float(np.mean(np.abs(pop.activity)))
    ok, reason = check_stability(pop, util_before, act_before)
    if not ok:
        snap.restore(pop, harness)
        return CycleReport(
            kept=elites,
            replaced=victims,
            cloned_from=cloned_from,
            type_nudged=type_nudged,
            util_before=util_before,
            util_after=util_after,
            activity_before=act_before,
            activity_after=act_after,
            rolled_back=True,
            fail_reason=reason,
        )
    return CycleReport(
        kept=elites,
        replaced=victims,
        cloned_from=cloned_from,
        type_nudged=type_nudged,
        util_before=util_before,
        util_after=float(pop.utility.mean()),
        activity_before=act_before,
        activity_after=float(np.mean(np.abs(pop.activity))),
        rolled_back=False,
    )


def run_cycles(
    pop: Population,
    harness: TemporalHarness,
    n: int,
    seed: Optional[int] = None,
) -> List[CycleReport]:
    n = int(max(1, min(n, defaults.EVOLVE_MAX_CYCLES)))
    rng = np.random.default_rng(defaults.SEED + 99 if seed is None else seed)
    return [run_cycle(pop, harness, rng) for _ in range(n)]
