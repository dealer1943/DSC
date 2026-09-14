"""F021 / B016 Profile D — matched-topology stress (ER vs FlyWire subgraph)."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

PROTOCOL = "stress_d_v0"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _build_on_adj(adj: np.ndarray, meta: dict, seed: int):
    from dsc.substrate import Substrate
    from dsc.runtime import init_population, build_harness, DscRuntime

    sub = Substrate(adj=adj.astype(np.uint8), meta=dict(meta))
    if "n" not in sub.meta:
        sub.meta["n"] = int(adj.shape[0])
        sub.meta["n_edges"] = int(adj.sum())
        sub.meta["density"] = float(adj.sum() / max(1, adj.shape[0] * (adj.shape[0] - 1)))
    pop = init_population(sub, seed=seed)
    harness = build_harness()
    return DscRuntime(sub=sub, pop=pop, harness=harness, manifest={"stress": meta})


def _eval_runtime(rt, ticks: int, seed: int) -> dict[str, Any]:
    rt.harness.reset(seed=seed)
    errs: list[float] = []
    walls: list[float] = []
    covs: list[float] = []
    out: dict[str, Any] = {}
    for _ in range(ticks):
        t0 = time.perf_counter()
        out = rt.tick(1)
        walls.append((time.perf_counter() - t0) * 1e6)
        errs.append(float(out.get("err", rt.harness.last_err)))
        if out.get("coverage_mean") is not None:
            covs.append(float(out["coverage_mean"]))
    task_error = float(np.mean(errs[len(errs) // 2 :])) if errs else 1.0
    tick_us = float(np.median(walls)) if walls else 0.0
    proxy = 1.0 / (1.0 + task_error)
    n_edges = int(rt.sub.n_edges)
    latent_n = len(getattr(getattr(rt, "latent", None), "entries", []) or [])
    return {
        "task_error": task_error,
        "tick_wall_us": tick_us,
        "n_nodes": int(rt.sub.n),
        "n_edges": n_edges,
        "density": float(rt.sub.density),
        "utility_mean": float(np.mean(rt.pop.utility)),
        "coverage_mean": float(np.mean(covs)) if covs else float(out.get("coverage_mean") or 0.0),
        "stem_frac": float(out.get("stem_frac", 0.0)) if errs else None,
        "latent_n": latent_n,
        "task_utility_proxy": proxy,
        "E_edge": proxy / max(n_edges, 1),
        "E_tick": proxy / max(tick_us, 1.0),
        "ticks": ticks,
        "seed": seed,
    }


def _gaps(dsc: dict, fly: dict) -> list[dict[str, Any]]:
    """Where fly is better → development target. winner dsc|fly_adj|tie."""
    rows = []
    te_d, te_fly = dsc["task_error"], fly["task_error"]
    rows.append({
        "metric": "task_error",
        "dsc": te_d,
        "er": te_d,
        "fly_adj": te_fly,
        "winner": "fly_adj" if te_fly < te_d - 1e-9 else ("dsc" if te_d < te_fly - 1e-9 else "tie"),
        "dev_hint": "Need stronger inductive bias / motifs" if te_fly < te_d else "DSC holding on task — push scale or harder harness",
    })
    for metric, higher_better, hint_fly, hint_dsc in (
        ("E_tick", True, "Optimize message passing / hub handling", "DSC cheaper/tick — keep while raising task"),
        ("E_edge", True, "More signal per edge: prune+coverage under skew", "Good edge efficiency — test at larger N"),
        ("utility_mean", True, "Retune F005 / type emergence for hubs", "Utility OK on this family"),
        ("coverage_mean", True, "Coverage collapse under prune/skew — strengthen F008 absorb", "Coverage holding"),
        ("tick_wall_us", False, "Sparse kernels on hubs", "DSC already fast"),
    ):
        a, b = dsc[metric], fly[metric]
        if higher_better:
            winner = "fly_adj" if b > a + 1e-12 else ("dsc" if a > b + 1e-12 else "tie")
        else:
            winner = "fly_adj" if b < a - 1e-12 else ("dsc" if a < b - 1e-12 else "tie")
        hint = hint_fly if winner == "fly_adj" else hint_dsc
        rows.append({"metric": metric, "dsc": a, "er": a, "fly_adj": b, "winner": winner, "dev_hint": hint})
    return rows


def run_stress(
    n: int = 128,
    neuropil: str = "GNG",
    seed: int = 42,
    ticks: int = 256,
    warm: int = 32,
    evolve: int = 2,
    feather: Path | None = None,
    out_dir: Path | None = None,
    dsc_family: str = "erdos_renyi_directed",
    experiment: str = "baseline",
    prune_stress: bool = False,
    task_lag: int | None = None,
    task_noise: float | None = None,
) -> dict[str, Any]:
    from dsc import defaults
    from dsc.substrate import generate_substrate
    from tools.flywire_subgraph.extract import extract_subgraph, save_subgraph

    # optional temporary default overrides (restored in finally)
    _saved = {}
    def _override(name, val):
        _saved[name] = getattr(defaults, name)
        setattr(defaults, name, val)

    out_dir = Path(out_dir or "BENCHMARKS/runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    feather = Path(feather or "MODELS/fly/flywire_v783/proofread_connections_783.feather")

    bundle = extract_subgraph(feather, n=n, neuropil=neuropil, seed=seed)
    sub_path = Path(f"MODELS/fly/subgraphs/n{n}_{neuropil}_s{seed}.npz")
    save_subgraph(bundle, sub_path)

    fly_edges = int(bundle["adj"].sum())
    # DSC side: chosen family; match fly edge budget when not pure ER-p
    dsc_sub = generate_substrate(
        n=n,
        seed=seed,
        family=dsc_family,
        target_edges=fly_edges,
    )
    rt_er = _build_on_adj(dsc_sub.adj, dsc_sub.meta, seed=seed)
    rt_fly = _build_on_adj(bundle["adj"], bundle["meta"], seed=seed)

    try:
        if prune_stress:
            _override("PRUNE_FAIL_STREAK", 3)
            _override("PRUNE_UTIL_QUANTILE", 0.40)
            _override("EVOLVE_REPLACE_FRAC", 0.35)
            _override("ABSORB_BLEND", 0.45)
            if evolve < 8:
                evolve = 8
        if task_lag is not None:
            _override("TASK_LAG", int(task_lag))
        if task_noise is not None:
            _override("TASK_NOISE", float(task_noise))

        for rt in (rt_er, rt_fly):
            # rebuild harness with possibly overridden lag/noise
            from dsc.harness import TemporalHarness
            rt.harness = TemporalHarness(
                seed=seed,
                lag=int(defaults.TASK_LAG),
                noise=float(defaults.TASK_NOISE),
            )
            rt.harness.reset(seed=seed)
            for _ in range(warm):
                rt.tick(1)
            if evolve > 0:
                rt.evolve(n=evolve, seed=seed)

        dsc_m = _eval_runtime(rt_er, ticks=ticks, seed=seed + 1)
        fly_m = _eval_runtime(rt_fly, ticks=ticks, seed=seed + 1)
    finally:
        for k, v in _saved.items():
            setattr(defaults, k, v)
    gaps = _gaps(dsc_m, fly_m)
    fly_wins = sum(1 for g in gaps if g["winner"] == "fly_adj")
    dsc_wins = sum(1 for g in gaps if g["winner"] == "dsc")

    fam_slug = dsc_sub.meta.get("family", dsc_family).replace("_directed", "").replace("_", "")[:12]
    report = {
        "bench": "B016_profile_D",
        "protocol": PROTOCOL,
        "experiment": experiment,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": f"stressD_{_utc_stamp()}_n{n}_{neuropil}_{fam_slug}",
        "n": n,
        "neuropil": neuropil,
        "seed": seed,
        "warm": warm,
        "evolve": evolve,
        "ticks": ticks,
        "dsc_family": dsc_sub.meta.get("family", dsc_family),
        "hub_aware": bool(__import__("dsc.defaults", fromlist=["HUB_AWARE"]).HUB_AWARE),
        "prune_stress": bool(prune_stress),
        "task_lag": int(task_lag) if task_lag is not None else 1,
        "task_noise": float(task_noise) if task_noise is not None else 0.05,
        "subgraph": sub_path.name,
        "dsc": dsc_m,
        "er": dsc_m,  # backward-compatible alias
        "fly_adj": fly_m,
        "gaps": gaps,
        "scoreboard": {"fly_adj_wins": fly_wins, "dsc_wins": dsc_wins, "er_wins": dsc_wins},
        "pass_matched": fly_wins == 0 and dsc_m["task_error"] <= fly_m["task_error"],
        "notes": [
            "Same DSC software + harness; only adjacency family differs.",
            "Not biological equivalence — inductive-bias stress test.",
            "Development backlog = rows where winner=fly_adj.",
        ],
    }
    json_path = out_dir / f"{report['run_id']}.json"
    md_path = out_dir / f"{report['run_id']}.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    md_path.write_text(_render_md(report), encoding="utf-8")
    report["json_path"] = json_path.name
    report["md_path"] = md_path.name
    return report


def _render_md(report: dict) -> str:
    lines = [
        f"# Profile D stress — `{report['protocol']}`",
        "",
        f"- run: `{report['run_id']}`",
        f"- N={report['n']} neuropil=`{report['neuropil']}` seed={report['seed']}",
        f"- scoreboard: fly_adj wins **{report['scoreboard']['fly_adj_wins']}** · DSC wins **{report['scoreboard'].get('dsc_wins', report['scoreboard'].get('er_wins'))}**",
        f"- dsc_family: `{report.get('dsc_family')}` · experiment: `{report.get('experiment')}`",
        "",
        "## Side-by-side",
        "",
        "| metric | DSC | FlyWire-adj |",
        "|--------|-----|-------------|",
    ]
    dsc, fly = report.get("dsc") or report.get("er") or {}, report["fly_adj"]
    for k in ("n_nodes", "n_edges", "density", "task_error", "tick_wall_us", "utility_mean", "coverage_mean", "latent_n", "E_edge", "E_tick"):
        lines.append(f"| `{k}` | {dsc.get(k)} | {fly.get(k)} |")
    lines += ["", "## Gaps → development targets", "", "| metric | winner | hint |", "|--------|--------|------|"]
    for g in report["gaps"]:
        lines.append(f"| `{g['metric']}` | **{g['winner']}** | {g['dev_hint']} |")
    lines += ["", "## Notes", ""]
    for n in report.get("notes") or []:
        lines.append(f"- {n}")
    lines.append("")
    return "\n".join(lines)


def _append_ledger(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dsc = report.get("dsc") or report.get("er") or {}
    row = {
        "utc": report.get("utc"),
        "experiment": report.get("experiment"),
        "run_id": report.get("run_id"),
        "n": report.get("n"),
        "neuropil": report.get("neuropil"),
        "dsc_family": report.get("dsc_family"),
        "hub_aware": report.get("hub_aware"),
        "prune_stress": report.get("prune_stress"),
        "task_lag": report.get("task_lag"),
        "task_noise": report.get("task_noise"),
        "dsc_coverage": dsc.get("coverage_mean"),
        "fly_coverage": (report.get("fly_adj") or {}).get("coverage_mean"),
        "fly_wins": (report.get("scoreboard") or {}).get("fly_adj_wins"),
        "dsc_wins": (report.get("scoreboard") or {}).get("dsc_wins"),
        "dsc_task_error": dsc.get("task_error"),
        "fly_task_error": (report.get("fly_adj") or {}).get("task_error"),
        "dsc_edges": dsc.get("n_edges"),
        "fly_edges": (report.get("fly_adj") or {}).get("n_edges"),
        "md": report.get("md_path"),
        "json": report.get("json_path"),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def main(argv=None) -> int:

    ap = argparse.ArgumentParser(description="F021 FlyWire matched-topology stress")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--neuropil", type=str, default="GNG")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ticks", type=int, default=256)
    ap.add_argument("--warm", type=int, default=32)
    ap.add_argument("--evolve", type=int, default=2)
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    ap.add_argument("--dsc-family", type=str, default="erdos_renyi_directed",
                    help="er|preferential|modular (F022)")
    ap.add_argument("--experiment", type=str, default="baseline")
    ap.add_argument("--prune-stress", action="store_true",
                    help="Aggressive evolve/prune/absorb (F024)")
    ap.add_argument("--task-lag", type=int, default=None)
    ap.add_argument("--task-noise", type=float, default=None)
    args = ap.parse_args(argv)
    report = run_stress(
        n=args.n,
        neuropil=args.neuropil,
        seed=args.seed,
        ticks=args.ticks,
        warm=args.warm,
        evolve=args.evolve,
        out_dir=args.out,
        dsc_family=args.dsc_family,
        experiment=args.experiment,
        prune_stress=args.prune_stress,
        task_lag=args.task_lag,
        task_noise=args.task_noise,
    )
    _append_ledger(report, Path(args.out) / "stress_ledger.jsonl")
    print(json.dumps({
        "run_id": report["run_id"],
        "experiment": report.get("experiment"),
        "dsc_family": report.get("dsc_family"),
        "hub_aware": report.get("hub_aware"),
        "scoreboard": report["scoreboard"],
        "dsc_task_error": (report.get("dsc") or report["er"])["task_error"],
        "fly_task_error": report["fly_adj"]["task_error"],
        "gaps": [{"metric": g["metric"], "winner": g["winner"]} for g in report["gaps"]],
        "md": report["md_path"],
        "json": report["json_path"],
    }, indent=2))
    # exit 0 always for first exploratory stress; pass_matched is informational
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
