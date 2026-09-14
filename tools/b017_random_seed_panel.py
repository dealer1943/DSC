"""B017 — Profile D panel over random seeds drawn from 1–100 (tooling only)."""
from __future__ import annotations

import argparse
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from tools.flywire_stress import run_stress

DEFAULT_CELLS = (
    ("GNG", "preferential"),
    ("AVLP_R", "preferential"),
    ("ME_R", "sheet_hub"),
    ("LO_R", "laminar"),
)


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _parse_cells(raw: str | None) -> list[tuple[str, str]]:
    if not raw:
        return list(DEFAULT_CELLS)
    out: list[tuple[str, str]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise SystemExit(f"cell must be neuropil:family, got {part!r}")
        npil, fam = part.split(":", 1)
        out.append((npil.strip(), fam.strip()))
    return out


def _draw_seeds(n: int, lo: int, hi: int, draw_seed: int | None) -> tuple[list[int], int]:
    pool = list(range(lo, hi + 1))
    if n > len(pool):
        raise SystemExit(f"n_seeds={n} > pool size {len(pool)}")
    if draw_seed is None:
        draw_seed = secrets.randbelow(2**31 - 1) + 1
    rng = np.random.default_rng(draw_seed)
    picked = rng.choice(pool, size=n, replace=False)
    seeds = sorted(int(x) for x in picked)
    return seeds, int(draw_seed)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="B017 Profile D random-seed panel (retooling)")
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--n-seeds", type=int, default=8, help="how many seeds to draw from the pool")
    ap.add_argument("--seed-lo", type=int, default=1)
    ap.add_argument("--seed-hi", type=int, default=100)
    ap.add_argument(
        "--draw-seed",
        type=int,
        default=None,
        help="RNG seed for the draw itself (omit = OS entropy; always recorded)",
    )
    ap.add_argument("--ticks", type=int, default=256)
    ap.add_argument(
        "--cells",
        type=str,
        default=None,
        help="comma neuropil:family (default GNG/AVLP/ME/LO best-known)",
    )
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    ap.add_argument("--experiment-prefix", type=str, default="B017")
    ap.add_argument("--require-gng-lead", action="store_true")
    args = ap.parse_args(argv)

    cells = _parse_cells(args.cells)
    seeds, draw_seed = _draw_seeds(args.n_seeds, args.seed_lo, args.seed_hi, args.draw_seed)
    print(f"B017 draw_seed={draw_seed} seeds={seeds}", flush=True)

    rows: list[dict[str, Any]] = []
    for neuropil, family in cells:
        for seed in seeds:
            tag = f"{args.experiment_prefix}_{neuropil}_{family}_s{seed}"
            print(f"=== {tag} ===", flush=True)
            try:
                rep = run_stress(
                    n=args.n,
                    neuropil=neuropil,
                    seed=seed,
                    ticks=args.ticks,
                    warm=32,
                    evolve=2,
                    out_dir=args.out,
                    dsc_family=family,
                    experiment=tag,
                    prune_stress=False,
                    task_lag=2,
                    task_noise=0.20,
                )
                dsc_task = float((rep.get("dsc") or rep["er"])["task_error"])
                fly_task = float(rep["fly_adj"]["task_error"])
                rows.append(
                    {
                        "ok": True,
                        "neuropil": neuropil,
                        "dsc_family": family,
                        "seed": seed,
                        "run_id": rep["run_id"],
                        "fly_wins": int(rep["scoreboard"]["fly_adj_wins"]),
                        "dsc_wins": int(rep["scoreboard"]["dsc_wins"]),
                        "dsc_task": dsc_task,
                        "fly_task": fly_task,
                        "task_gap_dsc_minus_fly": dsc_task - fly_task,
                        "md": rep.get("md_path"),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                rows.append(
                    {
                        "ok": False,
                        "neuropil": neuropil,
                        "dsc_family": family,
                        "seed": seed,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                print("FAIL", tag, exc, flush=True)

    aggregates: list[dict[str, Any]] = []
    for neuropil, family in cells:
        cell_rows = [
            r
            for r in rows
            if r.get("ok") and r["neuropil"] == neuropil and r["dsc_family"] == family
        ]
        if not cell_rows:
            aggregates.append({"neuropil": neuropil, "dsc_family": family, "ok": False})
            continue
        gaps = np.array([r["task_gap_dsc_minus_fly"] for r in cell_rows], dtype=np.float64)
        dsc_t = np.array([r["dsc_task"] for r in cell_rows], dtype=np.float64)
        fly_t = np.array([r["fly_task"] for r in cell_rows], dtype=np.float64)
        dsc_sb = sum(r["dsc_wins"] for r in cell_rows)
        fly_sb = sum(r["fly_wins"] for r in cell_rows)
        task_dsc_wins = int(sum(1 for r in cell_rows if r["dsc_task"] < r["fly_task"]))
        task_fly_wins = int(sum(1 for r in cell_rows if r["fly_task"] < r["dsc_task"]))
        task_ties = len(cell_rows) - task_dsc_wins - task_fly_wins
        aggregates.append(
            {
                "ok": True,
                "neuropil": neuropil,
                "dsc_family": family,
                "n_seeds": len(cell_rows),
                "mean_dsc_task": float(dsc_t.mean()),
                "std_dsc_task": float(dsc_t.std()),
                "mean_fly_task": float(fly_t.mean()),
                "std_fly_task": float(fly_t.std()),
                "mean_task_gap_dsc_minus_fly": float(gaps.mean()),
                "std_task_gap": float(gaps.std()),
                "task_dsc_wins": task_dsc_wins,
                "task_fly_wins": task_fly_wins,
                "task_ties": task_ties,
                "scoreboard_dsc_wins_sum": dsc_sb,
                "scoreboard_fly_wins_sum": fly_sb,
            }
        )

    stamp = _utc()
    report: dict[str, Any] = {
        "bench": "B017",
        "protocol": "profile_d_random_seed_panel_v0",
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": f"B017_{stamp}",
        "n": args.n,
        "ticks": args.ticks,
        "seed_pool": [args.seed_lo, args.seed_hi],
        "n_seeds": args.n_seeds,
        "draw_seed": draw_seed,
        "seeds_drawn": seeds,
        "cells": [{"neuropil": a, "dsc_family": b} for a, b in cells],
        "rows": rows,
        "aggregates": aggregates,
        "notes": [
            "Tooling-only assay over tools.flywire_stress.run_stress.",
            "Seeds drawn at random from the pool — not a pre-selected list.",
            "task_gap = dsc_task - fly_task (negative => DSC better on task).",
        ],
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{report['run_id']}.json"
    md_path = out_dir / f"{report['run_id']}.md"

    lines = [
        f"# B017 random-seed Profile D panel — `{report['run_id']}`",
        "",
        f"- pool: `{args.seed_lo}–{args.seed_hi}` · drawn **{args.n_seeds}** seeds · `draw_seed={draw_seed}`",
        f"- seeds: `{seeds}`",
        f"- N={args.n} · hard harness lag=2 noise=0.20 · ticks={args.ticks}",
        "",
        "## Aggregates (task)",
        "",
        "| neuropil | family | n | mean gap (dsc−fly) | ±std | task wins D/F/T | scoreboard Σ D/F |",
        "|----------|--------|---|--------------------|------|-----------------|------------------|",
    ]
    for a in aggregates:
        if not a.get("ok"):
            lines.append(
                f"| {a.get('neuropil')} | {a.get('dsc_family')} | — | FAIL | — | — | — |"
            )
            continue
        lines.append(
            f"| {a['neuropil']} | {a['dsc_family']} | {a['n_seeds']} | "
            f"{a['mean_task_gap_dsc_minus_fly']:.6g} | {a['std_task_gap']:.6g} | "
            f"{a['task_dsc_wins']}/{a['task_fly_wins']}/{a['task_ties']} | "
            f"{a['scoreboard_dsc_wins_sum']}/{a['scoreboard_fly_wins_sum']} |"
        )
    lines += [
        "",
        "## Layman",
        "",
        "Negative mean gap = DSC lower task error than fly wiring (good for us). "
        "Task wins = how often DSC beat fly on that seed. "
        "Scoreboard Σ still mixes efficiency axes.",
        "",
        "## Per-seed rows",
        "",
        "| neuropil | seed | dsc_task | fly_task | gap | sb D/F |",
        "|----------|------|----------|----------|-----|--------|",
    ]
    for r in rows:
        if not r.get("ok"):
            lines.append(f"| {r.get('neuropil')} | {r.get('seed')} | FAIL | — | — | — |")
            continue
        lines.append(
            f"| {r['neuropil']} | {r['seed']} | {r['dsc_task']:.6g} | {r['fly_task']:.6g} | "
            f"{r['task_gap_dsc_minus_fly']:.6g} | {r['dsc_wins']}/{r['fly_wins']} |"
        )

    md_path.write_text("\n".join(lines) + "\n")
    report["json_path"] = str(json_path)
    report["md_path"] = str(md_path)
    json_path.write_text(json.dumps(report, indent=2) + "\n")

    print(
        json.dumps(
            {
                "run_id": report["run_id"],
                "draw_seed": draw_seed,
                "seeds_drawn": seeds,
                "aggregates": aggregates,
                "md": md_path.name,
                "json": json_path.name,
            },
            indent=2,
        )
    )

    if args.require_gng_lead:
        gng = next((a for a in aggregates if a.get("neuropil") == "GNG" and a.get("ok")), None)
        if gng is None or gng["mean_task_gap_dsc_minus_fly"] >= 0:
            return 1
    return 0 if all(r.get("ok") for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
