# Benchmarks

Two tiers:

1. **B001–B010** — function checks tied to fundamental features (integrity of the DSC mechanism).
2. **B011–B015** — finished-system evaluations inspired by how modern LLMs are assessed (adaptation, reasoning, horizon, robustness, calibration/reproducibility).

Stubs first; harness code later. Each file states what is measured and why the measurement protects the design.

| ID | File | Tier | Related |
|----|------|------|---------|
| B001 | `B001_substrate_topology_invariants.md` | feature | F001 |
| B002 | `B002_stem_modularity.md` | feature | F002 |
| B003 | `B003_type_gating_gradient.md` | feature | F003 |
| B004 | `B004_differentiation_plasticity.md` | feature | F004 |
| B005 | `B005_utility_nondegeneracy.md` | feature | F005 |
| B006 | `B006_evolution_selection_signal.md` | feature | F006 |
| B007 | `B007_prune_without_forgetting.md` | feature | F007 |
| B008 | `B008_coverage_conservation.md` | feature | F008 |
| B009 | `B009_stability_rollback_efficacy.md` | feature | F009 |
| B010 | `B010_task_vs_footprint.md` | feature | F010 |
| B011 | `B011_few_shot_task_shift.md` | system / LLM-analog | full DSC |
| B012 | `B012_multi_step_temporal_reasoning.md` | system / LLM-analog | full DSC |
| B013 | `B013_long_horizon_dependency.md` | system / LLM-analog | full DSC |
| B014 | `B014_ood_noise_robustness.md` | system / LLM-analog | full DSC |
| B015 | `B015_calibration_and_seed_stability.md` | system / LLM-analog | full DSC |
| B016 | `B016_flywire_efficiency_parity.md` | system / comparison | F011 + R002; blueprint for efficiency tool |

3. **B016+** — cross-artifact / biological comparison efficiency.
