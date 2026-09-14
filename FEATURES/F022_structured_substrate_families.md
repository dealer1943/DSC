---
id: F022
title: Structured substrate families (beyond ER)
status: implemented
phase: DSC core
pairs_with: [F001, F021, B016]
updated: 2026-09-14
---

## Purpose
Give DSC wiring inductive bias beyond Erdős–Rényi so Profile D stress (FlyWire-matched) can improve without copying biology wholesale.

## Families (v0)
| id | Idea |
|----|------|
| `erdos_renyi_directed` | MVP baseline |
| `preferential_directed` | Heavy-tailed hubs (experiment 1) |
| `modular_directed` | Block / neuropil-ish modules (experiment 2) |

## Eval protocol
One family change at a time → `tools.flywire_stress --n 512 --dsc-family <id>` → append `BENCHMARKS/runs/stress_ledger.jsonl`.
## Shipped
Families in `dsc/substrate.py`: ER, preferential, modular, laminar, sheet_hub; selected via `--dsc-family`.
