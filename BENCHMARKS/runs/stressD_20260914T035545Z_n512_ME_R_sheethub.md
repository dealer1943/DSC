# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T035545Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=47
- scoreboard: fly_adj wins **3** · DSC wins **3**
- dsc_family: `sheet_hub_directed` · experiment: `F030_multiseed_ME_R_s47_talk`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3514 | 3514 |
| `density` | 0.013431078767123288 | 0.013431078767123288 |
| `task_error` | 0.4159546374961718 | 0.41550885901209866 |
| `tick_wall_us` | 1137.7500000016028 | 1145.0209999992467 |
| `utility_mean` | 0.12680105122092367 | 0.1220443483685868 |
| `coverage_mean` | 0.4536588796656272 | 0.45429290485794194 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002009781770201 | 0.00020104146998115315 |
| `E_tick` | 0.0006207315438783885 | 0.000616984077597037 |

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
