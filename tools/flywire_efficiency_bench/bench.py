"""B016 — FlyWire efficiency parity (profiles A, B, C, E).

Offline only. Path-safe display names. Schema 1 report.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import shutil
import tempfile

import numpy as np

PROTOCOL = "b016_v0"

def _scrub_report(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _scrub_report(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_scrub_report(x) for x in obj]
    if isinstance(obj, str):
        for bad in ("Mac.home.local",):
            obj = obj.replace(bad, "[host]")
        if obj.startswith("/Users/") or obj.startswith("/home/"):
            return Path(obj).name
        return obj
    return obj

SCHEMA = 1
DEFAULT_PROFILES = ("A", "B", "C", "E")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _dir_bytes(p: Path) -> int:
    if not p.exists():
        return 0
    if p.is_file():
        return p.stat().st_size
    total = 0
    for root, _dirs, files in os.walk(p):
        for fn in files:
            try:
                total += (Path(root) / fn).stat().st_size
            except OSError:
                pass
    return total


def _degree_stats(adj: np.ndarray) -> dict[str, float]:
    deg = adj.sum(axis=0).astype(float) + adj.sum(axis=1).astype(float)
    if deg.size == 0:
        return {"degree_mean": 0.0, "degree_median": 0.0, "degree_max": 0.0}
    return {
        "degree_mean": float(deg.mean()),
        "degree_median": float(np.median(deg)),
        "degree_max": float(deg.max()),
    }


def _utility_proxy(task_error: float | None, utility_mean: float | None) -> float:
    if task_error is not None and math.isfinite(task_error):
        return 1.0 / (1.0 + float(task_error))
    if utility_mean is not None and math.isfinite(utility_mean):
        return float(utility_mean)
    return 0.0


def _E_scores(proxy: float, disk: int, edges: int, tick_us: float | None, touch: float | None) -> dict[str, float]:
    return {
        "E_disk": proxy / max(disk, 1),
        "E_edge": proxy / max(edges, 1),
        "E_tick": proxy / max(float(tick_us or 0.0), 1.0),
        "E_touch": proxy / max(float(touch or 0.0), 1.0),
    }


def _stem_type_stats(pop) -> dict[str, float]:
    # STEM ≈ low differentiation; type from argmax gate when differentiated
    diff = np.asarray(pop.differentiation, dtype=float)
    stem_frac = float((diff < 0.35).mean()) if diff.size else 1.0
    winners = np.asarray(pop.gate_logits).argmax(axis=1)
    # entropy of winner distribution among non-STEM
    mask = diff >= 0.35
    if mask.any():
        counts = np.bincount(winners[mask], minlength=int(pop.n_types))
        p = counts / max(counts.sum(), 1)
        p = p[p > 0]
        type_entropy = float(-(p * np.log(p + 1e-12)).sum())
    else:
        type_entropy = 0.0
    return {"stem_frac": stem_frac, "type_entropy": type_entropy}


def measure_dsc(dsc_dir: Path, *, isolate: bool = True) -> tuple[Any, dict[str, Any], Any]:
    """Load DSC. If isolate, copy to temp so Profile B ticks do not mutate MODEL/active."""
    from dsc.runtime import load_mvp

    dsc_dir = Path(dsc_dir)
    tmp_ctx = None
    work = dsc_dir
    if isolate:
        tmp_ctx = tempfile.TemporaryDirectory(prefix="b016_")
        work = Path(tmp_ctx.name) / "active"
        shutil.copytree(dsc_dir, work)
    t0 = time.perf_counter()
    rt = load_mvp(work)
    load_wall_s = time.perf_counter() - t0
    sub, pop = rt.sub, rt.pop
    n = int(sub.n)
    e = int(sub.n_edges)
    dens = float(sub.density)
    disk = _dir_bytes(Path(dsc_dir))  # original artifact bytes
    metrics = {
        "n_nodes": n,
        "n_edges": e,
        "density": dens,
        **_degree_stats(sub.adj),
        "disk_bytes": disk,
        "disk_profile": "active_checkpoint",
        "dynamics": True,
        "revision": getattr(rt, "revision", dsc_dir.name),
        "load_wall_s": load_wall_s,
        "utility_mean": float(np.mean(pop.utility)),
        "coverage_mean": None,
        "novelty_mean": None,
        "cost_mean": None,
        **_stem_type_stats(pop),
        "n_neuropils": None,
        "mean_syn_count": None,
    }
    return rt, metrics, tmp_ctx


def measure_flywire(fly_root: Path, edges_only: bool = True) -> dict[str, Any]:
    feather = fly_root / "proofread_connections_783.feather"
    metrics: dict[str, Any] = {
        "n_nodes": 0,
        "n_edges": 0,
        "density": None,
        "degree_mean": None,
        "degree_median": None,
        "degree_max": None,
        "disk_bytes": 0,
        "disk_profile": "edges_only" if edges_only else "full_pack",
        "dynamics": False,
        "pack": fly_root.name,
        "profile_edges": "proofread_connections",
        "load_wall_s": None,
        "utility_mean": None,
        "stem_frac": None,
        "type_entropy": None,
        "n_neuropils": None,
        "mean_syn_count": None,
        "task_error": None,
        "task_id": None,
        "tick_wall_us": None,
        "edges_touched_per_tick": None,
        "activation_l1": None,
        "sample_hz_sustainable": None,
    }
    t0 = time.perf_counter()
    if edges_only and feather.is_file():
        metrics["disk_bytes"] = feather.stat().st_size
        try:
            import pyarrow.feather as feather_api
            import pyarrow.compute as pc

            table = feather_api.read_table(feather)
            metrics["n_edges"] = int(table.num_rows)
            cols = set(table.column_names)
            pre = "pre_root_id" if "pre_root_id" in cols else None
            post = "post_root_id" if "post_root_id" in cols else None
            if pre and post:
                nodes = set(pc.unique(table[pre]).to_pylist()) | set(pc.unique(table[post]).to_pylist())
                metrics["n_nodes"] = len(nodes)
            if "syn_count" in cols:
                metrics["mean_syn_count"] = float(pc.mean(table["syn_count"]).as_py())
        except Exception as exc:  # noqa: BLE001
            metrics["notes"] = f"feather_meta_partial:{type(exc).__name__}"
    else:
        metrics["disk_bytes"] = _dir_bytes(fly_root)
        metrics["disk_profile"] = "full_pack"
    metrics["load_wall_s"] = time.perf_counter() - t0
    return metrics


def run_dsc_dynamics(rt: Any, ticks: int, seed: int) -> dict[str, Any]:
    """Profile B: harness ticks on loaded runtime."""
    rt.harness.reset(seed=seed)
    errs: list[float] = []
    acts: list[float] = []
    t_walls: list[float] = []
    last_out: dict[str, Any] = {}
    edges_touched = float(rt.sub.n_edges)  # each tick reads full adj gather
    for _ in range(ticks):
        t0 = time.perf_counter()
        out = rt.tick(1)
        t_walls.append((time.perf_counter() - t0) * 1e6)
        err = float(out.get("err", rt.harness.last_err))
        errs.append(err)
        acts.append(float(np.mean(rt.pop.activity)))
        last_out = out
    tick_us = float(np.median(t_walls)) if t_walls else 0.0
    task_error = float(np.mean(errs[-max(1, ticks // 4) :])) if errs else 1.0
    hz = 1e6 / tick_us if tick_us > 0 else 0.0
    extra = {}
    if "last_out" in dir() or True:
        try:
            extra = {
                "coverage_mean": float(last_out.get("coverage_mean")) if last_out else None,
                "novelty_mean": float(last_out.get("novelty_mean")) if last_out else None,
                "cost_mean": float(last_out.get("cost_mean")) if last_out else None,
                "stem_frac": float(last_out.get("stem_frac")) if last_out else None,
            }
        except Exception:
            extra = {}
    return {
        "task_id": "temporal_lag1_mse",
        "task_error": task_error,
        "tick_wall_us": tick_us,
        "edges_touched_per_tick": edges_touched,
        "activation_l1": float(np.mean(np.abs(rt.pop.activity))),
        "sample_hz_sustainable": hz,
        "activity_mean": float(np.mean(acts)) if acts else 0.0,
        "utility_mean": float(np.mean(rt.pop.utility)),
        "dynamics": True,
        "ticks": ticks,
        "seed": seed,
        **extra,
    }


def profile_e_operator_load(dsc_dir: Path, fly_root: Path) -> dict[str, Any]:
    """Load timing with display names only (no absolute paths in result)."""
    from dsc.runtime import load_mvp

    t0 = time.perf_counter()
    _ = load_mvp(dsc_dir)
    dsc_load = time.perf_counter() - t0
    t1 = time.perf_counter()
    _ = measure_flywire(fly_root, edges_only=True)
    fly_load = time.perf_counter() - t1
    return {
        "dsc_display": "active",
        "flywire_display": fly_root.name,
        "dsc_load_wall_s": dsc_load,
        "flywire_load_wall_s": fly_load,
        "path_safe": True,
    }


def compare_E(
    dsc_E: dict[str, float],
    fly_E: dict[str, float],
    *,
    fly_proxy: float,
    dsc_proxy: float,
    proxy_min: float = 0.5,
) -> dict[str, Any]:
    """Compare E_* scores.

    When FlyWire proxy is intentionally 0 (Profile C static null), winners are
    recorded as demo-only and do NOT count toward efficiency_vs_flywire pass.
    """
    winners: dict[str, Any] = {}
    null_opponent = fly_proxy <= 0.0
    proxy_ok = dsc_proxy >= proxy_min
    for k in ("E_disk", "E_edge", "E_tick", "E_touch"):
        d, f = float(dsc_E.get(k, 0.0) or 0.0), float(fly_E.get(k, 0.0) or 0.0)
        if null_opponent:
            winners[f"{k}_winner"] = "na_static_null" if proxy_ok and d > 0 else "na"
        elif not proxy_ok:
            winners[f"{k}_winner"] = "na_proxy_floor"
        elif d > f:
            winners[f"{k}_winner"] = "dsc"
        elif f > d:
            winners[f"{k}_winner"] = "flywire"
        else:
            winners[f"{k}_winner"] = "tie"
    wins = sum(1 for k in ("E_disk", "E_edge", "E_tick", "E_touch") if winners[f"{k}_winner"] == "dsc")
    demo_axes = sum(
        1
        for k in ("E_disk", "E_edge", "E_tick", "E_touch")
        if winners[f"{k}_winner"] == "na_static_null"
    )
    winners["dsc_E_wins"] = wins
    winners["static_null_demo_axes"] = demo_axes
    winners["goal_two_of_four"] = wins >= 2  # only true when both sides tasked
    winners["null_opponent"] = null_opponent
    winners["dsc_proxy"] = dsc_proxy
    winners["proxy_min"] = proxy_min
    return winners


def run_bench(
    dsc_path: Path,
    fly_root: Path,
    profiles: tuple[str, ...] = DEFAULT_PROFILES,
    seed: int = 42,
    ticks: int = 256,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    out_dir = Path(out_dir or "BENCHMARKS/runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = {p.upper() for p in profiles}
    notes: list[str] = []
    incomplete = False

    if not dsc_path.exists() and wanted & {"A", "B", "E"}:
        incomplete = True
        notes.append("missing_dsc_active")
    if not fly_root.exists() and wanted & {"A", "C", "E"}:
        incomplete = True
        notes.append("missing_flywire_pack")

    dsc_metrics: dict[str, Any] = {}
    fly_metrics: dict[str, Any] = {}
    dsc_E: dict[str, float] = {}
    fly_E: dict[str, float] = {}
    profiles_detail: dict[str, Any] = {}
    rt = None
    _dsc_tmp = None

    if not incomplete and wanted & {"A", "B", "E"}:
        rt, dsc_metrics, _dsc_tmp = measure_dsc(dsc_path, isolate=True)

    if not incomplete and wanted & {"A", "C", "E"}:
        fly_metrics = measure_flywire(fly_root, edges_only=True)

    if "A" in wanted and not incomplete:
        profiles_detail["A"] = {
            "name": "artifact_footprint",
            "dsc": {k: dsc_metrics.get(k) for k in (
                "n_nodes", "n_edges", "density", "degree_mean", "degree_median", "degree_max",
                "disk_bytes", "disk_profile", "stem_frac", "type_entropy",
            )},
            "flywire": {k: fly_metrics.get(k) for k in (
                "n_nodes", "n_edges", "density", "degree_mean", "degree_median", "degree_max",
                "disk_bytes", "disk_profile", "mean_syn_count", "n_neuropils",
            )},
        }

    if "B" in wanted and rt is not None:
        dyn = run_dsc_dynamics(rt, ticks=ticks, seed=seed)
        dsc_metrics.update(dyn)
        proxy = _utility_proxy(dyn["task_error"], dyn.get("utility_mean"))
        dsc_E = _E_scores(
            proxy,
            int(dsc_metrics.get("disk_bytes") or 0),
            int(dsc_metrics.get("n_edges") or 0),
            dyn.get("tick_wall_us"),
            dyn.get("edges_touched_per_tick"),
        )
        profiles_detail["B"] = {"name": "dsc_native_dynamics", **dyn, "E": dsc_E}
    elif "B" in wanted:
        notes.append("profile_B_skipped")

    if "C" in wanted and fly_metrics:
        proxy = 0.0  # static null
        fly_E = _E_scores(
            proxy,
            int(fly_metrics.get("disk_bytes") or 0),
            int(fly_metrics.get("n_edges") or 0),
            None,
            None,
        )
        fly_metrics["task_utility_proxy"] = 0.0
        profiles_detail["C"] = {
            "name": "flywire_static_null",
            "dynamics": False,
            "task_utility_proxy": 0.0,
            "E": fly_E,
            "note": "anatomy_is_not_free_compute",
        }
    elif "C" in wanted:
        notes.append("profile_C_skipped")

    if "E" in wanted and not incomplete:
        profiles_detail["E"] = {
            "name": "operator_load",
            **profile_e_operator_load(dsc_path, fly_root),
        }

    # If B ran but C didn't fill fly E, still compute fly E from static null for comparison
    if dsc_E and not fly_E and fly_metrics:
        fly_E = _E_scores(0.0, int(fly_metrics.get("disk_bytes") or 0), int(fly_metrics.get("n_edges") or 0), None, None)

    fly_proxy = float((fly_metrics or {}).get("task_utility_proxy") or 0.0)
    dsc_proxy = _utility_proxy(
        (dsc_metrics or {}).get("task_error"),
        (dsc_metrics or {}).get("utility_mean"),
    )
    comparisons = (
        compare_E(dsc_E, fly_E, fly_proxy=fly_proxy, dsc_proxy=dsc_proxy)
        if dsc_E and fly_E
        else {}
    )
    # Pass semantics (adversarial F1/F2):
    # - efficiency_vs_flywire `pass` requires both sides tasked (Profile D territory)
    # - Profile C-only runs get pass_kind=static_null_demo; pass=false for the goal
    has_fly_task = fly_proxy > 0.0
    required = set(wanted)
    missing_req = sorted(required - set(profiles_detail.keys()))
    if missing_req:
        incomplete = True
        notes.append(f"missing_profiles:{','.join(missing_req)}")

    if incomplete:
        claim_level = "incomplete"
        pass_kind = "incomplete"
        passed = False
        exit_hint = 2
    elif has_fly_task and bool(comparisons.get("goal_two_of_four")):
        claim_level = "matched_or_both_tasked"
        pass_kind = "efficiency_vs_flywire"
        passed = True
        exit_hint = 0
    elif not has_fly_task and dsc_E:
        claim_level = "static_null_asymmetry"
        pass_kind = "static_null_demo"
        # Demo can still be "ok" as anatomy≠compute illustration, but goal pass is false
        passed = False
        exit_hint = 0  # demo completed successfully; not a goal pass
        notes.append("pass_false_static_null_only_profile_D_required_for_goal")
        comparisons["overclaim_warning"] = (
            "E_* vs Profile C null is anatomy≠compute demo only; "
            "efficiency_vs_flywire pass requires Profile D / tasked FlyWire"
        )
        comparisons["claim_level"] = claim_level
        comparisons["pass_kind"] = pass_kind
        comparisons["static_null_demo_ok"] = bool(comparisons.get("static_null_demo_axes", 0) >= 2)
    else:
        claim_level = "no_claim"
        pass_kind = "failed"
        passed = False
        exit_hint = 1
        comparisons["claim_level"] = claim_level
        comparisons["pass_kind"] = pass_kind

    run_id = f"B016_{_utc_stamp()}_s{seed}"
    report: dict[str, Any] = {
        "bench": "B016",
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "utc": _utc(),
        "run_id": run_id,
        "goal": "efficiency_vs_flywire",
        "profiles_run": sorted(wanted),
        "seed": seed,
        "ticks": ticks,
        "dsc": {
            "revision": dsc_metrics.get("revision", "active"),
            "display": "active",
            "metrics": dsc_metrics,
            "E": dsc_E,
        },
        "flywire": {
            "pack": fly_metrics.get("pack", fly_root.name),
            "profile_edges": fly_metrics.get("profile_edges", "proofread_connections"),
            "metrics": fly_metrics,
            "E": fly_E,
        },
        "profiles": profiles_detail,
        "comparisons": comparisons,
        "claim_level": claim_level,
        "pass_kind": pass_kind,
        "pass": passed,
        "notes": notes,
        "exit_hint": exit_hint,
    }

    json_path = out_dir / f"{run_id}.json"
    md_path = out_dir / f"{run_id}.md"
    safe = _scrub_report(report)
    json_path.write_text(json.dumps(safe, indent=2, default=str) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(safe), encoding="utf-8")
    report["json_path"] = json_path.name
    report["md_path"] = md_path.name
    try:
        if "_dsc_tmp" in locals() and _dsc_tmp is not None:
            _dsc_tmp.cleanup()
    except Exception:
        pass
    return report


def render_markdown(report: dict[str, Any]) -> str:
    dsc_m = (report.get("dsc") or {}).get("metrics") or {}
    fly_m = (report.get("flywire") or {}).get("metrics") or {}
    dsc_E = (report.get("dsc") or {}).get("E") or {}
    fly_E = (report.get("flywire") or {}).get("E") or {}
    lines = [
        f"# B016 — FlyWire efficiency parity",
        "",
        f"- run_id: `{report.get('run_id')}`",
        f"- schema: `{report.get('schema')}` · protocol: `{report.get('protocol')}`",
        f"- seed: `{report.get('seed')}` · ticks: `{report.get('ticks')}`",
        f"- pass: **{report.get('pass')}** · pass_kind: `{report.get('pass_kind')}` · claim: `{report.get('claim_level')}`",
        "",
        "## Footprint (Profile A)",
        "",
        "| metric | DSC (`active`) | FlyWire |",
        "|--------|----------------|---------|",
    ]
    for key in ("n_nodes", "n_edges", "density", "disk_bytes", "disk_profile", "dynamics"):
        lines.append(f"| `{key}` | {dsc_m.get(key)} | {fly_m.get(key)} |")
    lines += [
        "",
        "## Efficiency scores",
        "",
        "| score | DSC | FlyWire | winner |",
        "|-------|-----|---------|--------|",
    ]
    comps = report.get("comparisons") or {}
    for k in ("E_disk", "E_edge", "E_tick", "E_touch"):
        lines.append(
            f"| `{k}` | {dsc_E.get(k)} | {fly_E.get(k)} | {comps.get(k + '_winner', '')} |"
        )
    lines += [
        "",
        f"DSC E wins: `{comps.get('dsc_E_wins')}` · goal (≥2): `{comps.get('goal_two_of_four')}`",
        f"- claim_level: `{report.get('claim_level')}`",
        f"- warning: `{comps.get('overclaim_warning')}`",
        "",
        "## Profile B (DSC dynamics)",
        "",
    ]
    b = (report.get("profiles") or {}).get("B") or {}
    for k in ("task_id", "task_error", "tick_wall_us", "edges_touched_per_tick", "sample_hz_sustainable"):
        lines.append(f"- `{k}`: `{b.get(k)}`")
    lines += [
        "",
        "## Notes",
        "",
        "- Offline-only; not biological equivalence.",
        "- Profile C sets FlyWire `task_utility_proxy=0` (static anatomy).",
        "- Display names only (`active`, pack folder name).",
        "",
    ]
    if report.get("notes"):
        for n in report["notes"]:
            lines.append(f"- note: `{n}`")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B016 FlyWire efficiency parity")
    ap.add_argument("--dsc", type=Path, default=Path("MODEL/active"))
    ap.add_argument("--flywire", type=Path, default=Path("MODELS/fly/flywire_v783"))
    ap.add_argument("--profiles", type=str, default="A,B,C,E")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ticks", type=int, default=256)
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    args = ap.parse_args(argv)
    profiles = tuple(p.strip().upper() for p in args.profiles.split(",") if p.strip())
    report = run_bench(
        dsc_path=args.dsc,
        fly_root=args.flywire,
        profiles=profiles,
        seed=args.seed,
        ticks=args.ticks,
        out_dir=args.out,
    )
    print(
        json.dumps(
            {
                "run_id": report["run_id"],
                "pass": report["pass"],
                "pass_kind": report.get("pass_kind"),
                "claim_level": report.get("claim_level"),
                "json": report["json_path"],
                "md": report["md_path"],
                "comparisons": report.get("comparisons"),
            },
            indent=2,
        )
    )
    return int(report.get("exit_hint", 0 if report.get("pass") or report.get("pass_kind") == "static_null_demo" else 1))


if __name__ == "__main__":
    raise SystemExit(main())
