---
id: B013
title: Long-horizon dependency retention
status: stub
tier: system_llm_analog
inspired_by: long-context retention / needle-in-haystack style probes
updated: 2026-09-13
---

## Purpose
Place a cue early in a long sequence and require correct use after a variable delay; plot accuracy versus horizon while holding compute/footprint reporting constant.

## Why this system-level check
Long-context evals separate models that still “have” early information from those that only look local. For a state connectome, horizon curves reveal whether attractors/latents persist or wash out.
