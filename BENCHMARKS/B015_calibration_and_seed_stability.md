---
id: B015
title: Calibration and seed stability
status: stub
tier: system_llm_analog
inspired_by: calibration metrics and multi-seed reporting in modern LLM evals
updated: 2026-09-13
---

## Purpose
Across fixed seeds, report mean/variance of task and footprint metrics, plus calibration of predictive confidence (or normalized utility) against empirical correctness; flag brittle hyperparameter cliffs.

## Why this system-level check
Single-seed hero runs are common failure mode in stochastic systems. Stability and calibration make results comparable, reproducible, and honest about uncertainty—the same bar contemporary model reports are held to.
