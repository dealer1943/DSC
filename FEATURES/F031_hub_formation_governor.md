---
id: F031
title: Hub formation governor (when to form a hub)
status: soft_assay
phase: DSC core / R005 meta
pairs_with: [F023, F028, R005, R004, B017]
updated: 2026-09-14
priority_note: ME_R first — anti-overfit; no neuropil if-branches in dsc/.
---

## Purpose
Meta-architecture control for **when to form (or amplify) a hub**.

Rule of thumb:
> Form or amplify a hub when integration demand rises faster than local wiring can carry —
> and only until hub-share / skew hits a soft ceiling.

Layman: hubs help until they congest the graph. Under-hub fails integration;
over-hub (R005 gene v0.1/v0.2 overshoot) cartoons topology and can erase task gains.

## Non-goals
- No `if neuropil == …` in `dsc/`.
- No pasted FlyWire ME_R hub % or max-degree constants.
- Not a second brain — only caps / on-ramps on existing `sheet_hub` genes + F023 damp.

## Technical (v0)
1. **On-ramp** from regime vector `r` (same sensor as R005):
   - `hub_demand ∝ r_hub * (1 - κ·r_local)` — local sheet regime suppresses hub growth.
2. **Soft ceilings** (procedural vs ER same N/E z-scores, not fly tables):
   - `z_skew_max`, `z_hub_share_max` scale gently with `hub_demand`.
3. **Gene clip** before generate: α/β/σ from `substrate_genes_from_r`, then governor shrinks
   α/β if demand is low or ceilings would be tight.
4. **One regenerate** if post-gen `degree_skew` / `hub_out_share` z vs ER exceeds ceiling:
   back off α/β ×0.85 (and slightly raise `sigma_scale`), rebuild once, keep better-of
   (closer to ceiling without overshoot; never fly-fitted targets).
5. Optional gather damp nudge: raise `HUB_OUT_EXP` slightly when overshoot was detected.

CLI:
```bash
# genes from r + F031 governor (recommended ME_R path)
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R \
  --dsc-family sheet_hub --regime-substrate --hub-governor --experiment F031_ME_R

# governor alone implies substrate genes + govern
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --hub-governor
```

## Acceptance (anti-overfit)
- [x] No neuropil strings in `dsc/` governor path
- [x] ME_R 30-seed: mean task gap vs `sheet_hub` control improves or holds vs ungoverened genes
- [x] Topology: **ER-z overshoot reduced** vs genes-alone (fly is exam tape only — not a fit target)
- [x] Ceilings labeled as assay ER-z hand knobs (not fly constants)
- [x] GNG: `--hub-governor` refuses silent remap unless optic venue or explicit `sheet_hub` request
- [x] Ledger/MD record hub_governor / genes / overshoot / regenerated / nudge / family_forced_sheet_hub
- [x] Peer adversarial (blockers patched; promote is opt-in) review before promote


## Bench — ME_R 30-seed (recorded)
Artifact: `BENCHMARKS/runs/F031_hub_gov_n30_20260914T145424Z.{json,md}`  
Seeds: same draw as R005 gather/substrate n30 (`draw_seed=42`, n=30 from 1–100).

### Topology seed42
| metric | fly | control | genes alone | **governor** |
|--------|-----|---------|-------------|--------------|
| degree_skew | 4.78 | 1.88 | **12.84** (overshoot) | 1.53 |
| hub_out_share | 0.269 | 0.204 | 0.521 | **0.209** (closest) |
| local_frac | 0.359 | 0.205 | 0.222 | **0.235** |
| recip | 0.296 | 0.250 | 0.353 | **0.334** |
| clustering | 0.108 | 0.088 | 0.050 | **0.106** |

Governor kills gene hub cartoon; closest on hub_share / local / recip / clustering. Skew still below fly (control also under) — ceiling working.

### Task
| arm | mean gap | ±std | task D/F | sb Σ D/F |
|-----|----------|------|----------|----------|
| control | +6.2e-6 | ±2.0e-5 | 14/16 | 85/95 |
| substrate genes | **−4.3e-6** | ±2.5e-5 | 15/15 | 88/92 |
| **hub-governor** | −3.1e-6 | ±**1.7e-5** | **18/12** | 72/108 |

Paired gov−control: mean Δ **−9.3e-6**, better **20/10**.  
Paired gov−sub: mean ≈ flat (+1.2e-6); seed-count leans gov on gap 19/11; lower variance; more task wins vs fly.

**Read:** Soft opt-in. Governor trades a hair of mean-gap vs raw genes for **topology honesty + more task wins + tighter variance**. Scoreboard efficiency still soft. Not default stack until Peer clears + GNG sanity documented.

## Peer
Adversarial review requested 2026-09-14 (DSC Peer). Promote only after blockers cleared.

## Status
**soft_assay** (not promoted). Peer re-review (post-patch): patches peer-OK, but
`promote_ok_heuristic=False` on `F031_promote_confirm_n30_20260914T150550Z`
(paired gov better only 13/17 vs control; sb efficiency worse; overshoot_final+nudge
on 30/30 so regenerate never clears and gated nudge is always-on on ME_R in practice).
Do **not** claim promote on the soft mean-gap tick. Pre-patch draw42 20/10 is not
post-patch evidence. Next: topology-only arm (nudge forced 0) + bench until
`promote_ok_heuristic=True` with paired majority.

## Peer blockers (2026-09-14) — patched
Ledger fields, `family_forced_sheet_hub` + `degenerate_ab` on override paths, nudge gated on `overshoot_final`, GNG refuse unless optic/explicit sheet_hub, acceptance = ER-z not fly-fit, ceiling assay label, MD governor lines.

## Promote-confirm — fresh 30-seed (post-Peer)
Artifact: `BENCHMARKS/runs/F031_promote_confirm_n30_20260914T150550Z.{json,md}`  
`draw_seed=314159` (fresh ≠ prior 42 panel). Arms: control vs `--hub-governor`.

| arm | mean gap | ±std | task D/F | sb Σ D/F |
|-----|----------|------|----------|----------|
| control | +4.2e-6 | ±2.1e-5 | 14/16 | 83/97 |
| governor | **+0.37e-6** | ±**1.0e-5** | **16/14** | 74/106 |

Paired Δgap mean **−3.8e-6**; gov better **13** / control **17** (count noisy; mean + wins still favor gov).  
Regen/overshoot_final/nudge rates = 1.0 on this draw (ceilings still tight — assay knobs).

**Promote decision (revoked):** Peer re-review → stay **soft_assay**. Post-patch confirm does not earn promote. draw_seed=42 pre-patch 20/10 is not post-patch evidence. Ship topology-only arm (nudge=0) before re-asking promote.

