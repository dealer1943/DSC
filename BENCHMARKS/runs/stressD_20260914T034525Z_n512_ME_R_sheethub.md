# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T034525Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **4** · DSC wins **2**
- dsc_family: `sheet_hub_directed` · experiment: `F030_exp9_talk_ME_R_sheethub`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10120407201218773 | 0.10119781757297051 |
| `tick_wall_us` | 1050.6665000000748 | 1078.6455000000306 |
| `utility_mean` | 0.15583878154612194 | 0.1598477487615675 |
| `coverage_mean` | 0.4613005843961483 | 0.4623022820810712 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002547256371140626 | 0.0002547270838713927 |
| `E_tick` | 0.0008643055587206487 | 0.0008418911069498638 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **fly_adj** | Need stronger inductive bias / motifs |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **fly_adj** | More signal per edge: prune+coverage under skew |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
