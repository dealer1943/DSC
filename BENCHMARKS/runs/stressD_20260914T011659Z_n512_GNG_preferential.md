# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T011659Z_n512_GNG_preferential`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **3** · DSC wins **2**

## Side-by-side

| metric | ER | FlyWire-adj |
|--------|----|-------------|
- dsc_family: `preferential_directed` · experiment: `F022_exp1_preferential`

| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.006383465780584753 | 0.006381155568224717 |
| `tick_wall_us` | 1565.4375000002663 | 1573.645999999984 |
| `utility_mean` | 0.12159796107526158 | 0.15489955934154712 |
| `E_edge` | 7.568413621655776e-05 | 7.56843099543369e-05 |
| `E_tick` | 0.0006347471709263499 | 0.0006314376329813054 |

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
