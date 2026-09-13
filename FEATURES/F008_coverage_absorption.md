---
id: F008
title: Coverage absorption
status: implemented
phase: 4
pairs_with: [B008]
updated: 2026-09-13
slice: S005
---

## Purpose
When a cell is pruned, redistribute the niche it owned to surviving cells so responsibility is not orphaned.

## Algorithm
Before overwriting a victim (`dsc/absorb.py`):
- Score survivors by gate cosine similarity + activity
- Blend victim `type_weights` / `bias` / partial `gate_logits` into top `ABSORB_TOP` with `ABSORB_BLEND`
