# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035542Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=47
- scoreboard: fly_adj wins **4** · DSC wins **2**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s47_base`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3514 | 3514 |
| `density` | 0.013431078767123288 | 0.013431078767123288 |
| `task_error` | 0.4158089104681348 | 0.4153005695532891 |
| `tick_wall_us` | 1013.5415000007697 | 1010.4584999979238 |
| `utility_mean` | 0.12333915360365812 | 0.12325040072319549 |
| `coverage_mean` | 0.45539992569189425 | 0.45384878921106503 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00020099886339396085 | 0.00020107105720798077 |
| `E_tick` | 0.000696873296225011 | 0.000699250582809978 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **fly_adj** | Optimize message passing / hub handling |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **dsc** | Utility OK on this family |
| `coverage_mean` | **dsc** | Coverage holding |
| `tick_wall_us` | **fly_adj** | Sparse kernels on hubs |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
