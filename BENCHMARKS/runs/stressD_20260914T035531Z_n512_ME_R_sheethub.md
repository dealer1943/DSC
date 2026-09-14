# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035531Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=45
- scoreboard: fly_adj wins **3** · DSC wins **3**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s45_talk`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 4295 | 4295 |
| `density` | 0.016416187622309196 | 0.016416187622309196 |
| `task_error` | 0.29586108637213726 | 0.2953756930580229 |
| `tick_wall_us` | 1242.6040000015348 | 1244.3959999988151 |
| `utility_mean` | 0.1173972180229129 | 0.11417138486063944 |
| `coverage_mean` | 0.4600453742041718 | 0.46075649927422946 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00017967116477877966 | 0.00017973848978926902 |
| `E_tick` | 0.0006210246005355733 | 0.0006203626607974033 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **dsc** | Utility OK on this family |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
