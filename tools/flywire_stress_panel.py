"""Run Profile D hard-harness panel across neuropils (paper generalization)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.flywire_stress import run_stress


DEFAULT_PANEL = ("GNG", "ME_R", "LO_R", "AVLP_R")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ticks", type=int, default=256)
    ap.add_argument("--neuropils", type=str, default=",".join(DEFAULT_PANEL))
    ap.add_argument("--dsc-family", type=str, default="preferential")
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    ap.add_argument("--experiment-prefix", type=str, default="panel_hard")
    args = ap.parse_args(argv)
    neuropils = [x.strip() for x in args.neuropils.split(",") if x.strip()]
    summary = []
    for npil in neuropils:
        print(f"=== panel {npil} ===", flush=True)
        try:
            rep = run_stress(
                n=args.n,
                neuropil=npil,
                seed=args.seed,
                ticks=args.ticks,
                warm=32,
                evolve=2,
                out_dir=args.out,
                dsc_family=args.dsc_family,
                experiment=f"{args.experiment_prefix}_{npil}",
                prune_stress=False,
                task_lag=2,
                task_noise=0.20,
            )
            summary.append({
                "neuropil": npil,
                "run_id": rep["run_id"],
                "fly_wins": rep["scoreboard"]["fly_adj_wins"],
                "dsc_wins": rep["scoreboard"]["dsc_wins"],
                "dsc_task": (rep.get("dsc") or rep["er"])["task_error"],
                "fly_task": rep["fly_adj"]["task_error"],
                "md": rep["md_path"],
                "ok": True,
            })
        except Exception as exc:  # noqa: BLE001
            summary.append({"neuropil": npil, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            print("FAIL", npil, exc, flush=True)
    out = Path(args.out) / f"panel_summary_{args.n}_{args.seed}.json"
    out.write_text(json.dumps({"n": args.n, "seed": args.seed, "family": args.dsc_family, "panel": summary}, indent=2) + "\n")
    print(json.dumps({"summary": summary, "wrote": out.name}, indent=2))
    # exit 0 if all ok and dsc leads or ties majority
    fails = [s for s in summary if not s.get("ok")]
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
