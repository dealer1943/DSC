# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T124332Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **6** · DSC wins **0**
- dsc_family: `sheet_hub_directed` · experiment: `R003_ME_R_sheet_hub_baseline`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10119116613971535 | 0.10117564743301982 |
| `tick_wall_us` | 1001.33350000009 | 996.562500000131 |
| `utility_mean` | 0.15570261277413194 | 0.16014130727689835 |
| `coverage_mean` | 0.4602710825911656 | 0.46296067868244023 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002547286224781748 | 0.0002547322123312454 |
| `E_tick` | 0.0009068981903977162 | 0.0009112527683519803 |

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
