---
id: B007
title: Prune active set without catastrophic forgetting
status: stub
tier: feature
measures: [F007]
updated: 2026-09-13
---

## Purpose
After pruning, confirm active count drops while dormant pool retains parameters; on a controlled task revisit that favored a pruned specialist, reactivation (or recovery with latent init) outperforms training from scratch on the same budget.

## What integrity looks like
Deleting parameters buys sparsity by discarding memory. Integrity is smaller active sets **and** recoverable competence—measured, not assumed.
