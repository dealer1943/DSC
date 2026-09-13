---
id: F011
title: Offline FlyWire comparison substrate
status: decided
phase: substrate-validation
priority: P0
updated: 2026-09-13
supersedes: zebrafish / Fish1 CAVE path
pairs_with: [B001, B010]
---

## Purpose
Select a **published biological connectome** that can sit beside the DSC’s synthetic substrate as an offline comparison graph—same machine, no live auth—so later null-model and topology-swap experiments are reproducible after a cutoff.

## Decision
**Use FlyWire (FAFB v783 female adult whole-brain connectivity) as the primary biological comparison substrate.**  
**Do not pursue zebrafish (mapZebrain proximity graphs or Fish1 EM via CAVE) for this project path.**

## Tradeoff

| Axis | FlyWire (chosen) | Zebrafish / Fish1 (dropped) |
|------|------------------|-----------------------------|
| Offline | Yes — Zenodo connectivity pack (~10.6 GB) | Fish1 requires CAVE + Google token; not offline-first |
| Pack size | ~10.6 GB (≈852 MB aggregated edges usable alone) | Fish1 EM volume ~hundreds of TB; synapses queried online |
| Biological richness | Adult fly whole brain; complex, well-documented | Larval vertebrate; scientifically richer in many ways |
| Role in DSC MVP | Comparison / validation substrate | Same aspirational role, worse ops fit |

Zebrafish (especially Fish1) has **more potential** as a long-horizon biology story: vertebrate scale, CLEM, richer systems neuroscience questions. That potential does **not** match the current deliverable. DSC’s near-term need is a **fixed, offline graph to compare against**—not the most ambitious organismal resource. FlyWire is more than enough complexity for that job while staying downloadable and auth-free.

## Why FlyWire fits first principles here
1. **Mechanism before biology** — MVP dynamics are proven on synthetic sparse directed graphs; biology is a swap-in, not the bootstrap.  
2. **Reproducibility** — Successors must reload the same substrate without accounts, tokens, or admin approval.  
3. **Honest scope** — Comparison substrate ≠ flagship neuroscience platform. Prefer a complete offline artifact over a gated frontier dataset.  
4. **Complexity density** — Whole-brain fly wiring already stresses topology, sparsity, and signed/NT-aware edges; sufficient to stress-test DSC claims.

## Local assets
- Target: `MODELS/fly/flywire_v783/` (Zenodo FlyWire connectivity release).  
- Already present: `MODELS/fly/male_cns_v1.0/` (MaleCNS) and `MODELS/fly/hemibrain_v1.2.1/` as additional fly baselines.  
- Removed: `MODELS/zebrafish/` (mapZebrain path deleted under this decision).

## Non-goals
- CAVE authentication workflows  
- Fish1 bulk EM or synapse materialization  
- Claiming FlyWire is “better biology” than zebrafish in absolute terms—it is the better **offline comparison** choice for DSC right now

## Acceptance
- [x] Decision recorded with tradeoff table  
- [x] Zebrafish local path removed  
- [x] FlyWire pack present under `MODELS/fly/flywire_v783/` (~10.60 GB, MD5-verified)
