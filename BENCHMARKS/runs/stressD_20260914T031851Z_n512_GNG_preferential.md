# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T031851Z_n512_GNG_preferential`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **0** · DSC wins **6**
- dsc_family: `preferential_directed` · experiment: `sweep_20260914T031845Z_GNG_preferential`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.10129587048610823 | 0.10133548839677353 |
| `tick_wall_us` | 1671.6250000001764 | 1702.958500000129 |
| `utility_mean` | 0.1612322851692614 | 0.1568376158823531 |
| `coverage_mean` | 0.46162226655548444 | 0.459159464048059 |
| `latent_n` | 64 | 64 |
| `E_edge` | 6.91614899787187e-05 | 6.91590020594967e-05 |
| `E_tick` | 0.000543196710943245 | 0.0005331830094738441 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **dsc** | DSC holding on task — push scale or harder harness |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **dsc** | Good edge efficiency — test at larger N |
| `utility_mean` | **dsc** | Utility OK on this family |
| `coverage_mean` | **dsc** | Coverage holding |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
