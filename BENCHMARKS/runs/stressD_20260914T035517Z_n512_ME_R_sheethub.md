# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035517Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=43
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s43_talk`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3792 | 3792 |
| `density` | 0.014493639921722113 | 0.014493639921722113 |
| `task_error` | 0.187389553146329 | 0.18720118042135386 |
| `tick_wall_us` | 1175.4374999997099 | 1188.1664999995323 |
| `utility_mean` | 0.13241419769546192 | 0.13042779934066956 |
| `coverage_mean` | 0.4625987920615525 | 0.45965744872199304 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00022209482934222637 | 0.0002221300690378197 |
| `E_tick` | 0.0007164852175176735 | 0.0007089218739896671 |

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
