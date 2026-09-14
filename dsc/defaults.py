"""Frozen substrate + MVP runtime defaults (S001 / F001)."""
from __future__ import annotations

# Stack
PYTHON_MIN = (3, 9)
ARRAY_STACK = "numpy"  # no NetworkX required for ER generator

# Substrate (F001)
N_NODES = 128
GRAPH_FAMILY = "erdos_renyi_directed"
EDGE_PROB = 0.08          # expected density ~8% (<10% guardrail)
DIRECTED = True
ALLOW_SELF_LOOPS = False
SEED = 42

# Cells / gating (F002 / F003)
TYPE_NAMES = (
    "ATTRACTOR",
    "LATENT",
    "MODULATORY",
    "MODULAR",
    "METASTABLE",
)
# STEM = soft mixture over TYPE_NAMES (never a hard one-hot at init)
HIDDEN = 8
STEM_TEMPERATURE = 1.0

# Utility (F005)
UTILITY_EMA_ALPHA = 0.15
W_TASK = 1.0
W_COVERAGE = 0.35
W_NOVELTY = 0.25
W_COST = 0.20

# Temporal harness (F010)
TASK_NAME = "lag1_scalar_predict"
TASK_LAG = 1
TASK_NOISE = 0.05

# Persistence
SCHEMA_VERSION = 1
CHECKPOINT_NAME = "checkpoint.npz"

# Differentiation (F004 light)
DIFF_EMA_ALPHA = 0.18
DIFF_RISE = 0.14          # push toward 1 when utility stable/high
DIFF_FALL = 0.06          # fall toward STEM when utility drops
DIFF_STABILITY_EPS = 0.025 # |Δu| below this counts as stable
DIFF_STEM_LABEL = 0.30    # UI STEM label threshold (cells.py)
DIFF_PEAK_BONUS = 0.10    # extra rise when gate mixture is peaked (low entropy)
DIFF_TEMP_FLOOR = 0.85    # committed cells: temp *= (1 - floor*diff) → sharper types
EMERGE_ELITE_BOOST = 0.12 # post-evolve commitment bump for top-K elites
EMERGE_GATE_SHARPEN = 0.35  # post-evolve amplify gate logits toward winner

# Evolution (F006)
EVOLVE_TOP_K = 16                 # elites kept / cloned from
EVOLVE_REPLACE_FRAC = 0.25        # fraction of slots replaced per cycle
EVOLVE_MUTATE_SIGMA = 0.05        # Gaussian noise on params of clones
EVOLVE_TYPE_MUTATE_RATE = 0.05    # rare gate-logit nudge probability per clone
EVOLVE_TYPE_MUTATE_SIGMA = 0.35
EVOLVE_DEFAULT_CYCLES = 1
EVOLVE_MAX_CYCLES = 32

# Stability / rollback (F009 light)
ROLLBACK_UTIL_CLIFF = 0.45        # mean utility drop fraction vs pre-cycle → fail
ROLLBACK_FOOTPRINT_MIN = 1e-4     # near-zero floor only (DSC activity is often ~0.01–0.05)
ROLLBACK_FOOTPRINT_REL = 0.20     # activity mean must stay ≥ this × pre-cycle

# Latent prune pool (F007)
LATENT_POOL_MAX = 64
PRUNE_FAIL_STREAK = 8          # sustained low-utility ticks before eligible for latent
PRUNE_UTIL_QUANTILE = 0.25     # below this quantile counts as "low" for streak
REACTIVATE_RATE = 0.08         # chance per cycle to revive one latent into a victim slot

# Coverage absorption (F008)
ABSORB_BLEND = 0.35            # how much pruned cell params bleed into absorbers
ABSORB_TOP = 3                 # number of surviving absorbers per prune

# Crossover (F006 fancy)
EVOLVE_CROSSOVER_RATE = 0.35   # fraction of replacements that blend two elites
EVOLVE_CROSSOVER_ALPHA = 0.5   # mix weight parent_a vs parent_b (jittered)


# Message passing (F023)
HUB_AWARE = True              # damp high out-degree sources; log in-degree normalize
HUB_OUT_EXP = 0.5             # divide source msgs by out_deg**exp
