---
id: B003
title: Type gating differentiability and mixture use
status: stub
tier: feature
measures: [F003]
updated: 2026-09-13
---

## Purpose
Show that STEM behavior is a soft mixture over type heads, that gate weights receive usable gradients under the task loss/utility, and that hard one-hot type assignment is not required for forward computation in the plastic regime.

## What integrity looks like
Non-differentiable or bypassed gating makes type selection an external schedule. This benchmark ties learning signal to the mixture mechanism itself.
