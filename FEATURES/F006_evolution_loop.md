---
id: F006
title: Evolution loop
status: stub
phase: 3
pairs_with: [B006]
updated: 2026-09-13
---

## Purpose
Run periodic population update cycles (every N task steps): evaluate → select/prune → reproduce (clone top-K) → mutate parameters (and rarely type) → optional hybridization between high-utility different types.

## Why it is fundamental
Dynamic states are not a fixed network trained once. Generational pressure is how the connectome discovers and refreshes its repertoire. Without a closed loop of evaluation and variation, gating and differentiation have nothing to optimize against over time.
