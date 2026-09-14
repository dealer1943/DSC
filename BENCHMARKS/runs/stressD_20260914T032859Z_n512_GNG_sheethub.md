# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T032859Z_n512_GNG_sheethub`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **5** · DSC wins **1**
- dsc_family: `sheet_hub_directed` · experiment: `F028_exp7_sheet_hub_GNG_sanity`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.1014242633135953 | 0.10133548839677353 |
| `tick_wall_us` | 1662.811999999958 | 1661.4795000000627 |
| `utility_mean` | 0.15660966638612311 | 0.1568376158823531 |
| `coverage_mean` | 0.4613103752263619 | 0.459159464048059 |
| `latent_n` | 64 | 64 |
| `E_edge` | 6.915342783632058e-05 | 6.91590020594967e-05 |
| `E_tick` | 0.0005460120290586523 | 0.0005464939760250415 |

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
