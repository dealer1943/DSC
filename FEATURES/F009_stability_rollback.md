---
id: F009
title: Stability checks and cycle rollback
status: stub
phase: 4
pairs_with: [B009]
updated: 2026-09-13
---

## Purpose
After each evolution cycle, verify reachability from the base state, interference (e.g., pairwise activation correlation below a merge/prune threshold), and non-degenerate transition probabilities; **rollback the cycle** if checks fail.

## Why it is fundamental
Evolutionary updates can destroy controllability (unreachable states), collapse diversity (near-duplicate cells), or freeze dynamics (0/1 transitions). Guardrailed rollback keeps search inside a viable dynamical regime instead of accepting every mutation that raises a short-horizon score.
