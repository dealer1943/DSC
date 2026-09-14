# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T030951Z_n512_ME_R_laminar`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **3** · DSC wins **3**
- dsc_family: `laminar_directed` · experiment: `F027_exp6_laminar_ME_R`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10131981648063557 | 0.10117564743301982 |
| `tick_wall_us` | 1018.958499999778 | 1050.958499999588 |
| `utility_mean` | 0.16622793440438527 | 0.16014130727689835 |
| `coverage_mean` | 0.4602378406759419 | 0.46296067868244023 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002546988664312632 | 0.0002547322123312454 |
| `E_tick` | 0.0008911073991999194 | 0.0008640877227419026 |

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
