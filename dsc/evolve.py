"""F006 evolution + F007 latent prune + F008 absorb + crossover + F009 rollback."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from dsc import defaults
from dsc.absorb import absorb_coverage
from dsc.cells import Population
from dsc.harness import TemporalHarness
from dsc.latent import LatentPool


@dataclass
class PopSnapshot:
    """In-memory last-good (F009), includes latent pool."""

    gate_logits: np.ndarray
    type_weights: np.ndarray
    bias: np.ndarray
    readout: np.ndarray
    utility: np.ndarray
    age: np.ndarray
    differentiation: np.ndarray
    activity: np.ndarray
    hidden: np.ndarray
    fail_streak: np.ndarray
    harness_state: Dict[str, Any]
    latent: LatentPool
    signal_hist: Dict[str, List[float]] = field(default_factory=dict)
    note: str = ""

    @classmethod
    def capture(
        cls,
        pop: Population,
        harness: TemporalHarness,
        latent: LatentPool,
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
            fail_streak=pop.fail_streak.copy(),
            harness_state=deepcopy(harness.state_dict()),
            latent=latent.copy(),
            signal_hist={k: list(v) for k, v in (signal_hist or {}).items()},
            note=note,
        )

    def restore(
        self,
        pop: Population,
        harness: TemporalHarness,
        latent: LatentPool,
    ) -> LatentPool:
        pop.gate_logits[...] = self.gate_logits
        pop.type_weights[...] = self.type_weights
        pop.bias[...] = self.bias
        pop.readout[...] = self.readout
        pop.utility[...] = self.utility
        pop.age[...] = self.age
        pop.differentiation[...] = self.differentiation
        pop.activity[...] = self.activity
        pop.hidden[...] = self.hidden
        pop.fail_streak[...] = self.fail_streak
        harness.load_state(deepcopy(self.harness_state))
        return self.latent.copy()


@dataclass
class CycleReport:
    kept: List[int]
    replaced: List[int]
    cloned_from: List[int]
    crossed_from: List[Tuple[int, int]]
    type_nudged: List[int]
    pruned_to_latent: List[int]
    absorbed_via: List[Tuple[int, List[int]]]
    reactivated: List[int]
    util_before: float
    util_after: float
    activity_before: float
    activity_after: float
    latent_size: int
    rolled_back: bool = False
    fail_reason: str = ""

    def lines(self, cycle_i: int) -> List[str]:
        if self.rolled_back:
            return [
                f"evolve[{cycle_i}] ROLLBACK — {self.fail_reason}",
                f"  util {self.util_before:.4f}→{self.util_after:.4f}  "
                f"act {self.activity_before:.4f}→{self.activity_after:.4f}",
            ]
        xover = len(self.crossed_from)
        return [
            f"evolve[{cycle_i}] keep={len(self.kept)} replace={len(self.replaced)} "
            f"xover={xover} type_nudge={len(self.type_nudged)} "
            f"latent+={len(self.pruned_to_latent)} revive={len(self.reactivated)} "
            f"pool={self.latent_size}",
            f"  util {self.util_before:.4f}→{self.util_after:.4f}  "
            f"act {self.activity_before:.4f}→{self.activity_after:.4f}  "
            f"absorb={len(self.absorbed_via)}",
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
    if util_before > 1e-6:
        if util_after < util_before * (1.0 - defaults.ROLLBACK_UTIL_CLIFF):
            return False, (
                f"utility cliff {util_before:.4f}→{util_after:.4f} "
                f"(>{defaults.ROLLBACK_UTIL_CLIFF:.0%} drop)"
            )
    return True, ""


def update_fail_streaks(pop: Population) -> None:
    """F007 eligibility: sustained low-utility ticks."""
    q = float(np.quantile(pop.utility, defaults.PRUNE_UTIL_QUANTILE))
    low = pop.utility < q
    pop.fail_streak = np.where(low, pop.fail_streak + 1, 0).astype(np.int32)


def _mutate_slot(pop: Population, idx: int, rng: np.random.Generator) -> bool:
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
    pop.differentiation[idx] = float(pop.differentiation[idx]) * 0.5
    pop.age[idx] = 0
    pop.utility[idx] = float(pop.utility[idx]) * 0.5
    pop.fail_streak[idx] = 0
    return nudged


def _crossover_install(
    pop: Population,
    idx: int,
    a: int,
    b: int,
    rng: np.random.Generator,
) -> None:
    """Fancy crossover: blend two elites into slot idx (gates/weights/bias)."""
    alpha = float(
        np.clip(
            defaults.EVOLVE_CROSSOVER_ALPHA + rng.normal(0.0, 0.1),
            0.2,
            0.8,
        )
    )
    # per-dim mask for gates (uniform crossover) + soft blend for weights
    mask = rng.random(pop.gate_logits[idx].shape) < alpha
    pop.gate_logits[idx] = np.where(mask, pop.gate_logits[a], pop.gate_logits[b])
    pop.type_weights[idx] = alpha * pop.type_weights[a] + (1 - alpha) * pop.type_weights[b]
    pop.bias[idx] = alpha * pop.bias[a] + (1 - alpha) * pop.bias[b]
    pop.hidden[idx] = 0.5 * (pop.hidden[a] + pop.hidden[b])
    pop.activity[idx] = 0.5 * (float(pop.activity[a]) + float(pop.activity[b]))
    pop.utility[idx] = 0.5 * (float(pop.utility[a]) + float(pop.utility[b]))
    pop.differentiation[idx] = 0.5 * (
        float(pop.differentiation[a]) + float(pop.differentiation[b])
    )


def run_cycle(
    pop: Population,
    harness: TemporalHarness,
    latent: LatentPool,
    rng: np.random.Generator,
    sub: Optional["Substrate"] = None,
) -> Tuple[CycleReport, LatentPool]:
    snap = PopSnapshot.capture(pop, harness, latent, note="pre-cycle")
    util_before = float(pop.utility.mean())
    act_before = float(np.mean(np.abs(pop.activity)))

    update_fail_streaks(pop)

    n = pop.n
    k = min(defaults.EVOLVE_TOP_K, n)
    n_replace = max(1, int(round(n * defaults.EVOLVE_REPLACE_FRAC)))
    n_replace = min(n_replace, n - k) if n > k else max(1, n // 4)

    order = np.argsort(-pop.utility)
    elites = order[:k].tolist()
    # Prefer sustained-failure cells among the bottom for latent prune (F007)
    bottom = order[-n_replace:]
    streak_ok = [int(i) for i in bottom if pop.fail_streak[i] >= defaults.PRUNE_FAIL_STREAK]
    victims = streak_ok + [int(i) for i in bottom if int(i) not in streak_ok]
    victims = victims[:n_replace]
    elite_set = set(elites)
    victims = [v for v in victims if v not in elite_set] or [int(i) for i in bottom]

    survivors = [i for i in range(n) if i not in set(victims)]
    cloned_from: List[int] = []
    crossed_from: List[Tuple[int, int]] = []
    type_nudged: List[int] = []
    pruned_to_latent: List[int] = []
    absorbed_via: List[Tuple[int, List[int]]] = []
    reactivated: List[int] = []

    for v in victims:
        # F008 absorb before overwrite
        absorbers = absorb_coverage(pop, v, survivors, sub=sub)
        if absorbers:
            absorbed_via.append((v, absorbers))
        # F007 archive into latent
        latent.push_from_pop(pop, v)
        pruned_to_latent.append(v)

        # Fill slot: reactivate OR crossover OR clone
        did_revive = False
        # Revive from older latent entries (exclude the one we just pushed = last)
        if len(latent.entries) > 1 and rng.random() < defaults.REACTIVATE_RATE:
            older_idxs = list(range(len(latent.entries) - 1))
            bi = max(older_idxs, key=lambda i: latent.entries[i].utility)
            entry = latent.entries.pop(bi)
            latent.install(pop, v, entry)
            reactivated.append(v)
            did_revive = True

        if not did_revive:
            if len(elites) >= 2 and rng.random() < defaults.EVOLVE_CROSSOVER_RATE:
                a, b = (int(x) for x in rng.choice(elites, size=2, replace=False))
                _crossover_install(pop, v, a, b, rng)
                crossed_from.append((a, b))
            else:
                parent = int(rng.choice(elites))
                pop.gate_logits[v] = pop.gate_logits[parent].copy()
                pop.type_weights[v] = pop.type_weights[parent].copy()
                pop.bias[v] = pop.bias[parent].copy()
                pop.hidden[v] = pop.hidden[parent].copy()
                pop.activity[v] = pop.activity[parent]
                pop.utility[v] = pop.utility[parent]
                pop.differentiation[v] = pop.differentiation[parent]
                pop.age[v] = pop.age[parent]
                cloned_from.append(parent)
            if _mutate_slot(pop, v, rng):
                type_nudged.append(v)

    pop.readout += rng.normal(0.0, defaults.EVOLVE_MUTATE_SIGMA * 0.25, size=pop.readout.shape)

    util_after = float(pop.utility.mean())
    act_after = float(np.mean(np.abs(pop.activity)))
    ok, reason = check_stability(pop, util_before, act_before)
    if not ok:
        restored = snap.restore(pop, harness, latent)
        return (
            CycleReport(
                kept=elites,
                replaced=victims,
                cloned_from=cloned_from,
                crossed_from=crossed_from,
                type_nudged=type_nudged,
                pruned_to_latent=pruned_to_latent,
                absorbed_via=absorbed_via,
                reactivated=reactivated,
                util_before=util_before,
                util_after=util_after,
                activity_before=act_before,
                activity_after=act_after,
                latent_size=len(restored),
                rolled_back=True,
                fail_reason=reason,
            ),
            restored,
        )

    return (
        CycleReport(
            kept=elites,
            replaced=victims,
            cloned_from=cloned_from,
            crossed_from=crossed_from,
            type_nudged=type_nudged,
            pruned_to_latent=pruned_to_latent,
            absorbed_via=absorbed_via,
            reactivated=reactivated,
            util_before=util_before,
            util_after=float(pop.utility.mean()),
            activity_before=act_before,
            activity_after=float(np.mean(np.abs(pop.activity))),
            latent_size=len(latent),
            rolled_back=False,
        ),
        latent,
    )


def run_cycles(
    pop: Population,
    harness: TemporalHarness,
    latent: LatentPool,
    n: int,
    seed: Optional[int] = None,
    sub: Optional["Substrate"] = None,
) -> Tuple[List[CycleReport], LatentPool]:
    n = int(max(1, min(n, defaults.EVOLVE_MAX_CYCLES)))
    rng = np.random.default_rng(defaults.SEED + 99 if seed is None else seed)
    reports: List[CycleReport] = []
    for _ in range(n):
        rep, latent = run_cycle(pop, harness, latent, rng, sub=sub)
        reports.append(rep)
    return reports, latent
