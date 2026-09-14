# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T012841Z_n512_GNG_preferential`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **5** · DSC wins **1**
- dsc_family: `preferential_directed` · experiment: `F024_exp4_prune_coverage`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.006459409133330456 | 0.0064442218719800055 |
| `tick_wall_us` | 1774.8330000002534 | 1766.3744999993903 |
| `utility_mean` | 0.1442061193631127 | 0.14305983536479083 |
| `coverage_mean` | 0.43006062228829417 | 0.4324404477668085 |
| `latent_n` | 63 | 63 |
| `E_edge` | 7.567842539801723e-05 | 7.567956738681318e-05 |
| `E_tick` | 0.0005598172036751776 | 0.000562506444823458 |

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
