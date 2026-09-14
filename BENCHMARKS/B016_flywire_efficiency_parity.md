---
id: B016
title: FlyWire efficiency parity (DSC vs biological comparison pack)
status: implemented
tier: system / comparison
measures: [F001, F005, F010, F011, F012]
related_research: [R002]
tool: `python -m tools.flywire_efficiency_bench`
updated: 2026-09-13
---

## Purpose
**Tool live.** Define a **reproducible efficiency comparison** between the active DSC runtime and the offline FlyWire pack so the project can claim — with numbers, not vibes — that DSC delivers **more useful dynamical work per unit resource** than treating FlyWire-scale anatomy as the compute substrate.

This file is the **contract**. Implementation: `tools/flywire_efficiency_bench/`. Profile D remains future.

## Goal statement (project intent)
**Be more efficient than FlyWire** on the axes that matter for a dynamic connectome: storage, wiring complexity carried at runtime, update cost, and task utility — without pretending a 128-node synthetic MVP “is” a fly brain.

Efficiency ≠ “fewer neurons.” Efficiency = **capability or integrity signal per footprint**, under matched protocols.

## Why this protects the design
Raw scale contests crown FlyWire every time (see R002). Without a normalized efficiency bench, the team can either (a) inflate DSC until it is inoperable, or (b) declare victory for being small while doing nothing useful. B016 forces **ratios**: task / coverage / novelty signals and operator-visible dynamics in the numerator; bytes, edges touched, and ops in the denominator.

## Axes (from R002) → metrics

Each axis becomes one or more **measurable fields**. The future tool emits a single JSON report plus a markdown table.

| # | Axis (R002) | Metric ID | Definition | Direction |
|---|-------------|-----------|------------|-----------|
| 1 | Nodes | `n_nodes` | Count of active graph nodes in the evaluated artifact | context (not alone scored) |
| 2 | Edges | `n_edges` | Count of directed edges used at runtime/eval | context |
| 3 | Density | `density` | `n_edges / (N*(N-1))` for directed simple graphs | context |
| 4 | Mean / median / max degree | `degree_mean`, `degree_median`, `degree_max` | In+out degree on the evaluated digraph | context; flag hubs |
| 5 | Disk footprint | `disk_bytes` | Bytes of the artifact needed to **reload and run** the evaluated mode (DSC: `MODEL/active` checkpoint set; FlyWire: declare profile — `edges_only` vs `full_pack`) | **lower better** for efficiency |
| 6 | Dynamics present | `dynamics` | `true` if per-tick state update exists | required for DSC; FlyWire static ⇒ use null / replay profiles below |
| 7 | Task harness | `task_id`, `task_error` | Harness name + scalar error (e.g. lag-1 MSE) after protocol | **lower error better** |
| 8 | Multi-term utility | `utility_mean`, `coverage_mean`, `novelty_mean`, `cost_mean` | From F005 terms (or declared N/A on static FlyWire) | interpret as vector |
| 9 | STEM / type mix | `stem_frac`, `type_entropy` | Fraction STEM-labeled; entropy of mixture winners | context until F004 |
| 10 | Load / sample cost | `load_wall_s`, `tick_wall_us`, `sample_hz_sustainable` | Wall time to load; median µs/tick; max Hz UI can sustain without drop | **lower load/tick better**; higher sustainable Hz better |
| 11 | Ops proxy | `edges_touched_per_tick`, `activation_l1` | Edges read in one tick; sum of \|activity\| | **lower for same task_error better** |
| 12 | Neuropil / biology extras | `n_neuropils`, `mean_syn_count` | FlyWire-only context fields; DSC → null | context |

### Derived efficiency scores (required)

The tool **must** compute these normalized scores so “more efficient than FlyWire” is falsifiable:

| Score ID | Formula (v0) | Meaning |
|----------|----------------|---------|
| `E_disk` | `task_utility_proxy / disk_bytes` | Useful signal per stored byte |
| `E_edge` | `task_utility_proxy / max(n_edges, 1)` | Useful signal per edge carried |
| `E_tick` | `task_utility_proxy / max(tick_wall_us, 1)` | Useful signal per microsecond of tick |
| `E_touch` | `task_utility_proxy / max(edges_touched_per_tick, 1)` | Useful signal per edge touched per tick |

Where `task_utility_proxy` for v0 is:

```text
task_utility_proxy = 1 / (1 + task_error)     # if task defined
                   = utility_mean               # fallback if only F005 available
                   = 0                          # if neither (static anatomy-only profile)
```

**Pass rule (project goal):** On the **matched protocol profile** below, DSC wins if it strictly exceeds FlyWire on **at least two of** `{E_disk, E_edge, E_tick, E_touch}` and does not lose `task_error` by more than a declared tolerance when both sides have a task binding.

Static FlyWire has no native DSC task — see profiles.

## Evaluation profiles (tool must implement)

### Profile A — `artifact_footprint` (always on)
Inventory-only: axes 1–5, 9–12 as applicable. No dynamics. Reproduces R002-style table.  
**Use:** baseline honesty, regression on pack size.

### Profile B — `dsc_native_dynamics` (DSC required)
Run DSC harness for `T` ticks (default T=256, seed fixed). Record task_error, utility terms, tick_wall_us, edges_touched_per_tick, sustainable sample Hz probe.  
**Use:** primary efficiency claim for DSC alone over time (vs its own prior revision).

### Profile C — `flywire_static_null` (FlyWire required)
Load FlyWire edges (default: proofread connections only). No tick dynamics. `task_utility_proxy = 0` unless a **declared adapter** maps a subgraph into the DSC harness (Profile D).  
**Use:** shows FlyWire’s E_* collapse on dynamics scores — anatomy is not free compute.

### Profile D — `matched_subgraph_swap` (F021 — in progress)
**Tool:** `python -m tools.flywire_stress`. Extract a FlyWire subgraph with `n_nodes ≈ N_dsc` (or fixed N ∈ {128,512,2048}), degree-matched or neuropil-focused, wire it as DSC substrate **without** changing harness hyperparameters. Run Profile B on (i) synthetic ER DSC and (ii) FlyWire-derived substrate.  
**Use:** the fairest “efficiency vs FlyWire wiring” test — same software, different hardware topology.

### Profile E — `operator_load` (UI / F012 / F013)
Measure load_wall_s and progress completeness for `/load dsc` vs `/load flywire` (pack **names** only in logs — no filesystem path leaks).  
**Use:** demo and human-efficiency axis.

## Tool blueprint (`tools/flywire_efficiency_bench` — future)

### CLI sketch
```bash
python -m tools.flywire_efficiency_bench \
  --dsc MODEL/active \
  --flywire MODELS/fly/flywire_v783 \
  --profiles A,B,C,E \
  --seed 42 \
  --ticks 256 \
  --out BENCHMARKS/runs/B016_<utc>.json
```

### Inputs
| Input | Required | Notes |
|-------|----------|--------|
| DSC active dir | yes for B/D | manifest + checkpoint; display name `active` |
| FlyWire pack dir | yes for A/C/D/E | edges feather minimum for C |
| profiles | yes | subset of A–E |
| seed, ticks | yes for B/D | recorded in report |
| N_match | for D | default 128 |

### Outputs
1. **JSON report** — all metric IDs + derived E_* + profile + versions  
2. **Markdown table** — side-by-side DSC vs FlyWire (R002-compatible columns + E_* rows)  
3. **Exit code** — `0` pass, `1` fail goal rule, `2` incomplete inputs  

### Report schema (minimum)
```json
{
  "bench": "B016",
  "schema": 1,
  "utc": "...",
  "goal": "efficiency_vs_flywire",
  "profiles_run": ["A", "B", "C", "E"],
  "dsc": { "revision": "r1-n128-e1276", "metrics": {}, "E": {} },
  "flywire": { "pack": "flywire_v783", "profile_edges": "proofread_connections", "metrics": {}, "E": {} },
  "comparisons": { "E_disk_winner": "dsc", "E_edge_winner": "dsc", "...": "..." },
  "pass": true,
  "notes": []
}
```

### Privacy / demo constraint
User-facing strings and exported tables use **pack display names** (`active`, `flywire_v783`) never absolute paths (same rule as F012 path scrub).

## Protocol constants (freeze unless version bump)
| Constant | v0 value |
|----------|----------|
| DSC density guard | &lt; 0.10 (B001) |
| Default ticks | 256 |
| Default seed | 42 |
| FlyWire default file | `proofread_connections_783.feather` |
| task_error tolerance (pass rule) | 10% relative if both have tasks |
| Schema | 1 |

Bump `schema` when formulas change; keep old reports readable.

## Integrity rules
1. **Never score node count alone** as efficiency.  
2. **Declare which FlyWire bytes** enter `disk_bytes` (`edges_only` vs `full_pack`).  
3. **Static vs dynamic** must not be silently mixed — Profile C vs B are separate.  
4. **Matched topology claims** require Profile D; Profiles A–C alone do not prove “better than fly wiring.”  
5. **Seed and revision** always recorded; B015-style multi-seed optional later.  
6. Progress / load metrics must not block headless CI (optional UI probe).

## Relation to other benches
| Bench | Relation |
|-------|----------|
| B001 | Topology invariants on whichever substrate Profile D uses |
| B010 | Task vs footprint within DSC; B016 adds cross-artifact E_* |
| B015 | Multi-seed stability of E_* scores (later) |
| R002 | Human baseline snapshot; B016 automates and extends it |
| F011 | FlyWire remains comparison substrate, not DSC bootstrap |

## Acceptance for this **spec** (now)
- [x] Axes from R002 mapped to metric IDs  
- [x] Derived E_* scores and pass rule defined  
- [x] Profiles A–E specified  
- [x] Future tool I/O + privacy constraint sketched  

## Acceptance for the **future tool** (later)
- [x] CLI runs profiles A,B,C,E on current `MODEL/active` + local FlyWire pack  
- [x] Emits JSON + markdown; exit codes as specified  
- [x] Path-safe display names only  
- [x] Documented in root README under Benchmarks  

## Non-goals
- Implementing the tool in this slice  
- Training FlyWire weights as an LM  
- Replacing biological interest of FlyWire with “DSC is bigger”

## One-line claim the tool must be able to support or refute
**Per byte, per edge, and per tick, the DSC runtime produces more harness-defined useful signal than the FlyWire pack under declared profiles — especially when topology is matched (Profile D).**


## Implementation notes (2026-09-14)
- CLI: `PYTHONPATH=. python -m tools.flywire_efficiency_bench --profiles A,B,C,E --seed 42 --ticks 256`
- Reports land in `BENCHMARKS/runs/B016_<utc>_s<seed>.{json,md}`
- **Honesty:** with Profile C (`task_utility_proxy=0` on static FlyWire), DSC almost always wins ≥2 E_* scores. That refutes “anatomy alone is compute,” **not** “DSC wiring beats FlyWire wiring.” Profile D (matched subgraph) is required for the latter claim.

## Pass semantics (post-adversarial 2026-09-14)
- `pass: true` **only** when both sides have a task utility proxy (Profile D / tasked FlyWire) and ≥2 `E_*` wins with `proxy ≥ proxy_min`.
- Profiles A,B,C,E alone → `pass: false`, `pass_kind: static_null_demo`, `claim_level: static_null_asymmetry`. Exit 0 means the **demo completed**, not that DSC beat FlyWire wiring.
- Null-opponent `E_*` winners are `na_static_null` and do **not** increment `dsc_E_wins`.


See FEATURES/F021_flywire_matched_stress.md for the stress-test development loop.
