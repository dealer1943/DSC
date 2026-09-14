---
id: F020
title: DSC development run (train → checkpoint → bench gate)
status: implemented
phase: DSC core
pairs_with: [F006, F010, F014, B006, B010, B016, R001]
updated: 2026-09-14
---

## Purpose
A **named, reproducible development protocol** that turns an abstract DSC MVP into a **developed checkpoint** worth comparing to FlyWire — not vibes, not a single `/tick`.

Operators (or CI) run one command / one documented sequence: seed → ticks → evolve cadence → save tip → integrity benches → B016 report. Pass/fail gates decide whether the tip is “developed enough” to claim efficiency vs FlyWire.

## Why it is fundamental
Without a development run contract, DSC stays a demo: someone ticks a few times, evolves once, and points at the UI. B016 then compares an **under-trained** artifact to a biological pack and either (a) “wins” by being small while useless, or (b) loses on task signal and looks like a failure of the whole idea. F020 freezes the **numerator** of efficiency: what counts as a developed DSC.

## Protocol v0 (freeze unless version bump)

| Step | Action | Default |
|------|--------|---------|
| 0 | Start from `python -m dsc` build **or** load `MODEL/active` | seed `42` |
| 1 | Warmup ticks | `T_warm=64` |
| 2 | Evolve cycles | `E=3` (`/evolve 3`) |
| 3 | Train ticks | `T_train=256` |
| 4 | Optional second evolve | `E2=2` |
| 5 | Eval ticks (no evolve) | `T_eval=64` |
| 6 | `/save dsc_dev_<utc>` + refresh `MODEL/active` | F014 |
| 7 | Run B006, B010 | must pass integrity gates |
| 8 | Run B016 profiles A,B,C,E | report under `BENCHMARKS/runs/` |
| 9 | R001 meta log append | one row per run |

**Protocol version:** `dev_run_v0` — recorded in every report.

## Pass / fail gates (v0)

| Gate | Rule |
|------|------|
| G1 task | `task_error` after T_eval ≤ `0.05` (lag-1 MSE harness) |
| G2 evolve | B006: elite utility ↑ by δ **and** typed_frac non-decrease; **fail on no-op** |
| G3 footprint | `disk_after ≤ 2× disk_before` **and** `E_disk ≥ 1e-7` (no vacuous `>0`) |
| G4 honesty | B016 Profile A present **and** no absolute-path/hostname leaks in JSON+MD; `--skip-b016` ⇒ **fail** |
| G5 dynamics | B016 Profile B: `dynamics=true` **and** finite `tick_wall_us`; `--skip-b016` ⇒ **fail** |

Fail any gate ⇒ exit code 1 from `python -m tools.dev_run` (does not block manual exploration).

**B016 note:** under profiles A,B,C,E (no Profile D), B016 `pass` for goal `efficiency_vs_flywire` is **false**; `pass_kind=static_null_demo` means the anatomy≠compute illustration completed. F020 still uses B016 artifacts for G4/G5 honesty/dynamics, not for claiming FlyWire efficiency parity.

## CLI

```bash
python -m tools.dev_run --seed 42 --out BENCHMARKS/runs/
```

Also callable as library: `tools.dev_run.run_protocol(...)`.

## Non-goals
- Replacing interactive `/tick` exploration  
- Training on FlyWire weights  
- Claiming biological equivalence  

## Acceptance
1. Doc + `tools/dev_run.py` exist and record `dev_run_v0`.  
2. Running the tool produces a checkpoint name + B006/B010/B016 artifacts.  
3. Gates G1–G5 evaluated and written into the run summary JSON.
