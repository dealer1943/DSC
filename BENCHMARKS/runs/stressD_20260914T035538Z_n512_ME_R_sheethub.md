# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035538Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=46
- scoreboard: fly_adj wins **6** · DSC wins **0**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s46_talk`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3677 | 3677 |
| `density` | 0.014054091242661448 | 0.014054091242661448 |
| `task_error` | 0.27592491358178695 | 0.27591716068211836 |
| `tick_wall_us` | 1178.4375000019054 | 1172.8545000018187 |
| `utility_mean` | 0.12453801470863045 | 0.12534096891681634 |
| `coverage_mean` | 0.4591816244988647 | 0.46090854403411907 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00021314799542233973 | 0.00021314929058089232 |
| `E_tick` | 0.0006650714859011835 | 0.0006682414071521452 |

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
