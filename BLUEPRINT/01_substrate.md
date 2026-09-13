# Substrate blueprint (S001 frozen)

**Status:** frozen 2026-09-13 for MVP implementation  
**Code:** `dsc/substrate.py` · defaults in `dsc/defaults.py`

## Decisions

| Knob | Value | Rationale |
|------|--------|-----------|
| N | **128** | Dense enough for dynamics; light enough for UI canvas |
| Family | **Erdős–Rényi directed** | Simplest sparse directed baseline |
| Edge probability | **0.08** | Expected density ~8% (<10% guardrail) |
| Self-loops | **forbidden** | Cleaner message passing |
| Seed | **42** | Reproducible packs |
| Stack | **NumPy only** | Available on Mac Python 3.9; no NetworkX hard dep |

## Invariants (B001)
- Directed adjacency `A[i,j] = 1` means edge i→j (row = source).
- Density = `#edges / (N*(N-1))` ∈ (0, 0.10).
- No self-loops on diagonal.
- Same seed → identical edge set.

## Generator API
```python
from dsc.substrate import generate_substrate
sub = generate_substrate(n=128, p=0.08, seed=42)
# sub.adj: (N,N) uint8, sub.meta: dict
```

## Null-model hook (later)
Degree-preserving rewiring stub reserved; not required for `/load dsc` v0.
