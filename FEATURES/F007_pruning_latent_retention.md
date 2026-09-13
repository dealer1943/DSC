---
id: F007
title: Pruning with latent retention
status: stub
phase: 4
pairs_with: [B007]
updated: 2026-09-13
---

## Purpose
Remove low-utility cells from the **active** set after sustained failure (utility below threshold for M consecutive evaluations), while **moving parameters into a dormant/latent pool** instead of destroying them.

## Why it is fundamental
Active-set sparsity is required for a compact footprint, but hard deletion is irreversible forgetting. Latent retention preserves the option to reactivate under task change—adaptation without rebuilding from noise. Compactness and continuity are the same design problem.
