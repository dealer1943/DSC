---
id: F008
title: Coverage absorption
status: stub
phase: 4
pairs_with: [B008]
updated: 2026-09-13
---

## Purpose
When a cell is pruned from the active set, redistribute the input patterns it dominated to surviving cells (e.g., widen basins / raise coverage of the strongest remaining responders) so responsibility for those inputs is not orphaned.

## Why it is fundamental
Pruning without absorption leaves holes in the input map: the population looks smaller but fails silently on regions the pruned cell owned. Absorption couples removal to continuity of function—size reduction that preserves competence.
