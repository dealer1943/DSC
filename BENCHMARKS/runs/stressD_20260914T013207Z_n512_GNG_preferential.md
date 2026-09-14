# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T013207Z_n512_GNG_preferential`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `preferential_directed` · experiment: `F024_exp4b_hub_absorb`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.006429854953976727 | 0.006450522341097451 |
| `tick_wall_us` | 1624.1669999998985 | 1658.7710000002253 |
| `utility_mean` | 0.1358395228643758 | 0.13864190927598646 |
| `coverage_mean` | 0.43350867790760605 | 0.43863904918938784 |
| `latent_n` | 63 | 63 |
| `E_edge` | 7.568064772255026e-05 | 7.567909362604048e-05 |
| `E_tick` | 0.0006117666618946355 | 0.0005989921575769955 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **dsc** | DSC holding on task — push scale or harder harness |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **dsc** | Good edge efficiency — test at larger N |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
