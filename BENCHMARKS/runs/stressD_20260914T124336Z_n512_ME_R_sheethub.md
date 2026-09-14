# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T124336Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **4** · DSC wins **2**
- dsc_family: `sheet_hub_directed` · experiment: `R003_ME_R_sheet_hub_nearest_exact`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10122045715090996 | 0.10111799431774669 |
| `tick_wall_us` | 1730.7500000001141 | 1760.7914999999696 |
| `utility_mean` | 0.15490074897000367 | 0.1559578267139882 |
| `coverage_mean` | 0.4606462331754682 | 0.46145822647756507 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002547218470329094 | 0.0002547455497807078 |
| `E_tick` | 0.0005246762297687488 | 0.0005157725289838342 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
