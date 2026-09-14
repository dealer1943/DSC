# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T025215Z_n512_ME_R_preferential`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **6** · DSC wins **0**
- dsc_family: `preferential_directed` · experiment: `panel_hard_ME_R`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10117812871843576 | 0.10117564743301982 |
| `tick_wall_us` | 1021.7500000000434 | 1017.1880000000577 |
| `utility_mean` | 0.1595416223761124 | 0.16014130727689835 |
| `coverage_mean` | 0.45861276517799593 | 0.46296067868244023 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00025473163834298054 | 0.0002547322123312454 |
| `E_tick` | 0.0008887871697506113 | 0.00089277531484921 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **fly_adj** | Optimize message passing / hub handling |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **fly_adj** | Sparse kernels on hubs |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
