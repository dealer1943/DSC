# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035608Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=48
- scoreboard: fly_adj wins **4** · DSC wins **2**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s48_talk`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3658 | 3658 |
| `density` | 0.013981470156555773 | 0.013981470156555773 |
| `task_error` | 0.2708913777710513 | 0.27083320885871376 |
| `tick_wall_us` | 8722.853999998391 | 8298.35449999905 |
| `utility_mean` | 0.12463671288340003 | 0.1187002433478762 |
| `coverage_mean` | 0.456202056125385 | 0.45483277507345465 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00021510369248254992 | 0.00021511353826541448 |
| `E_tick` | 9.020548860514148e-05 | 9.482425979451424e-05 |

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
