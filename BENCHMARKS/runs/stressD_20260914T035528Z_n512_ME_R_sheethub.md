# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035528Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=45
- scoreboard: fly_adj wins **3** · DSC wins **3**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s45_base`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 4295 | 4295 |
| `density` | 0.016416187622309196 | 0.016416187622309196 |
| `task_error` | 0.29560864236845846 | 0.29531162968315283 |
| `tick_wall_us` | 1050.457999999921 | 1065.6249999989598 |
| `utility_mean` | 0.11582206345589693 | 0.10891923675266899 |
| `coverage_mean` | 0.45965471966652616 | 0.4624841160056942 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.00017970617296466168 | 0.00017974737927500052 |
| `E_tick` | 0.0007347633250289683 | 0.0007244715486093897 |

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
