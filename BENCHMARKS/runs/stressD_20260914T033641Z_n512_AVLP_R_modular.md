# Profile D stress — `stress_d_v0`

- run: `stressD_20260914T033641Z_n512_AVLP_R_modular`
- N=512 neuropil=`AVLP_R` seed=42
- scoreboard: fly_adj wins **3** · DSC wins **3**
- dsc_family: `modular_directed` · experiment: `F029_exp8_bilayer_AVLP_modular`

## Side-by-side

| metric | DSC | FlyWire-adj |
|--------|-----|-------------|
| `n_nodes` | 512 | 512 |
| `n_edges` | 24854 | 24854 |
| `density` | 0.09499602495107633 | 0.09499602495107633 |
| `task_error` | 0.10129712849755086 | 0.10127647595554685 |
| `tick_wall_us` | 2142.7080000000487 | 2148.2500000002956 |
| `utility_mean` | 0.16223784271306815 | 0.15500108913213437 |
| `coverage_mean` | 0.4622944069457613 | 0.4646973507835811 |
| `latent_n` | 64 | 64 |
| `E_edge` | 3.6534166118057426e-05 | 3.653485125336795e-05 |
| `E_tick` | 0.0004237722380735866 | 0.0004226869279884009 |

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
