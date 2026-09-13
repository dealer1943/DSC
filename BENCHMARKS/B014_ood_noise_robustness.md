---
id: B014
title: Out-of-distribution and noise robustness
status: stub
tier: system_llm_analog
inspired_by: HELM-style robustness / perturbation evaluations
updated: 2026-09-13
---

## Purpose
Measure task degradation under input noise, timing jitter, and mild covariate shift relative to the training distribution, including confidence or utility calibration under the same perturbations.

## Why this system-level check
Leaderboard accuracy on clean i.i.d. splits overstates reliability. Robustness probes ask whether the evolved state repertoire remains usable when the world is messy—aligned with real deployment, not only lab sequences.
