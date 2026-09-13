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
