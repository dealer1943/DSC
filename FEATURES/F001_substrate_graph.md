---
id: F001
title: Synthetic substrate graph
status: implemented
phase: 1
pairs_with: [B001]
updated: 2026-09-13
---

## Purpose
Provide the topological “hardware” on which state cells operate: a configurable, reproducible, **sparse** (<10% edge density), **directed** synthetic graph (Erdős–Rényi, Watts–Strogatz, or Barabási–Albert).

## Why it is fundamental
Connectome dynamics are shaped by wiring. Starting from a fully connected or undirected substrate collapses diversity and hides whether later mechanisms work. A synthetic sparse directed graph isolates evolutionary mechanisms from biological topology and gives a clean baseline before any organismal connectome is introduced.

## Later (not this stub)
Generator API, sparsity enforcement, export formats, degree-preserving rewiring hook for null models.

## Implementation
- Code: `dsc/substrate.py` · defaults: `dsc/defaults.py` · blueprint: `BLUEPRINT/01_substrate.md`
- Frozen: N=128, ER directed p=0.08, seed=42
