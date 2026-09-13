---
id: B009
title: Stability checks and rollback efficacy
status: stub
tier: feature
measures: [F009]
updated: 2026-09-13
---

## Purpose
Inject controlled post-cycle failures (unreachable states, correlation above threshold, collapsed transitions) and verify detection plus full rollback to the pre-cycle population snapshot; confirm clean cycles commit.

## What integrity looks like
Guardrails that only log warnings still accept broken dynamics. Efficacy means failed cycles do not persist in the live population.
