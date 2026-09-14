"""F020 — DSC development run protocol (dev_run_v0)."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROTOCOL = "dev_run_v0"
_ABS = re.compile(r"(?:/Users/|/home/|/workspace/|/var/|/opt/|Mac\.home\.local)")


def _path_leaks(text: str) -> list[str]:
    return sorted(set(_ABS.findall(text)))


def run_protocol(
    seed: int = 42,
    t_warm: int = 64,
    e1: int = 3,
    t_train: int = 256,
    e2: int = 2,
    t_eval: int = 64,
    out_dir: Path | None = None,
    dsc_dir: Path | None = None,
    fly_root: Path | None = None,
    skip_b016: bool = False,
) -> dict[str, Any]:
    from dsc.runtime import load_mvp
    from dsc.meta.manager import append_row
    from tools.benches.b006_selection import run as run_b006
    from tools.benches.b010_task_footprint import run as run_b010
    from tools.flywire_efficiency_bench.bench import run_bench

    out_dir = Path(out_dir or "BENCHMARKS/runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    dsc_dir = Path(dsc_dir or "MODEL/active")
    fly_root = Path(fly_root or "MODELS/fly/flywire_v783")
    active = Path("MODEL/active")

    rt = load_mvp(dsc_dir)
    # pre-run footprint for real G3
    from tools.benches.b010_task_footprint import _dir_bytes

    disk_before = _dir_bytes(active if active.exists() else dsc_dir)
    # warmup / train
    rt.harness.reset(seed=seed)
    for _ in range(t_warm):
        rt.tick(1)
    rt.evolve(n=e1, seed=seed)
    for _ in range(t_train):
        rt.tick(1)
    if e2 > 0:
        rt.evolve(n=e2, seed=seed + 1)
    errs = []
    for _ in range(t_eval):
        rt.tick(1)
        errs.append(float(rt.harness.last_err))
    task_error = sum(errs[len(errs) // 2 :]) / max(1, len(errs) - len(errs) // 2)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ckpt_name = f"dsc_dev_{stamp}"
    saved = rt.save_named(ckpt_name)
    # Assert active refresh (save_named uses also_active=)
    if not active.exists():
        raise RuntimeError("MODEL/active missing after save_named")
    man = json.loads((active / "manifest.json").read_text())
    # Benches on refreshed active (copies inside B006/B010/B016)
    b006 = run_b006(active, cycles=2, seed=seed)
    b010 = run_b010(active, ticks=t_eval, seed=seed)
    b016 = None
    b016_skip_reason = None
    if skip_b016:
        b016_skip_reason = "skip_b016"
    else:
        b016 = run_bench(
            dsc_path=active,
            fly_root=fly_root,
            profiles=("A", "B", "C", "E"),
            seed=seed,
            ticks=min(256, max(32, t_train)),
            out_dir=out_dir,
        )

    disk_after = int(b010.get("disk_bytes") or _dir_bytes(active))
    e_disk_after = float(b010.get("E_disk") or 0.0)
    # G1 task
    g1 = task_error <= 0.05
    # G2 evolve — inherits tightened B006
    g2 = bool(b006.get("pass"))
    # G3 footprint — byte cap AND meaningful E_disk (not >0 vacuous)
    baseline_bytes = max(disk_before, 1)
    g3 = disk_after <= 2 * baseline_bytes and e_disk_after >= 1e-7
    # G4 honesty — require B016 Profile A + no path leaks; skip => fail
    g4 = False
    g5 = False
    if b016 is None:
        g4 = False
        g5 = False
    else:
        has_a = bool((b016.get("profiles") or {}).get("A"))
        blob = ""
        jname = b016.get("json_path")
        mname = b016.get("md_path")
        if jname:
            blob += (out_dir / jname).read_text(encoding="utf-8")
        if mname:
            blob += (out_dir / mname).read_text(encoding="utf-8")
        leaks = _path_leaks(blob)
        g4 = has_a and not leaks
        bprof = (b016.get("profiles") or {}).get("B") or {}
        tw = bprof.get("tick_wall_us")
        g5 = bool(bprof.get("dynamics")) and tw is not None and float(tw) == float(tw)  # finite

    gates = {
        "G1_task": g1,
        "G2_evolve": g2,
        "G3_footprint": g3,
        "G4_honesty": g4,
        "G5_dynamics": g5,
    }
    if b016_skip_reason:
        gates["skip_b016"] = True
    passed = all(bool(gates[k]) for k in ("G1_task", "G2_evolve", "G3_footprint", "G4_honesty", "G5_dynamics"))

    summary = {
        "protocol": PROTOCOL,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "checkpoint": ckpt_name,
        "saved": Path(saved).name if saved else None,
        "task_error_eval": task_error,
        "disk_before": disk_before,
        "disk_after": disk_after,
        "gates": gates,
        "pass": passed,
        "b006": b006,
        "b010": b010,
        "b016_run_id": (b016 or {}).get("run_id"),
        "b016_pass": (b016 or {}).get("pass"),
        "b016_pass_kind": (b016 or {}).get("pass_kind"),
        "params": {
            "t_warm": t_warm,
            "e1": e1,
            "t_train": t_train,
            "e2": e2,
            "t_eval": t_eval,
            "skip_b016": skip_b016,
        },
    }
    sum_path = out_dir / f"dev_run_{stamp}.json"
    sum_path.write_text(json.dumps(summary, indent=2, default=str) + "\n")
    append_row(
        "dev_run",
        {
            "protocol": PROTOCOL,
            "pass": passed,
            "gates": gates,
            "checkpoint": ckpt_name,
            "task_error_eval": task_error,
            "b016_run_id": summary["b016_run_id"],
            "b016_pass_kind": summary["b016_pass_kind"],
            "summary": sum_path.name,
        },
    )
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="F020 DSC development run")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    ap.add_argument("--dsc", type=Path, default=Path("MODEL/active"))
    ap.add_argument("--flywire", type=Path, default=Path("MODELS/fly/flywire_v783"))
    ap.add_argument("--skip-b016", action="store_true")
    ap.add_argument("--t-warm", type=int, default=64)
    ap.add_argument("--e1", type=int, default=3)
    ap.add_argument("--t-train", type=int, default=256)
    ap.add_argument("--e2", type=int, default=2)
    ap.add_argument("--t-eval", type=int, default=64)
    args = ap.parse_args(argv)
    summary = run_protocol(
        seed=args.seed,
        t_warm=args.t_warm,
        e1=args.e1,
        t_train=args.t_train,
        e2=args.e2,
        t_eval=args.t_eval,
        out_dir=args.out,
        dsc_dir=args.dsc,
        fly_root=args.flywire,
        skip_b016=args.skip_b016,
    )
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "protocol",
                    "pass",
                    "gates",
                    "checkpoint",
                    "task_error_eval",
                    "b016_run_id",
                    "b016_pass_kind",
                )
            },
            indent=2,
        )
    )
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
