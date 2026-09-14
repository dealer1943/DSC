# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035521Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=44
- scoreboard: fly_adj wins **5** · DSC wins **1**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s44_base`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 4118 | 4118 |
| `density` | 0.015739664872798435 | 0.015739664872798435 |
| `task_error` | 0.445873819431545 | 0.44561733145057963 |
| `tick_wall_us` | 1085.3749999988338 | 1041.5209999994345 |
| `utility_mean` | 0.12417030011231708 | 0.1252861280637292 |
| `coverage_mean` | 0.4634941849977984 | 0.4620185919584846 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00016795125899035133 | 0.00016798105766416483 |
| `E_tick` | 0.0006372205777017251 | 0.0006641690330405305 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **fly_adj** | Optimize message passing / hub handling |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `coverage_mean` | **dsc** | Coverage holding |
| `tick_wall_us` | **fly_adj** | Sparse kernels on hubs |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
