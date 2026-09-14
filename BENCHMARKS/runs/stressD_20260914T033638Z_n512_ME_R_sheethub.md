# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T033638Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **4** · DSC wins **2**
- dsc_family: `sheet_hub_directed` · experiment: `F029_exp8_bilayer_ME_R_sheethub`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10123692267596715 | 0.10121511980836523 |
| `tick_wall_us` | 1275.7289999998366 | 1287.3544999998376 |
| `utility_mean` | 0.15608415233330408 | 0.16448657688724552 |
| `coverage_mean` | 0.45920315405219675 | 0.4620960842040772 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002547180384710382 | 0.0002547230816125358 |
| `E_tick` | 0.0007118046286863176 | 0.0007053906176960617 |

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
