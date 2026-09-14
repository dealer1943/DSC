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
    for _ in range(ticks):
        t0 = time.perf_counter()
        out = rt.tick(1)
        walls.append((time.perf_counter() - t0) * 1e6)
        errs.append(float(out.get("err", rt.harness.last_err)))
    task_error = float(np.mean(errs[len(errs) // 2 :])) if errs else 1.0
    tick_us = float(np.median(walls)) if walls else 0.0
    proxy = 1.0 / (1.0 + task_error)
    n_edges = int(rt.sub.n_edges)
    return {
        "task_error": task_error,
        "tick_wall_us": tick_us,
        "n_nodes": int(rt.sub.n),
        "n_edges": n_edges,
        "density": float(rt.sub.density),
        "utility_mean": float(np.mean(rt.pop.utility)),
        "stem_frac": float(out.get("stem_frac", 0.0)) if errs else None,
        "task_utility_proxy": proxy,
        "E_edge": proxy / max(n_edges, 1),
        "E_tick": proxy / max(tick_us, 1.0),
        "ticks": ticks,
        "seed": seed,
    }


def _gaps(er: dict, fly: dict) -> list[dict[str, Any]]:
    """Where fly is better → development target."""
    rows = []
    # lower task_error better
    te_er, te_fly = er["task_error"], fly["task_error"]
    rows.append({
        "metric": "task_error",
        "er": te_er,
        "fly_adj": te_fly,
        "winner": "fly_adj" if te_fly < te_er - 1e-9 else ("er" if te_er < te_fly - 1e-9 else "tie"),
        "dev_hint": "Grow beyond ER: motifs / neuropil-like inductive bias (F001 family)" if te_fly < te_er else "ER holding on task — push scale or harder harness",
    })
    for metric, higher_better, hint_fly, hint_er in (
        ("E_tick", True, "Optimize message passing / hub handling on biological degree skew", "Synthetic wiring is cheaper/tick — keep while raising task"),
        ("E_edge", True, "Need more signal per edge: prune+coverage (F007/F008) under fly skew", "Good edge efficiency on ER — test at N=512"),
        ("utility_mean", True, "Retune F005 terms / type emergence for hub-heavy graphs", "Utility OK on ER"),
        ("tick_wall_us", False, "Sparse kernels; avoid dense gather on fly hubs", "ER already fast"),
    ):
        a, b = er[metric], fly[metric]
        if higher_better:
            winner = "fly_adj" if b > a + 1e-12 else ("er" if a > b + 1e-12 else "tie")
            hint = hint_fly if winner == "fly_adj" else hint_er
        else:
            winner = "fly_adj" if b < a - 1e-12 else ("er" if a < b - 1e-12 else "tie")
            hint = hint_fly if winner == "fly_adj" else hint_er
        rows.append({"metric": metric, "er": a, "fly_adj": b, "winner": winner, "dev_hint": hint})
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
) -> dict[str, Any]:
    from dsc.runtime import generate_substrate
    from tools.flywire_subgraph.extract import extract_subgraph, save_subgraph

    out_dir = Path(out_dir or "BENCHMARKS/runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    feather = Path(feather or "MODELS/fly/flywire_v783/proofread_connections_783.feather")

    bundle = extract_subgraph(feather, n=n, neuropil=neuropil, seed=seed)
    sub_path = Path(f"MODELS/fly/subgraphs/n{n}_{neuropil}_s{seed}.npz")
    save_subgraph(bundle, sub_path)

    # ER matched N
    er_sub = generate_substrate(n=n, seed=seed)
    # density may differ — that's part of the stress
    rt_er = _build_on_adj(er_sub.adj, er_sub.meta, seed=seed)
    rt_fly = _build_on_adj(bundle["adj"], bundle["meta"], seed=seed)

    for rt in (rt_er, rt_fly):
        rt.harness.reset(seed=seed)
        for _ in range(warm):
            rt.tick(1)
        if evolve > 0:
            rt.evolve(n=evolve, seed=seed)

    er_m = _eval_runtime(rt_er, ticks=ticks, seed=seed + 1)
    fly_m = _eval_runtime(rt_fly, ticks=ticks, seed=seed + 1)
    gaps = _gaps(er_m, fly_m)
    fly_wins = sum(1 for g in gaps if g["winner"] == "fly_adj")
    er_wins = sum(1 for g in gaps if g["winner"] == "er")

    report = {
        "bench": "B016_profile_D",
        "protocol": PROTOCOL,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": f"stressD_{_utc_stamp()}_n{n}_{neuropil}",
        "n": n,
        "neuropil": neuropil,
        "seed": seed,
        "warm": warm,
        "evolve": evolve,
        "ticks": ticks,
        "subgraph": sub_path.name,
        "er": er_m,
        "fly_adj": fly_m,
        "gaps": gaps,
        "scoreboard": {"fly_adj_wins": fly_wins, "er_wins": er_wins},
        "pass_matched": fly_wins == 0 and er_m["task_error"] <= fly_m["task_error"],
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
        f"- scoreboard: fly_adj wins **{report['scoreboard']['fly_adj_wins']}** · ER wins **{report['scoreboard']['er_wins']}**",
        "",
        "## Side-by-side",
        "",
        "| metric | ER | FlyWire-adj |",
        "|--------|----|-------------|",
    ]
    er, fly = report["er"], report["fly_adj"]
    for k in ("n_nodes", "n_edges", "density", "task_error", "tick_wall_us", "utility_mean", "E_edge", "E_tick"):
        lines.append(f"| `{k}` | {er.get(k)} | {fly.get(k)} |")
    lines += ["", "## Gaps → development targets", "", "| metric | winner | hint |", "|--------|--------|------|"]
    for g in report["gaps"]:
        lines.append(f"| `{g['metric']}` | **{g['winner']}** | {g['dev_hint']} |")
    lines += ["", "## Notes", ""]
    for n in report.get("notes") or []:
        lines.append(f"- {n}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="F021 FlyWire matched-topology stress")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--neuropil", type=str, default="GNG")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ticks", type=int, default=256)
    ap.add_argument("--warm", type=int, default=32)
    ap.add_argument("--evolve", type=int, default=2)
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    args = ap.parse_args(argv)
    report = run_stress(
        n=args.n,
        neuropil=args.neuropil,
        seed=args.seed,
        ticks=args.ticks,
        warm=args.warm,
        evolve=args.evolve,
        out_dir=args.out,
    )
    print(json.dumps({
        "run_id": report["run_id"],
        "scoreboard": report["scoreboard"],
        "er_task_error": report["er"]["task_error"],
        "fly_task_error": report["fly_adj"]["task_error"],
        "gaps": [{"metric": g["metric"], "winner": g["winner"]} for g in report["gaps"]],
        "md": report["md_path"],
    }, indent=2))
    # exit 0 always for first exploratory stress; pass_matched is informational
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
