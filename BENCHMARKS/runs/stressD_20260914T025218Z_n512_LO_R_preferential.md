# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T025218Z_n512_LO_R_preferential`
- N=512 neuropil=`LO_R` seed=42
- scoreboard: fly_adj wins **5** · DSC wins **1**
- dsc_family: `preferential_directed` · experiment: `panel_hard_LO_R`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 11341 | 11341 |
| `density` | 0.04334714408023484 | 0.04334714408023484 |
| `task_error` | 0.1012718861366963 | 0.1012431361681741 |
| `tick_wall_us` | 1506.66699999924 | 1488.6040000003932 |
| `utility_mean` | 0.16047069715352247 | 0.15797971237504216 |
| `coverage_mean` | 0.46033116876785385 | 0.4620923431813871 |
| `latent_n` | 64 | 64 |
| `E_edge` | 8.00670996841022e-05 | 8.006918998234788e-05 |
| `E_tick` | 0.0006026819313875336 | 0.0006100109119615206 |

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
