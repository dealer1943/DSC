# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T033154Z_n512_AVLP_R_sheethub`
- N=512 neuropil=`AVLP_R` seed=42
- scoreboard: fly_adj wins **6** · DSC wins **0**
- dsc_family: `sheet_hub_directed` · experiment: `AVLP_bakeoff_sheet_hub`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 24854 | 24854 |
| `density` | 0.09499602495107633 | 0.09499602495107633 |
| `task_error` | 0.1013448267198756 | 0.10125344045834397 |
| `tick_wall_us` | 1926.1040000000396 | 1915.5204999998787 |
| `utility_mean` | 0.15070095176271026 | 0.15538351009332113 |
| `coverage_mean` | 0.4643775653818568 | 0.46518652953837175 |
| `latent_n` | 64 | 64 |
| `E_edge` | 3.6532583857228964e-05 | 3.6535615472059977e-05 |
| `E_tick` | 0.0004714080024689996 | 0.00047405192841456736 |

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
