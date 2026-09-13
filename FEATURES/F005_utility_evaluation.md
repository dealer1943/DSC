---
id: F005
title: Multi-term utility evaluation
status: implemented
phase: 3
pairs_with: [B005]
updated: 2026-09-13
---

## Purpose
Score each active cell with a **composite** utility: task contribution (prefer counterfactual / masking marginal), coverage bonus, novelty bonus, minus compute cost—typically as an exponential moving average.

## Why it is fundamental
Task performance alone rewards monopoly states and erases diversity. Coverage forces partitioning of the input space; novelty penalizes redundant clones; cost keeps the footprint compact. Selection without this structure converges to a single do-everything cell and fails the compactness success criterion.
