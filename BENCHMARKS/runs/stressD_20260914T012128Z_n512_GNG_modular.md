# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T012128Z_n512_GNG_modular`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **3** · DSC wins **2**
- dsc_family: `modular_directed` · experiment: `F022_exp2_modular`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.006383798934163956 | 0.006381155568224717 |
| `tick_wall_us` | 1555.1040000001403 | 1582.5624999998845 |
| `utility_mean` | 0.12132574729108486 | 0.15489955934154712 |
| `E_edge` | 7.568411116205976e-05 | 7.56843099543369e-05 |
| `E_tick` | 0.0006389647865651383 | 0.000627879976551044 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
