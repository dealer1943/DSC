---
id: F030
title: Talk board (shared presence + edge-masked glance)
status: implemented
phase: DSC core
pairs_with: [F023, F026, F029]
updated: 2026-09-14
---

## Layman
Lobby light board: each apartment has a light (talking or not). Everyone sees the same board. You only *listen hard* to neighbors whose light is on — not a private wire to all 511 others.

## Technical
Opt-in `TALK_BOARD` (`--talk-board`):
1. Once per tick: `talk_board[i] = activity[i] > TALK_THRESH` (prev-tick); `talk_packed = packbits(...)`.
2. Global volume: light add of `talk_frac` into inject (`TALK_GLOBAL`).
3. Edge-masked glance: gather hidden only from in-neighbors with talk bit on; `messages += TALK_MIX * glance`.
4. Cost: O(edges) for glance + O(N) to build board — not O(N²).

Default off. No neuropil hardcodes.

## Eval
```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --dsc-family sheet_hub --talk-board --experiment F030_ME_R
```

## Results — ME_R sheet_hub (N=512 hard)

| talk | thresh | bilayer | fly | dsc | task gap (dsc−fly) |
|------|--------|---------|-----|-----|--------------------|
| off | — | off | 4 | 2 | +0.000016 |
| on | 0.05 | off | 4 | 2 | +0.000006 |
| on | **0.02** | off | **2** | **4** | **−0.000013** (DSC task lead) |
| on | 0.05 | on | 6 | 0 | +0.000046 |

Thresh 0.05 left the board mostly dark (activity often ~0.01–0.05). 0.02 is still procedural (tied to observed activity scale notes in F009), not ME-fitted. Single-seed — don’t overclaim; coverage/utility still often fly. Default: `TALK_BOARD=False`, `TALK_THRESH=0.02`.
