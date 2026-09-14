---
id: R005
title: Regime mode — meta-architecture that guides without overfitting the fly
status: tooling_v0_gather_knobs
updated: 2026-09-14
related: [F022, F027, F028, F029, F030, R003, R004, B017]
priority_note: ME_R first, then LO_R — but solution must stay neuropil-agnostic.
---

## The biggest question
Microscope (R004) says fly ME_R is peakier, more ultra-local, slightly more reciprocal/clustered than `sheet_hub`.  
**How do we turn that into a mode that guides the network — without baking FlyWire ME_R into DSC?**

Answer in one line: **do not copy ME_R; detect a regime from the graph (or state), then blend procedural priors.** The fly is an *exam tape*, not the blueprint.

## Layman
You do not hardcode “when the neuropil label is medulla, use these constants.”  
You notice the **graph shape** — fat hubs? tight local cliques? lots of reciprocal edges? — and flip a **regime mode**: *hubby*, *sheet-local*, *modular*, *hybrid*.  

Same network, same cells. Mode only changes **how messages and wiring priors are weighted**. On a different graph (e.g. GNG-shaped), mode can change again from **stats**, not from an anatomical label.

## Meta-architecture (three layers)

```
┌─────────────────────────────────────────────────────────┐
│  1. REGIME SENSOR (read-only)                           │
│     graph stats and/or live state → regime vector r     │
│     examples: skew, hub_share, local_edge_frac, dens    │
└──────────────────────────┬──────────────────────────────┘
                           │ r ∈ [0,1]^k  (soft, not one-hot required)
┌──────────────────────────▼──────────────────────────────┐
│  2. MODE MIXER (procedural)                             │
│     r → weights over prior families / message knobs     │
│     sheet_hub, preferential, modular, laminar, …        │
│     + gather knobs (hub-aware, local-bias, recip prior) │
│     NO neuropil string in this path                     │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  3. CELL DYNAMICS (unchanged contract)                  │
│     STEM / types / utility / evolve still own learning  │
│     Mode is inductive bias + routing, not a second brain│
└─────────────────────────────────────────────────────────┘
```

### What “mode” is allowed to touch
| Allowed (general) | Forbidden (overfit) |
|-------------------|---------------------|
| Soft mix of **existing** substrate families | `if neuropil == "ME_R"` |
| Density / skew / hub_share → continuous knobs | Constants copied from measured fly ME_R tables |
| Message gather bias: more weight on short index hops when `local_frac` regime high | Atlas coordinates / neuropil labels inside `dsc/` |
| Optional gene-like params evolved from **task utility** (F028 future) | Fitting generator to one subgraph then claiming generality |

### Regime sensor (v0 sketch — stats only)
From adjacency (matched N/E as in Profile D):

| signal | high means | pulls mode toward |
|--------|------------|-------------------|
| `out_degree_skew`, `hub_out_share` | peaky hubs | preferential / hub-aware |
| `local_index_edge_frac` | ultra-local wires | sheet / laminar local kernel |
| `reciprocity_edge_frac` | reciprocal edges | density-scaled recip (already in F028) |
| `clustering` | tight clumps | modular / local mix |
| `density` | crowded book | weaker forced recip (F028 rule) |

Emit soft vector `r` (e.g. sigmoid of z-scores vs a **neutral procedural baseline**, not vs fly).  
Fly ME_R is used only in **evaluation** (microscope / B017) to see if `r` lands in the right region of mode-space.

### Mode mixer (v0 sketch)
```text
w_pref  ∝ r_hub
w_sheet ∝ r_local
w_mod   ∝ r_cluster
w_lam   ∝ r_local * (1 - r_hub)     # sheet without hub dominance

# at init (substrate) OR as message prior each tick:
prior = w_pref * Pref + w_sheet * SheetHub + …   # or discrete argmax with hysteresis
gather = hub_aware(r_hub) + local_bias(r_local)  # continuous knobs
```

Important: **mixer inputs are r, not "ME_R".**  
If a random ER graph is somehow hubby+local, it gets the same mode. That is the generalization test.

## How this uses the microscope without overfitting
1. R004 measures fly vs DSC gaps (skew, local_frac, …).  
2. Those gaps define **which axes of r matter** — a checklist for the sensor, not target numbers to paste into code.  
3. Success = on ME_R *and* on held-out seeds / LO_R / GNG sanity, task improves **without** neuropil branches.  
4. B017 random seeds = honesty; GNG must not collapse when ME_R mode engages via stats.

## Anti-overfit acceptance (must pass before promoting a feature)
- [ ] No neuropil / atlas strings in `dsc/` mode path  
- [ ] Knobs are functions of graph/state stats only  
- [ ] ME_R B017 cell improves mean task gap vs current sheet_hub  
- [ ] GNG preferential sanity: no wipeout vs current best  
- [ ] LO_R (second priority) reuses same mode path — only `r` changes  
- [ ] Microscope gaps shrink on the axes we claimed to target (hub, local_frac) without forcing fly’s exact max-degree

## Tooling (v0) — shipped as assay
```bash
PYTHONPATH=. python -m tools.regime_mode --neuropil ME_R --seed 42 --sense fly
PYTHONPATH=. python -m tools.regime_mode --neuropil ME_R --seed 42 --sense fly --with-stress
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --regime-mode
```
- `regime_features(adj)` → `r` vs **ER baseline** (same N/E), never vs fly tables.
- `mode_weights(r)` → soft family mix; `pick` = argmax.
- `--regime-mode` on stress: sense **fly** matched adj → override `dsc_family` with pick.
- Neuropil CLI args only select the exam subgraph.


## Gather knobs from r (v0.1 — shipped assay)

`gather_knobs_from_r(r)` → continuous message defaults (no adj blend, no neuropil if):
- `HUB_OUT_EXP` ← r_hub
- `LOCAL_GATHER_MIX` ← r_local (soft blend toward sheet-nearest; not full R003 nearest)
- bilayer/talk gated extreme (mostly off after ME_R saturation hurt task)

CLI:
```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --dsc-family sheet_hub --regime-gather
# --regime-mode = family pick + same gather knobs (DSC-only; fly stays exam tape)
```

### Pilot (seeds 42 / 17 / 22) — `R005_gather_knobs` / `_v01`
Full knob pack (bilayer+talk auto-on from saturated ME_R `r`) slightly **worse** task on 42+17.
Soft hub+local v0.1: flat-to-worse on 42+17; seed 22 tiny task win only.

### 30-seed panel — **not promoted**
Artifact: `BENCHMARKS/runs/R005_gather_n30_20260914T141451Z.{json,md}`

- ME_R · N=512 · `sheet_hub` control vs `--regime-gather` v0.1 (hub+local; DSC-only)
- 30 seeds drawn from 1–100 (`draw_seed=42`):
  `[7, 8, 12, 16, 17, 33, 35, 40, 41, 43, 45, 46, 48, 54, 55, 56, 61, 62, 64, 66, 68, 75, 77, 81, 88, 89, 95, 96, 98, 100]`
- elapsed ~266s · fails 0

| arm | n | mean gap (dsc−fly) | ±std | median gap | task wins D/F | scoreboard Σ D/F |
|-----|---|--|--|--|--|--|
| control | 30 | +6.2e-6 | ±2.0e-5 | +5e-7 | 14/16 | 75/105 |
| gather v0.1 | 30 | +6.9e-6 | ±2.3e-5 | −1e-6 | 16/14 | 62/118 |

**Paired (gather − control) on gap:** mean Δgap **+7.0e-7** (±9.2e-6); gather better **14** / control better **16**.

**Read:** noise-scale. Slightly worse mean gap + worse scoreboard; tiny task-win flip vs fly is not alpha. Keep as wiring/assay only.

### Follow-ups (do not claim ME_R win until gates pass)
1. Retune `r`→knob curves offline (or R001-logged search) — current map is uncalibrated.
2. Substrate σ/α genes from `r` (still one family; params from stats) — gather alone did not close the ME_R gap.
3. Re-check GNG sanity if any knob map is promoted (anti-overfit).
4. Context for “fly still better on ME_R”: see **R004** microscope (seed-42 fly **6–0** scoreboard) and **B017** ME_R sheet_hub (8 random seeds: fly task **5–3**).


## Substrate σ/α from r (v0.2 — assay)

Still **one** family (`sheet_hub`); genes only: `alpha`, `beta`, `sigma_scale`, `p_recip_scale` from `r` (no neuropil if, no adj blend).

```bash
PYTHONPATH=. python -m tools.flywire_stress --n 512 --neuropil ME_R --dsc-family sheet_hub --regime-substrate
```

`substrate_genes_from_r` (v0.2 soft): α≈1+0.55·r_hub, β≈1+0.35·r_hub, σ_scale≈1/(1+0.7·r_local+…), p_recip_scale≈1+0.3·r_recip.  
v0.1 (α≈2.25, σ≈0.37) **overshot** hubs (skew 9.8–12 vs fly 4.8) — discarded for task panels.

### Topology seed42 (v0.2 vs default sheet_hub)
| metric | closer to fly? |
|--------|----------------|
| degree_skew / hub_out_share / recip / clustering | **control** (genes still overshoot hubs) |
| extract_order_local_frac | **genes** (slightly closer) |

### 30-seed task panel — small win, **soft / not full promote**
Artifact: `BENCHMARKS/runs/R005_substrate_n30_20260914T143717Z.{json,md}`  
Same 30 seeds as gather n30 (`draw_seed=42`).

| arm | n | mean gap (dsc−fly) | ±std | task D/F | sb Σ D/F |
|-----|---|--|--|--|--|
| control | 30 | +6.2e-6 | ±2.0e-5 | 14/16 | 89/91 |
| substrate v0.2 | 30 | **−4.3e-6** | ±2.5e-5 | 15/15 | **94/86** |

**Paired:** mean Δgap **−1.05e-5** (±3.7e-5); substrate better **19** / control **11**.

**Read:** first lever that flips mean ME_R task gap to DSC-side. Effect is small vs paired noise (~0.3σ). Topology hub axes still wrong direction — do **not** treat as R004 microscope closed. Keep `--regime-substrate` opt-in; do not make default stack. GNG: forcing sheet_hub+genes is not the GNG map (preferential remains).

### Follow-ups
1. **F031 hub formation governor** (implemented, ME_R opt-in): see `FEATURES/F031_hub_formation_governor.md` + `F031_hub_gov_n30_20260914T145424Z` + promote-confirm `F031_promote_confirm_n30_20260914T150550Z`
2. Calibrate genes so hub skew approaches fly without overshoot (maybe α↑ with σ less tight, or cap max degree soft).
2. GNG sanity whenever promoting (preferential must not collapse).
3. Optional combo: substrate genes + gather (expect interaction).
4. Re-run R004 microscope under genes for honest topology scoreboard.

## Implementation slice (future F0xx — in-loop genes)

1. `regime_features(adj) -> r` in tooling first, then thin `dsc/` hook.  
2. `--regime-mode` opt-in on stress: mix families or bias gather.  
3. A/B: sheet_hub fixed vs regime-mode on ME_R (B017 draw) + GNG sanity.  
4. Promote only if anti-overfit gates pass.

## Self-benchmarking → self-architecture (R001 × R005)

**Can the meta find its own architecture?** In principle yes — if **assay stays quarantined from act** (R001) and the **search space is regime/mode genes**, not fly constants.

| Layer today | What exists | Gap for self-architecture |
|-------------|-------------|---------------------------|
| External benches | B006/B010 tools, B017, microscope, `dev_run` gates | Run *outside* the population |
| R001 light | `dsc/meta/manager.py` JSONL assay log from `dev_run` | Not a reserved cell; not in-loop |
| F006 evolve | Searches **cell** params (gates, weights, utility) | Does **not** yet search substrate family / `r` mixer |
| R005 mode | Spec only | Need opt-in genes: `r` thresholds, family mix, gather knobs |

### Closed loop (target, not built)
```
regime genes g  →  mode mixer  →  population tick/evolve
                      ↑                    │
                      │                    ▼
                 meta-manager ◄──── assay vector (B010/B017-style,
                 (quarantined)       task gap, footprint, integrity)
                      │
                      └── propose Δg under slow clock + F009 rollback
```

Rules so it does not game the meter:
1. Bench **definitions** pinned to `BENCHMARKS/` (manager may schedule, not redefine).
2. Manager **isolated** from task utility / prune-by-task (R001 hypothesis).
3. Architecture genes mutate on a **slower clock** than cell genes; rollback if integrity fails.
4. ME_R/LO_R remain **exam tapes**; fitness is assay vector generality (multi-seed, multi-neuropil), never “match fly degree_max”.

Promotion: when light R001 + regime genes exist, graduate to a feature (manager isolation + architecture search) paired with B015-style stability + B017 honesty.

## Non-goals
- Cloning FlyWire ME_R degree sequence  
- A permanent “optic mode” named after anatomy  
- Replacing cell learning with a fixed wiring oracle  

## Successor note
User priority remains ME_R then LO_R. This doc is the **meta** answer: mode = f(stats), fly = exam. Do not open an `if ME_R` PR.
