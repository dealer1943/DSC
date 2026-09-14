# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035535Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=46
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s46_base`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3677 | 3677 |
| `density` | 0.014054091242661448 | 0.014054091242661448 |
| `task_error` | 0.2759343096548874 | 0.2759338845124284 |
| `tick_wall_us` | 1013.9585000015217 | 1035.3750000007267 |
| `utility_mean` | 0.12693419249139495 | 0.12471819317680191 |
| `coverage_mean` | 0.45994524935064196 | 0.45989229215637384 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00021314642578499157 | 0.00021314649680559592 |
| `E_tick` | 0.0007729501824879794 | 0.000756962133288544 |

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
