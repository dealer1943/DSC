# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T033644Z_n512_AVLP_R_preferential`
- N=512 neuropil=`AVLP_R` seed=42
- scoreboard: fly_adj wins **4** · DSC wins **2**
- dsc_family: `preferential_directed` · experiment: `F029_exp8_bilayer_AVLP_preferential`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 23546 | 24854 |
| `density` | 0.08999663649706457 | 0.09499602495107633 |
| `task_error` | 0.10143523108154912 | 0.10127647595554685 |
| `tick_wall_us` | 2138.8749999999845 | 2122.0415000000603 |
| `utility_mean` | 0.16075891854698987 | 0.15500108913213437 |
| `coverage_mean` | 0.4637988484219068 | 0.4646973507835811 |
| `latent_n` | 64 | 64 |
| `E_edge` | 3.855883433742863e-05 | 3.653485125336795e-05 |
| `E_tick` | 0.00042447843530318564 | 0.0004279073679997216 |

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
