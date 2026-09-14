# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T012211Z_n512_GNG_preferential`
- N=512 neuropil=`GNG` seed=42
- scoreboard: fly_adj wins **2** · DSC wins **3**
- dsc_family: `preferential_directed` · experiment: `F023_exp3_hub_aware`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 13129 | 13129 |
| `density` | 0.05018117049902153 | 0.05018117049902153 |
| `task_error` | 0.006386764511900769 | 0.0063814918529512725 |
| `tick_wall_us` | 1811.2910000001038 | 1813.0414999999457 |
| `utility_mean` | 0.12741245793755612 | 0.1207124847277807 |
| `E_edge` | 7.568388813933828e-05 | 7.568428466424792e-05 |
| `E_tick` | 0.0005485886957873225 | 0.0005480619022548247 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **dsc** | Utility OK on this family |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
