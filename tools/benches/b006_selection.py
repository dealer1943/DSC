"""B006 — evolution selection signal (runnable)."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

DELTA = 1e-4
POST_TICKS = 16


def run(
    dsc_dir: Path,
    cycles: int = 3,
    seed: int = 42,
    *,
    mutate_active: bool = False,
    delta: float = DELTA,
    post_ticks: int = POST_TICKS,
) -> dict[str, Any]:
    """Evolve on a temp copy by default.

    After evolve, run post_ticks so utilities re-score (elites are sticky until tick).
    Pass: (mean OR elite utility ↑ by delta) AND typed_frac non-decrease AND not no-op.
    Typed-only pass is not enough (adversarial F5).
    """
    from dsc.runtime import load_mvp

    dsc_dir = Path(dsc_dir)
    tmp_ctx = None
    work = dsc_dir
    if not mutate_active:
        tmp_ctx = tempfile.TemporaryDirectory(prefix="b006_")
        work = Path(tmp_ctx.name) / "active"
        shutil.copytree(dsc_dir, work)
    try:
        rt = load_mvp(work)
        # warm score before
        rt.harness.reset(seed=seed)
        for _ in range(post_ticks):
            rt.tick(1)
        before_u = float(np.mean(rt.pop.utility))
        before_typed = float((rt.pop.differentiation >= 0.35).mean())
        elite_before = float(np.sort(rt.pop.utility)[-min(8, rt.pop.n) :].mean())

        rt.evolve(n=cycles, seed=seed)
        for _ in range(post_ticks):
            rt.tick(1)

        after_u = float(np.mean(rt.pop.utility))
        after_typed = float((rt.pop.differentiation >= 0.35).mean())
        elite_after = float(np.sort(rt.pop.utility)[-min(8, rt.pop.n) :].mean())

        mean_ok = after_u >= before_u + delta
        elite_ok = elite_after >= elite_before + delta
        typed_ok = after_typed >= before_typed - 1e-9
        noop = (
            abs(after_u - before_u) < 1e-12
            and abs(elite_after - elite_before) < 1e-12
            and abs(after_typed - before_typed) < 1e-12
        )
        passed = bool((mean_ok or elite_ok) and typed_ok and not noop)

        return {
            "bench": "B006",
            "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "seed": seed,
            "cycles": cycles,
            "post_ticks": post_ticks,
            "mutated_active": bool(mutate_active),
            "delta": delta,
            "before": {
                "utility_mean": before_u,
                "typed_frac": before_typed,
                "elite_utility_mean": elite_before,
            },
            "after": {
                "utility_mean": after_u,
                "typed_frac": after_typed,
                "elite_utility_mean": elite_after,
            },
            "noop": noop,
            "pass": passed,
            "rule": "(mean OR elite utility ↑ by delta) AND typed non-decrease; fail on no-op; post-tick re-score",
        }
    finally:
        if tmp_ctx is not None:
            tmp_ctx.cleanup()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsc", type=Path, default=Path("MODEL/active"))
    ap.add_argument("--cycles", type=int, default=3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    ap.add_argument("--mutate-active", action="store_true")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    rep = run(args.dsc, cycles=args.cycles, seed=args.seed, mutate_active=args.mutate_active)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = args.out / f"B006_{stamp}.json"
    path.write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({"pass": rep["pass"], "json": path.name, "noop": rep["noop"], **rep["after"]}, indent=2))
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
