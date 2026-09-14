# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T033151Z_n512_AVLP_R_modular`
- N=512 neuropil=`AVLP_R` seed=42
- scoreboard: fly_adj wins **5** · DSC wins **1**
- dsc_family: `modular_directed` · experiment: `AVLP_bakeoff_modular`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 24854 | 24854 |
| `density` | 0.09499602495107633 | 0.09499602495107633 |
| `task_error` | 0.10129606401989169 | 0.10125344045834397 |
| `tick_wall_us` | 1908.312500000009 | 1905.8120000001732 |
| `utility_mean` | 0.16162350932741754 | 0.15538351009332113 |
| `coverage_mean` | 0.4634039879817562 | 0.46518652953837175 |
| `latent_n` | 64 | 64 |
| `E_edge` | 3.653420143081745e-05 | 3.6535615472059977e-05 |
| `E_tick` | 0.00047582408141304565 | 0.0004764668219858497 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **fly_adj** | Optimize message passing / hub handling |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **dsc** | Utility OK on this family |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **fly_adj** | Sparse kernels on hubs |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
