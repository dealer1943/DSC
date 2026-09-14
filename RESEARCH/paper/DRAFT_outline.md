---
title: "Dynamic State Connectomes beat matched FlyWire wiring on efficiency (draft outline)"
status: outline
updated: 2026-09-14
repo: https://github.com/dealer1943/DSC
---

## One-sentence claim (v0)
Under a matched-N, same-software Profile D protocol, a structured DSC substrate (preferential + hub-aware messaging + sparse gather) achieves equal-or-better temporal-task utility than FlyWire-derived wiring **while carrying a much smaller deployable footprint than the full FlyWire pack** — across multiple neuropils, including optic.

## What we are NOT claiming
- DSC is not a biological model of *Drosophila* cognition.
- We do not train on or replace the full ~10^5-node FlyWire graph as the runtime substrate.
- “Beat the fly” here means **beat FlyWire-shaped connectivity in a controlled efficiency stress**, plus footprint advantage vs the offline biological pack — not AGI-in-a-fly.

## Why it would be an innovation
Biology gives existence proofs for compact, dynamic, sparse computation. If a *synthetic* evolving connectome can match or exceed biological wiring efficiency on a shared harness **and** ship as a ~100KB–MB checkpoint instead of a multi-GB anatomy pack, that is a systems result: **dynamic connectome substrates as an efficiency class**, not just another GNN.

## Evidence package (map to repo)
| Paper need | Artifact |
|------------|----------|
| Baseline footprint | R002, B016 Profile A/C |
| Fair wiring stress | F021 / B016 Profile D, `tools/flywire_stress` |
| Ablation ladder | `BENCHMARKS/runs/stress_ledger.jsonl` (ER → preferential → hub-aware → absorb → sparse → hard harness) |
| Generalization | Multi-neuropil panel (GNG, ME_*, LO_*, AVLP_*) |
| Reproducibility | seed 42, dated `stressD_<utc>_…` JSON/MD, offline packs |

## Suggested structure
1. Intro — efficiency vs scale; dynamic vs static connectomes  
2. Related — FlyWire, connectome analytics, reservoir/liquid state, sparse graphs  
3. DSC — state cells, types, evolve/prune, operator console (brief)  
4. Methods — Profile D protocol; substrate families; hub-aware; sparse gather; harness  
5. Results — N=128/512; ablation ledger; multi-neuropil; footprint table  
6. Discussion — what “beat FlyWire” means; limits; scaling to 2k/full-pack proxies  
7. Conclusion — dynamic connectomes as an efficiency substrate  


## First multi-neuropil panel (N=512, hard harness, preferential+hub+sparse)
Recorded in `BENCHMARKS/runs/panel_summary_512_42.json`:

| Neuropil | Winner | Score (fly–DSC) | Note |
|----------|--------|-----------------|------|
| GNG | **DSC** | 0–6 | Prior sweet spot |
| AVLP_R | **DSC** | 2–4 | Travels beyond GNG |
| LO_R | Fly | 5–1 | Optic pressure |
| ME_R | Fly | 6–0 | Prestige optic fight — main gap |

**Paper implication:** innovation is real on some biological regimes; **optic neuropils are the remaining mountain**. Next methods work should target laminar / retinotopic inductive bias, not more GNG tuning.

## Open experimental todos before submission
- [ ] Multi-neuropil N=512 hard-harness panel (GNG, ME_R, LO_R, AVLP_R)  
- [ ] Optic-first deep dive (ME_R ± ME_L) with ablations frozen  
- [ ] Footprint table: DSC tip bytes vs FlyWire edges_only vs full_pack  
- [ ] Multi-seed (B015-style) on best stack  
- [ ] Failure cases (where fly-adj still wins)  

## Working title candidates
- “Smaller than anatomy: dynamic connectomes vs matched FlyWire wiring”  
- “Efficiency beyond scale: synthetic connectomes under FlyWire-matched stress”  
