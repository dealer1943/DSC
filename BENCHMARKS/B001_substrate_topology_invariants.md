---
id: B001
title: Substrate topology invariants
status: stub
tier: feature
measures: [F001]
updated: 2026-09-13
---

## Purpose
Verify every generated substrate is directed, below the sparsity ceiling (edge density < 10%), seed-reproducible, and reports degree/sparsity metadata.

## What integrity looks like
A substrate that silently becomes dense or undirected changes the dynamical regime under test. This benchmark treats topology constraints as measurable properties of the artifact, not as comments beside the generator.
