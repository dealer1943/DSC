# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T032902Z_n512_LO_R_sheethub`
- N=512 neuropil=`LO_R` seed=42
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `sheet_hub_directed` · experiment: `F028_exp7_sheet_hub_LO_R`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 11341 | 11341 |
| `density` | 0.04334714408023484 | 0.04334714408023484 |
| `task_error` | 0.10139940247005674 | 0.1012431361681741 |
| `tick_wall_us` | 1557.2704999999855 | 1570.9580000000667 |
| `utility_mean` | 0.15878535619807566 | 0.15797971237504216 |
| `coverage_mean` | 0.46216057658971366 | 0.4620923431813871 |
| `latent_n` | 64 | 64 |
| `E_edge` | 8.005782978350881e-05 | 8.006918998234788e-05 |
| `E_tick` | 0.00058303027481403 | 0.0005780324385437222 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **dsc** | Utility OK on this family |
| `coverage_mean` | **dsc** | Coverage holding |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
