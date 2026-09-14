# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T031854Z_n512_AVLP_R_preferential`
- N=512 neuropil=`AVLP_R` seed=42
- scoreboard: fly_adj wins **4** · DSC wins **2**
- dsc_family: `preferential_directed` · experiment: `sweep_20260914T031845Z_AVLP_R_preferential`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 23546 | 24854 |
| `density` | 0.08999663649706457 | 0.09499602495107633 |
| `task_error` | 0.10143253894414497 | 0.10125344045834397 |
| `tick_wall_us` | 1948.9584999998754 | 1917.6040000008497 |
| `utility_mean` | 0.16119250250696604 | 0.15538351009332113 |
| `coverage_mean` | 0.4643846488670486 | 0.46518652953837175 |
| `latent_n` | 64 | 64 |
| `E_edge` | 3.855892858349138e-05 | 3.6535615472059977e-05 |
| `E_tick` | 0.0004658429270951363 | 0.00047353686524547107 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **fly_adj** | Optimize message passing / hub handling |
| `E_edge` | **dsc** | Good edge efficiency — test at larger N |
| `utility_mean` | **dsc** | Utility OK on this family |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **fly_adj** | Sparse kernels on hubs |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
