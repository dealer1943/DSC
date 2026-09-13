"""F005 — multi-term utility evaluation."""
from __future__ import annotations

import numpy as np

from dsc import defaults
from dsc.cells import Population


def update_utilities(
    pop: Population,
    task_reward: float,
    *,
    alpha: float = defaults.UTILITY_EMA_ALPHA,
) -> dict:
    """
    task_reward: higher is better (we pass -err).
    Per-cell terms:
      task  — activity-weighted share of task_reward
      coverage — prefer cells that fire when others are quiet (soft exclusivity)
      novelty — distance of gate logits from population mean
      cost — activity + param magnitude penalty
    """
    act = pop.activity + 1e-6
    share = act / act.sum()
    task_term = share * float(task_reward)

    # coverage: high when a cell is active and mean others are low
    mean_others = (act.sum() - act) / max(1, pop.n - 1)
    coverage = act / (act + mean_others)

    mean_gate = pop.gate_logits.mean(axis=0, keepdims=True)
    novelty = np.linalg.norm(pop.gate_logits - mean_gate, axis=1)
    novelty = novelty / (novelty.max() + 1e-6)

    cost = 0.5 * (act / (act.max() + 1e-6)) + 0.5 * (
        np.linalg.norm(pop.type_weights.reshape(pop.n, -1), axis=1)
        / (np.linalg.norm(pop.type_weights.reshape(pop.n, -1), axis=1).max() + 1e-6)
    )

    raw = (
        defaults.W_TASK * task_term
        + defaults.W_COVERAGE * coverage
        + defaults.W_NOVELTY * novelty
        - defaults.W_COST * cost
    )
    pop.utility = (1 - alpha) * pop.utility + alpha * raw
    return {
        "task_mean": float(task_term.mean()),
        "coverage_mean": float(coverage.mean()),
        "novelty_mean": float(novelty.mean()),
        "cost_mean": float(cost.mean()),
        "utility_mean": float(pop.utility.mean()),
        "utility_max": float(pop.utility.max()),
    }
