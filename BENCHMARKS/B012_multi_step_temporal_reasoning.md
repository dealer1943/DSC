---
id: B012
title: Multi-step temporal reasoning suite
status: stub
tier: system_llm_analog
inspired_by: multi-step reasoning suites (e.g. math / chain-style benchmarks)
updated: 2026-09-13
---

## Purpose
Evaluate accuracy on sequences whose correct output depends on composing several intermediate temporal relations (delayed XOR-style dependencies, hierarchical motifs), reported by depth/number of steps.

## Why this system-level check
Reasoning benchmarks stress compositional structure, not single-frame pattern match. DSC claims dynamic state machinery; this suite asks whether those states support multi-step dependencies rather than shallow lag-1 memorization.
