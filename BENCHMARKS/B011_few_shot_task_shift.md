---
id: B011
title: Few-shot task shift adaptation
status: stub
tier: system_llm_analog
inspired_by: few-shot / in-context adaptation evaluations
updated: 2026-09-13
---

## Purpose
After training on task family A, expose a small number of episodes from related task family B and measure recovery speed and asymptotic accuracy versus a cold-started population with the same episode budget.

## Why this system-level check
Modern model evals ask whether competence transfers from thin evidence. For DSC, the analog is whether latent retention, plasticity, and evolution shorten adaptation under distribution shift—without retraining a new population from scratch.
