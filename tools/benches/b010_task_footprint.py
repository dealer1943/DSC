"""B010 — task error vs active footprint (runnable)."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


def _dir_bytes(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    total = 0
    for root, _, files in os.walk(p):
        for fn in files:
            try:
                total += (Path(root) / fn).stat().st_size
            except OSError:
                pass
    return total


def run(
    dsc_dir: Path,
    ticks: int = 64,
    seed: int = 42,
    *,
    mutate_active: bool = False,
) -> dict[str, Any]:
    """Tick on a temp copy by default so MODEL/active harness state is preserved."""
    from dsc.runtime import load_mvp

    dsc_dir = Path(dsc_dir)
    tmp_ctx = None
    work = dsc_dir
    disk = _dir_bytes(dsc_dir)
    if not mutate_active:
        tmp_ctx = tempfile.TemporaryDirectory(prefix="b010_")
        work = Path(tmp_ctx.name) / "active"
        shutil.copytree(dsc_dir, work)
    try:
        rt = load_mvp(work)
        rt.harness.reset(seed=seed)
        errs = []
        for _ in range(ticks):
            rt.tick(1)
            errs.append(float(rt.harness.last_err))
        task_error = float(np.mean(errs[-max(1, ticks // 4) :]))
        active = int(rt.pop.n)
        latent_n = len(getattr(rt.latent, "entries", []) or [])
        edges = int(rt.sub.n_edges)
        sparse = float((np.asarray(rt.pop.activity) < 1e-6).mean())
        proxy = 1.0 / (1.0 + task_error)
        return {
            "bench": "B010",
            "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "seed": seed,
            "ticks": ticks,
            "mutated_active": bool(mutate_active),
            "task_error": task_error,
            "task_utility_proxy": proxy,
            "active_cells": active,
            "dormant_proxy_latent": latent_n,
            "disk_bytes": disk,
            "n_edges": edges,
            "activation_sparsity": sparse,
            "E_disk": proxy / max(disk, 1),
            "E_edge": proxy / max(edges, 1),
            "pass": task_error <= 0.05,
            "rule": "task_error<=0.05 (aligned with F020 G1)",
        }
    finally:
        if tmp_ctx is not None:
            tmp_ctx.cleanup()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsc", type=Path, default=Path("MODEL/active"))
    ap.add_argument("--ticks", type=int, default=64)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    ap.add_argument("--mutate-active", action="store_true")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    rep = run(args.dsc, ticks=args.ticks, seed=args.seed, mutate_active=args.mutate_active)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = args.out / f"B010_{stamp}.json"
    path.write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({"pass": rep["pass"], "json": path.name, "task_error": rep["task_error"]}, indent=2))
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
