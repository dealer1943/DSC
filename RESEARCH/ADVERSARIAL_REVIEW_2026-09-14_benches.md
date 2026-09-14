# ADVERSARIAL_REVIEW — DSC bench tooling (B016 / F020 / B006 / B010 / R001)

**Scope:** read-only review of files under `/workspace/dsc-review/` as listed in the task brief.  
**Date:** 2026-09-14  
**Stance:** attack design + code; assume hostile CI cherry-picking and marketing-ready `pass: true`.

---

## Executive summary

- **B016 `pass: true` is structurally overclaiming.** Profile C zeros FlyWire `task_utility_proxy`, so every DSC `E_*` with a tiny positive numerator beats FlyWire zeros; `goal_two_of_four` is then almost automatic. Without Profile D (matched topology + shared task), a green `pass` is **not** evidence of efficiency parity vs FlyWire.
- **F020 gates G3–G5 are soft / gameable.** G3 accepts any `E_disk > 0` (always true for finite error); G4/G5 only check profile keys exist and **auto-pass when `--skip-b016`**; they do not enforce the F020 doc (path-leak check, finite `tick_wall_us`).
- **B006 selection gate accepts identity / non-regression.** `utility_ok OR typed_ok` with “non-decreasing typed_frac” means a no-op evolve can pass; G2 inherits this.
- **Destructive / non-isolated mutation risk.** B006 calls `rt.evolve` on the loaded tip with no copy; F020’s “refresh `MODEL/active`” after `save_named` is a no-op (`pass`), so active refresh is hope-based.
- **Exit codes, scrub, and metric honesty have holes.** B016 can return exit `0` while `pass: false` if `dsc_E` is empty; R001 scrub misses most absolute paths / Path objects; `E_*` treats `ε > 0` as a decisive win over anatomy-null FlyWire.

---

## Findings (ranked by severity)

| ID | Severity | Location | Why it matters | Concrete fix |
|----|----------|----------|----------------|--------------|
| F1 | **blocker** | `tools/flywire_efficiency_bench/bench.py` — `run_bench` pass rule (~L319–351), `compare_E`, Profile C | Profile C sets FlyWire proxy=`0` → all `fly_E[*]=0`. Any DSC with finite `task_error` gets `proxy=1/(1+err)>0` and wins **all four** `E_*` (including tick/touch where FlyWire has no dynamics). `pass = goal_two_of_four` therefore greenlights “efficiency_vs_flywire” without Profile D. MD notes admit anatomy≠compute, but the boolean `pass` and goal string do not. Marketing / CI will quote `pass: true`. | (1) Split flags: `pass_static_null_demo` vs `pass_matched_topology` (requires Profile D). (2) Default `pass` for B016 **false** (or `null`) until Profile D exists. (3) Require absolute utility floor + non-null FlyWire task proxy before any `E_*_winner=dsc` counts toward the goal. (4) Rename goal / add `claims: ["anatomy_null_only"]` when only A/B/C/E run. |
| F2 | **blocker** | Same — `_E_scores` + `compare_E` | Metric honesty: numerator can be tiny (`task_error≈huge` still yields proxy>0; or near-chance proxy) and still “win” every axis against zeros. No magnitude, confidence, or “meaningfully better” threshold. Denominator asymmetry (DSC small disk vs FlyWire feather) further inflates `E_disk` wins that are size theater, not compute efficiency. | Require `proxy >= proxy_min` (e.g. task_error≤gate) before scoring wins; compare only within Profile D; report ratios with CI / bootstrap; forbid declaring winners when opposing proxy is intentionally null. |
| F3 | **high** | `tools/dev_run.py` G3 (~L79–81); `FEATURES/F020_...md` G3 | Spec: disk ≤2× baseline **or** `E_disk` *improved vs pre-run*. Code: `disk <= 2*65000 or E_disk > 0`. `E_disk = proxy/max(disk,1)` is **>0 whenever proxy>0**, i.e. almost always. G3 is vacuous. Hardcoded `65_000` is unverified magic. | Measure `E_disk` / disk before the train loop; require real improvement **or** hard byte cap; drop `> 0` clause; document measured baseline tip bytes in protocol. |
| F4 | **high** | `tools/dev_run.py` G4/G5 (~L82–83) | Spec G4: Profile A + **no path leaks**. Spec G5: Profile B `dynamics=true` **and** `tick_wall_us` finite. Code only checks key presence / `dynamics`. **`skip_b016` ⇒ G4=G5=True`** — CI can skip the honesty/dynamics benches and still fully pass F020. | Never auto-pass G4/G5 on skip (fail or mark `gates_na` and force `pass=false`). Assert `tick_wall_us` finite; run a path-scrub / deny-absolute-path check on B016 JSON+MD. |
| F5 | **high** | `tools/benches/b006_selection.py` (~L27–30); F020 G2 | `passed = utility_ok or typed_ok` with `typed_ok = after_typed >= before_typed - 1e-6`. Identity evolve (no change) ⇒ both sides hold ⇒ **pass**. Elite-OR-mean further softens utility. G2 does not prove a selection signal. | Require strict improvement on a primary metric (e.g. elite utility ↑ by δ **and** typed non-decrease), or Wilcoxon / paired test over seeds; fail on no-op; remove OR-typed-as-sole-pass. |
| F6 | **high** | `bench.py` `run_bench` exit_hint (~L352–358, `main` L487) | Logic: incomplete→2; `elif not passed and dsc_E`→1; **else→0**. If `pass=false` because comparisons empty (B skipped, only A/E, missing dyn) but `dsc_E={}`, exit is **0**. Silent green CI on failed/incomplete efficiency claim. | `exit_hint = 0 if passed else (2 if incomplete else 1)`; treat missing required profiles as incomplete. |
| F7 | **high** | `dsc/meta/manager.py` `_scrub` | Privacy contract: display names only. Scrub only replaces literal `"Mac.home.local"` and strings starting with `/Users/` or `/home/` → basename. Misses `/workspace`, `/var`, `/opt`, `/tmp`, Windows paths, hostnames, paths mid-string. **`Path` objects pass through scrub unchanged**; `json.dumps(..., default=str)` then emits absolute paths → leak in JSONL. | Normalize all values to path-safe strings before dump; reject/scrub any `/` or `\` path-like token; allowlist display fields; never `default=str` on raw `Path`. |
| F8 | **med** | `b006_selection.py`, `b010_task_footprint.py`; `dev_run.py` | B006 `evolve`s the loaded runtime with **no copy** of `MODEL/active`. If `load_mvp` / `evolve` write-through, tip is corrupted. Even if memory-only, F020 then runs B010/B016 on disk tip that may not match what B006 “after” measured. B010 mutates harness/activity state without isolation. Offline-first tips are precious. | Always clone tip to a temp/workdir (or load read-only snapshot) before evolve/tick benches; B006 must not persist unless explicitly saving a named assay artifact. |
| F9 | **med** | `dev_run.py` (~L55–60) | After `rt.save_named(ckpt_name)`, refresh of `MODEL/active` is `if active.exists() and saved: pass`. Unused `shutil` import. Spec step 6 requires refresh; code hopes `save_named` did it. If it didn’t, benches run on **stale** active while summary claims new checkpoint. | Explicitly sync: copy/replace `MODEL/active` from returned save path (or API guarantee + assert revision/mtime); remove dead branch; use `shutil` or delete import. |
| F10 | **med** | `bench.py` `run_dsc_dynamics` (~L183, L196–205) | `edges_touched_per_tick = float(rt.sub.n_edges)` assumes full-adj gather every tick — may over/understate true touch; feeds `E_touch`. Brittle `"last_out" in dir() or True` is always true (dead check). `out.get("err", ...)` assumes `tick` returns a mapping — wrong type ⇒ crash, no error handling. | Instrument real touch counts from runtime; delete `or True`; type-check tick output; catch and mark profile incomplete with exit 2. |
| F11 | **med** | `b010_task_footprint.py` pass (~L59–60); F020 G1 interaction | B010 `pass: task_error<=0.05 or proxy>0.5`. But `proxy=1/(1+err)>0.5` ⇒ `err<1`, so almost any non-exploded run passes B010 even when G1 would fail. Soft gate labeled “v0” still pollutes integrity narrative. Unused `dormant=0`. | Align B010 pass with G1 (single threshold); remove vacuous `proxy>0.5` or set it to a tight bound; wire dormant proxy or delete. |
| F12 | **med** | API assumptions across tools | Context API: `load_mvp` → `.tick/.evolve/.harness/.sub/.pop`. Code also uses `rt.save_named`, `rt.latent`, `pop.differentiation/gate_logits/utility/activity/n_types`, `sub.adj/n_edges/density`, `harness.reset/last_err` — fine if present, but **no guards**. Missing attr ⇒ traceback mid-protocol; partial reports may still be written (B016 writes after compute) or not (dev_run crashes before summary). | Feature-detect / explicit errors → incomplete report + non-zero exit; don’t claim `dynamics: true` without successful ticks. |
| F13 | **med** | `bench.py` Profile E / A disk comparison | Profile A compares DSC `active_checkpoint` disk to FlyWire **edges_only** feather size — apples≠oranges footprint; can make DSC look smaller/larger spuriously. Operator-load (E) double-loads DSC (measure_dsc + profile_e) — noisy timings, not a correctness bug. | Label incomparability in Profile A; optional full-pack FlyWire disk; document asymmetry; don’t use A alone for pass. |
| F14 | **low** | `dev_run.py` L6; `bench.py` L196; `b010` L39 | Unused `shutil`; dead `or True`; unused `dormant`. Signal low review hygiene and hide the real active-refresh bug. | Remove dead code; run ruff/flake8 in CI. |
| F15 | **low** | `bench.py` `measure_flywire` broad `except Exception` | Feather parse failure → partial metrics with note, but still feeds Profile C zeros and can participate in pass logic if B ran. | On feather failure mark C incomplete; don’t emit fly_E winners. |
| F16 | **low** | F020 doc vs code params | Doc table shows single `E=3` then optional E2; code matches defaults, but G2 text says “typed_n increased” while B006 allows non-decrease. Spec/code drift invites false confidence. | Sync FEATURES/F020 gate table to actual predicates; bump `dev_run_v1` when tightening. |

---

## Checklist answers (required)

### 1. Can B016 `pass: true` overclaim vs FlyWire without Profile D?

**Yes — blocker.** With Profile C’s intentional `task_utility_proxy=0`, DSC wins ≥2 (typically 4) `E_*` axes whenever it produces any positive utility proxy. Spec intent (“anatomy≠compute”) is only in notes, not in the pass bit. Profile D is required for matched-topology claims; current green `pass` under goal `efficiency_vs_flywire` overclaims.

### 2. Are G1–G5 too soft / gameable?

**Yes.** G1 is the only relatively hard gate. G2 inherits B006’s identity-pass. G3’s `E_disk > 0` is always-on. G4/G5 ignore documented checks and **pass under `--skip-b016`**.

### 3. Do B006/B010 mutate MODEL/active destructively without copy?

**Risk: yes (design hole).** No copy/snapshot before `evolve` (B006) or long tick loops (B010). Persistence depends on unseen `load_mvp`/`evolve` write-through. F020 does not verify active refresh after `save_named`. Treat as unsafe-by-default until clone-on-assay is implemented.

### 4. Path/hostname leaks in JSON/MD/meta log?

**Partial hygiene; scrub insufficient.** B016 report fields prefer `active` / pack folder name (good). R001 scrub is hostname-hardcoded and home-prefix-only; `Path`→`default=str` can still leak absolutes into `r001_assay_log.jsonl`. No leak scanner for G4 despite the feature doc.

### 5. Wrong API assumptions, missing error handling, exit codes?

**Yes.** Assumes rich `pop`/`sub`/`harness`/`save_named`/`tick→dict`. Weak handling in dynamics extras; B016 exit `0` on `pass=false` when `dsc_E` empty; dev_run aborts without assay row on mid-run exceptions.

### 6. Metric honesty (`E_*` tiny numerator vs huge denom still “wins”)?

**Yes — core to F1/F2.** Against zeroed FlyWire, any ε>0 wins. Small-disk DSC further inflates `E_disk`. No floor on proxy, no null-opponent guard, no effect-size.

### 7. Unused imports / dead code / brittle patterns?

**Yes.** `shutil` unused; active refresh no-op; `"last_out" in dir() or True`; unused `dormant`; magic `65_000` baseline; always-true dynamics extras try block.

---

## Recommended patches (ordered)

1. **B016 pass semantics (blocker):** Gate `pass` on Profile D (or emit `pass: false` / `pass_kind: "static_null_demo"` only). Never count `E_*` wins against intentionally null FlyWire proxy toward efficiency parity.
2. **Null-opponent + proxy floor:** In `compare_E`, if opponent proxy is null/0 by protocol, set winners to `na` / exclude from `dsc_E_wins`; require `task_error` gate before wins count.
3. **Fix B016 exit codes:** Non-zero whenever `pass` is false or required profiles incomplete.
4. **Harden F020 gates:** Implement real G3 pre/post `E_disk`; G4 path-leak assert; G5 finite `tick_wall_us`; **fail** (don’t pass) when `--skip-b016`.
5. **Tighten B006:** Fail on no-op; require strict elite (or mean) improvement by δ across ≥N seeds.
6. **Clone before assay:** Temp copy of tip for B006/B010; assert F020 active refresh from `save_named` return path.
7. **R001 scrub:** Path-safe serializer; scrub all absolute/UNC paths and hostnames; never stringify raw `Path` via `default=str`.
8. **Clean dead code / API guards:** Remove unused imports and `or True`; validate `tick` return type; mark incomplete on feather/API failures.
9. **Doc bump:** Align `FEATURES/F020_*.md` with real predicates; note Profile D dependency on any public “vs FlyWire efficiency” claim.

---

## What is actually solid

- **Offline-first posture** and explicit non-goals (no biological equivalence, no FlyWire weight training) in F020 / B016 MD notes.
- **Profile C intent is correctly encoded** as static null (`task_utility_proxy=0`, note `anatomy_is_not_free_compute`) — the bug is using that null as a foil for a green efficiency `pass`, not the null itself.
- **Display-name discipline in B016 report schema** (`dsc.display="active"`, `flywire.pack=folder name`, Profile E `path_safe: True`) is the right privacy default.
- **Protocol versioning** (`dev_run_v0`, `b016_v0`, schema 1) and structured JSON+MD artifacts under `BENCHMARKS/runs/` are good reproducibility bones.
- **R001 as external assay logger** (not in-loop cell, no population utility mutation) matches the “light meta” design.
- **Separation of profiles A/B/C/E** (footprint / dynamics / static null / operator load) is a sound experimental frame — once pass bits stop lying about what was shown.
- **CLI exit intent** (0/1 for F020; 0/1/2 hints for B016) is directionally right once the `dsc_E` empty hole is fixed.

---

*End of adversarial review. No source files under review were modified; this document is the sole write artifact.*
