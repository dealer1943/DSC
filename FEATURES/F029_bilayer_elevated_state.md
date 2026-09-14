---
id: F029
title: Bilayer elevated state (folded sheet)
status: implemented
phase: DSC core
pairs_with: [F023, F027, F028]
updated: 2026-09-14
---

## Layman
Fold the sheet once: each cell keeps its usual local book **and** a second view from the desk one floor up (aligned seat). Same rule on every venue — index-derived floors, not a fly atlas. Opt-in A/B (`--bilayer`); default off so we do not bake an unproven fold into the stack.

## Technical
When `defaults.BILAYER` is true during `step_population`:
1. Partition `N` nodes into `L = clip(√N/2, 4..16)` sheets (same procedural rule as F027/F028).
2. For each node, sample hidden state of the aligned node in layer `L+1` (top sheet wraps to 0).
3. EMA into `pop.elevated` (`BILAYER_EMA`).
4. `messages += BILAYER_MIX * elevated` before the tanh base update.

No change to `HIDDEN` dim / checkpoint schema. Applies equally to DSC synthetic and fly-adj under Profile D (same software).

## Eval
```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --dsc-family sheet_hub --bilayer --experiment F029_ME_R_bilayer
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil AVLP_R --dsc-family modular --bilayer --experiment F029_AVLP_modular_bilayer
```
Compare to matched runs without `--bilayer`.

## Results (N=512 hard harness)

| neuropil | family | bilayer | fly | dsc | dsc task | fly task | gap |
|----------|--------|---------|-----|-----|----------|----------|-----|
| ME_R | sheet_hub | off | 4 | 2 | 0.101191 | 0.101176 | 0.000015 |
| ME_R | sheet_hub | **on** | 4 | 2 | 0.101237 | 0.101215 | 0.000022 |
| AVLP_R | modular | off | 5 | 1 | 0.101296 | 0.101253 | 0.000043 |
| AVLP_R | modular | **on** | **3** | **3** | 0.101297 | 0.101276 | **0.000021** |
| AVLP_R | preferential | on | 4 | 2 | 0.101435 | 0.101276 | 0.000159 |

Read: fold is not a free lunch. ME unchanged on scoreboard; AVLP+modular tightened the task gap and tied the board. Keep **opt-in** (`BILAYER=False` default).
