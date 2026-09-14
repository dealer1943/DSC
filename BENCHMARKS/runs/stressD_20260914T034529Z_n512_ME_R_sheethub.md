# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T034529Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **6** · DSC wins **0**
- dsc_family: `sheet_hub_directed` · experiment: `F030_exp9_talk_bilayer_ME_R_sheethub`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10123409707781317 | 0.10118824447767887 |
| `tick_wall_us` | 1320.2080000001006 | 1287.9375000001137 |
| `utility_mean` | 0.15640283860612536 | 0.1613371866134925 |
| `coverage_mean` | 0.45951554609209855 | 0.4622467898267675 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00025471869203854135 | 0.0002547292983217008 |
| `E_tick` | 0.0006878250526563471 | 0.0007050885221656976 |

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
