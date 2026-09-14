# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T034652Z_n512_ME_R_sheethub`
- N=512 neuropil=`ME_R` seed=42
- scoreboard: fly_adj wins **2** · DSC wins **4**
- dsc_family: `sheet_hub_directed` · experiment: `F030_exp9b_talk_ME_R_thresh02`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 3565 | 3565 |
| `density` | 0.013626009050880626 | 0.013626009050880626 |
| `task_error` | 0.10122560858471996 | 0.10123896424465731 |
| `tick_wall_us` | 1124.6670000002457 | 1126.0005000000017 |
| `utility_mean` | 0.15590070258213523 | 0.15917120091613102 |
| `coverage_mean` | 0.4589754828389041 | 0.46169592608744886 |
| `latent_n` | 64 | 64 |
| `E_edge` | 0.0002547206554671442 | 0.0002547175662534822 |
| `E_tick` | 0.0008074204513337465 | 0.0008064544586735643 |

## Gaps → development targets

| metric | winner | hint |
|--------|--------|------|
| `task_error` | **dsc** | DSC holding on task — push scale or harder harness |
| `E_tick` | **dsc** | DSC cheaper/tick — keep while raising task |
| `E_edge` | **dsc** | Good edge efficiency — test at larger N |
| `utility_mean` | **fly_adj** | Retune F005 / type emergence for hubs |
| `coverage_mean` | **fly_adj** | Coverage collapse under prune/skew — strengthen F008 absorb |
| `tick_wall_us` | **dsc** | DSC already fast |

## Notes

- Same DSC software + harness; only adjacency family differs.
- Not biological equivalence — inductive-bias stress test.
- Development backlog = rows where winner=fly_adj.
