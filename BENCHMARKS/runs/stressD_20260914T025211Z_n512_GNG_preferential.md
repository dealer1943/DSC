# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T025211Z_n512_GNG_preferential`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **0** · DSC wins **6**
- dsc_family: `preferential_directed` · experiment: `panel_hard_GNG`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.10129587048610823 | 0.10133548839677353 |
| `tick_wall_us` | 1641.97899999996 | 1652.0005000000283 |
| `utility_mean` | 0.1612322851692614 | 0.1568376158823531 |
| `coverage_mean` | 0.46162226655548444 | 0.459159464048059 |
| `latent_n` | 64 | 64 |
| `E_edge` | 6.91614899787187e-05 | 6.91590020594967e-05 |
| `E_tick` | 0.0005530041504371371 | 0.0005496296992882972 |

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
