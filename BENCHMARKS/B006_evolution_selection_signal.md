---
id: B006
title: Evolution loop selection signal
status: implemented
tier: feature
measures: [F006]
updated: 2026-09-13
---

## Purpose
Over multiple cycles, verify that higher-utility lineages increase in representation, parameter mutations explore locally, rare type mutations occur at configured rates, and hybrid children appear only from eligible parents—under fixed seeds.

## What integrity looks like
An “evolution” loop that does not preferentially retain high-utility structure is random churn. This benchmark tests that selection pressure is real, measurable, and rate-faithful.


## Runnable
```bash
PYTHONPATH=. python -m tools.benches.b006_selection --cycles 3 --seed 42
```
Pass: after post-tick re-score, (mean OR elite utility ↑ by δ) AND typed_frac non-decrease; **fail on no-op**. Runs on a temp copy of the tip.
