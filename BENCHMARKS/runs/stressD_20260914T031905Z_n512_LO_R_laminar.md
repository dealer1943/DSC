# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T031905Z_n512_LO_R_laminar`
- N=512 neuropil=`LO_R` seed=42
- scoreboard: fly_adj wins **3** · DSC wins **3**
- dsc_family: `laminar_directed` · experiment: `sweep_20260914T031845Z_LO_R_laminar`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 11341 | 11341 |
| `density` | 0.04334714408023484 | 0.04334714408023484 |
| `task_error` | 0.10128713533603734 | 0.1012431361681741 |
| `tick_wall_us` | 1573.2295000017161 | 1588.8124999978713 |
| `utility_mean` | 0.1681886694295025 | 0.15797971237504216 |
| `coverage_mean` | 0.4616985361920398 | 0.4620923431813871 |
| `latent_n` | 64 | 64 |
| `E_edge` | 8.006599101850123e-05 | 8.006918998234788e-05 |
| `E_tick` | 0.0005771747886368975 | 0.0005715367191478063 |

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
