---
id: F026
title: Sparse message gather (tick parity)
status: implemented
phase: DSC core
pairs_with: [F002, F023, F021]
updated: 2026-09-14
---

## Purpose
Replace dense `einsum` gathers with edge-list `np.add.at` when substrate density is low, cutting tick cost on preferential / FlyWire-adj graphs.

## Flags
`defaults.SPARSE_GATHER` (default true), `SPARSE_DENSITY_MAX` (~0.085).
