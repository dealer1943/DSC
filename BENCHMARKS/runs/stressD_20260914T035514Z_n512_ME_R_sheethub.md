# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035514Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=43
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s43_base`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3792 | 3792 |
| `density` | 0.014493639921722113 | 0.014493639921722113 |
| `task_error` | 0.187255001311602 | 0.18707388839868858 |
| `tick_wall_us` | 1028.645499999925 | 1068.083499998984 |
| `utility_mean` | 0.13026119946794948 | 0.13004694997442834 |
| `coverage_mean` | 0.46179781417131116 | 0.4593779774261153 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00022211999939140568 | 0.0002221538884361393 |
| `E_tick` | 0.0008188234310967887 | 0.0007887094454231729 |

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
