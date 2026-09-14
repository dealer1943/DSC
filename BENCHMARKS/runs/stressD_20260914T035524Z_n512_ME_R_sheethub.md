# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035524Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=44
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s44_talk`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 4118 | 4118 |
| `density` | 0.015739664872798435 | 0.015739664872798435 |
| `task_error` | 0.4458772021580171 | 0.4456968168679959 |
| `tick_wall_us` | 1213.2709999992385 | 1243.0835000003526 |
| `utility_mean` | 0.1277912024267978 | 0.12393077528955257 |
| `coverage_mean` | 0.4618185268895883 | 0.46022536619124477 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00016795086605714168 | 0.00016797182194867408 |
| `E_tick` | 0.0005700471423315513 | 0.0005564452933245785 |

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
