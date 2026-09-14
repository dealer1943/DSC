# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035549Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=48
- scoreboard: fly_adj wins **6** · DSC wins **0**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s48_base`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3658 | 3658 |
| `density` | 0.013981470156555773 | 0.013981470156555773 |
| `task_error` | 0.2709126623663396 | 0.2706624084075496 |
| `tick_wall_us` | 1111.7085000016402 | 1109.6670000014797 |
| `utility_mean` | 0.12120644253386847 | 0.12511331618503746 |
| `coverage_mean` | 0.455624434261523 | 0.4557004377112863 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002151000900359184 | 0.0002151424534903744 |
| `E_tick` | 0.0007077719828086486 | 0.0007092137504915801 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **fly_adj** | Optimize message passing / hub handling |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **fly_adj** | Sparse kernels on hubs |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
