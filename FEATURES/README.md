# Features

Fundamental capabilities required for Dynamic State Connectome (DSC) success.
Stubs first; implementation later. Each file states purpose and first-principles rationale.

| ID | File | Role |
|----|------|------|
| F001 | `F001_substrate_graph.md` | Synthetic sparse directed substrate |
| F002 | `F002_state_cell_core.md` | Modular state cell + STEM init |
| F003 | `F003_type_gating.md` | Differentiable mixture-of-types gating |
| F004 | `F004_differentiation_dynamics.md` | Plasticity ↔ commitment |
| F005 | `F005_utility_evaluation.md` | Multi-term counterfactual utility |
| F006 | `F006_evolution_loop.md` | Eval → select → reproduce → mutate |
| F007 | `F007_pruning_latent_retention.md` | Prune active set; retain latent params |
| F008 | `F008_coverage_absorption.md` | Redistribute pruned coverage |
| F009 | `F009_stability_rollback.md` | Post-cycle integrity checks + rollback |
| F010 | `F010_temporal_task_harness.md` | Measurable temporal task interface |
| F011 | `F011_offline_flywire_comparison_substrate.md` | Offline FlyWire biological comparison (zebrafish path dropped) |
| F012 | `F012_connectome_operator_console.md` | Universal operator TUI (DSC + FlyWire); signals, terminal, slash cmds |
| F013 | `F013_load_progress.md` | Load progress bar in operator console |
| F014 | `F014_checkpoint_save.md` | `/save` checkpoint bundles (`.model`) |
| F015 | `F015_cell_grid_canvas.md` | 12×12 equal-circle grid for all 128 cells |
| F016 | `F016_operator_tutorial.md` | Built-in tutorial (commands + train loop) |

## S004 (2026-09-13)
F004 light, F006 MVP, F009 light are **implemented** — see slice `SLICES/S004_evolution_mvp.md`.

## S005 (2026-09-13)
F007 latent prune, F008 absorption, and evolve crossover are **implemented**.
