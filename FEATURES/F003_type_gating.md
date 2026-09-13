---
id: F003
title: Differentiable type gating
status: implemented
phase: 2
pairs_with: [B003]
updated: 2026-09-13
---

## Purpose
Give STEM (and partially differentiated) cells a **learned mixture** over type behaviors (attractor, latent, modulatory, modular, metastable) via a gating network whose weights are trainable and differentiable.

## Why it is fundamental
Emergence requires a continuous path from “can behave like any type” to “committed type.” Soft gating is that path. Hard assignment at birth, or non-differentiable switching, removes the gradient signal that lets utility shape type selection.
