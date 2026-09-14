# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T031857Z_n512_ME_R_laminar`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **5** · DSC wins **1**
- dsc_family: `laminar_directed` · experiment: `sweep_20260914T031845Z_ME_R_laminar`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10131981648063557 | 0.10117564743301982 |
| `tick_wall_us` | 1077.9379999990012 | 1064.9579999997272 |
| `utility_mean` | 0.16622793440438527 | 0.16014130727689835 |
| `coverage_mean` | 0.4602378406759419 | 0.46296067868244023 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002546988664312632 | 0.0002547322123312454 |
| `E_tick` | 0.0008423503567257991 | 0.0008527287808168232 |

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
