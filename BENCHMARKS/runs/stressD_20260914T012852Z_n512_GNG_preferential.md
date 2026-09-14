# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T012852Z_n512_GNG_preferential`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `preferential_directed` · experiment: `F025_exp5_hard_harness`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.10128818450832244 | 0.101327823545511 |
| `tick_wall_us` | 1835.438000000078 | 1807.6045000001704 |
| `utility_mean` | 0.15483592451327252 | 0.15476621745484542 |
| `coverage_mean` | 0.46449621385391704 | 0.4639573042828342 |
| `latent_n` | 64 | 64 |
| `E_edge` | 6.91619726622552e-05 | 6.915948338163613e-05 |
| `E_tick` | 0.0004947198102484039 | 0.0005023194273511795 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **dsc** | DSC holding on task — push scale or harder harness |
| `E_tick` | **fly_adj** | Optimize message passing / hub handling |
| `E_edge` | **dsc** | Good edge efficiency — test at larger N |
| `utility_mean` | **dsc** | Utility OK on this family |
| `coverage_mean` | **dsc** | Coverage holding |
| `tick_wall_us` | **fly_adj** | Sparse kernels on hubs |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
