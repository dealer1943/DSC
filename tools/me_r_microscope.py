"""R004 — put ME_R (or LO_R) fly vs DSC wiring under a microscope (tooling only)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _topo(adj: np.ndarray, label: str) -> dict[str, Any]:
    A = (adj > 0).astype(np.uint8)
    n = int(A.shape[0])
    n_edges = int(A.sum())
    density = float(n_edges / max(1, n * (n - 1)))
    in_deg = A.sum(axis=0).astype(np.float64)
    out_deg = A.sum(axis=1).astype(np.float64)
    tot = in_deg + out_deg
    mutual = int((A & A.T).sum() // 2)
    recip_edges = int((A & A.T).sum())
    recip_rate = float(recip_edges / max(1, n_edges))
    U = ((A + A.T) > 0).astype(np.uint8)
    np.fill_diagonal(U, 0)
    A2 = U @ U
    triangles = float(np.trace(U @ A2) / 6.0) if n <= 2048 else float("nan")
    deg_u = U.sum(axis=1).astype(np.float64)
    wedges = float(np.sum(deg_u * (deg_u - 1) / 2.0))
    clustering = float(3.0 * triangles / wedges) if wedges > 0 else 0.0
    k = max(1, int(round(0.05 * n)))
    top = np.argsort(out_deg)[-k:]
    hub_out_share = float(out_deg[top].sum() / max(1.0, out_deg.sum()))
    src, dst = np.where(A)
    if len(src):
        hop = np.abs(src.astype(np.float64) - dst.astype(np.float64))
        mean_index_dist = float(hop.mean() / max(1, n))
        median_index_dist = float(np.median(hop) / max(1, n))
        local_frac = float(np.mean(hop <= max(1, n // 16)))
    else:
        mean_index_dist = median_index_dist = local_frac = 0.0

    def _skew(x: np.ndarray) -> float:
        m = float(x.mean()) if len(x) else 0.0
        s = float(x.std()) or 1.0
        return float(np.mean(((x - m) / s) ** 3))

    return {
        "label": label,
        "n": n,
        "n_edges": n_edges,
        "density": density,
        "degree_mean": float(tot.mean()),
        "degree_median": float(np.median(tot)),
        "degree_max": float(tot.max()) if n else 0.0,
        "degree_p95": float(np.percentile(tot, 95)) if n else 0.0,
        "in_degree_mean": float(in_deg.mean()),
        "out_degree_mean": float(out_deg.mean()),
        "degree_skew": _skew(tot),
        "out_degree_skew": _skew(out_deg),
        "reciprocity_edge_frac": recip_rate,
        "mutual_undirected_pairs": mutual,
        "clustering_undirected": clustering,
        "hub_out_share_top5pct": hub_out_share,
        "mean_index_dist_norm": mean_index_dist,
        "median_index_dist_norm": median_index_dist,
        "local_index_edge_frac": local_frac,
    }


def _delta(fly: dict[str, Any], dsc: dict[str, Any], keys: list[str]) -> list[dict[str, Any]]:
    rows = []
    for k in keys:
        fv, dv = fly.get(k), dsc.get(k)
        if not isinstance(fv, (int, float)) or not isinstance(dv, (int, float)):
            continue
        if not np.isfinite(fv) or not np.isfinite(dv):
            continue
        rows.append({
            "metric": k,
            "fly": float(fv),
            "dsc": float(dv),
            "dsc_minus_fly": float(dv - fv),
            "rel_pct": float(100.0 * (dv - fv) / fv) if abs(fv) > 1e-12 else None,
        })
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="R004 ME_R/LO_R fly vs DSC microscope")
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--neuropil", type=str, default="ME_R")
    ap.add_argument("--dsc-family", type=str, default="sheet_hub")
    ap.add_argument("--with-stress", action="store_true")
    ap.add_argument("--ticks", type=int, default=256)
    ap.add_argument("--out", type=Path, default=Path("BENCHMARKS/runs"))
    ap.add_argument("--feather", type=Path, default=None)
    args = ap.parse_args(argv)

    from tools.flywire_subgraph.extract import extract_subgraph, save_subgraph
    from dsc.substrate import generate_substrate

    feather = Path(args.feather or "MODELS/fly/flywire_v783/proofread_connections_783.feather")
    bundle = extract_subgraph(feather, n=args.n, neuropil=args.neuropil, seed=args.seed)
    sub_path = Path(f"MODELS/fly/subgraphs/n{args.n}_{args.neuropil}_s{args.seed}.npz")
    save_subgraph(bundle, sub_path)

    fly_adj = bundle["adj"].astype(np.uint8)
    fly_edges = int(fly_adj.sum())
    dsc_sub = generate_substrate(
        n=args.n, seed=args.seed, family=args.dsc_family, target_edges=fly_edges,
    )
    dsc_adj = dsc_sub.adj.astype(np.uint8)

    fly_t = _topo(fly_adj, f"fly_{args.neuropil}")
    dsc_t = _topo(dsc_adj, f"dsc_{args.dsc_family}")
    compare_keys = [
        "n_edges", "density", "degree_mean", "degree_median", "degree_max", "degree_p95",
        "degree_skew", "out_degree_skew", "reciprocity_edge_frac", "clustering_undirected",
        "hub_out_share_top5pct", "mean_index_dist_norm", "median_index_dist_norm",
        "local_index_edge_frac",
    ]
    deltas = _delta(fly_t, dsc_t, compare_keys)
    ranked = sorted(
        [d for d in deltas if d.get("rel_pct") is not None],
        key=lambda d: abs(d["rel_pct"]),
        reverse=True,
    )

    stress = None
    if args.with_stress:
        from tools.flywire_stress import run_stress
        rep = run_stress(
            n=args.n, neuropil=args.neuropil, seed=args.seed, ticks=args.ticks,
            warm=32, evolve=2, out_dir=args.out, dsc_family=args.dsc_family,
            experiment=f"R004_micro_{args.neuropil}_{args.dsc_family}_s{args.seed}",
            task_lag=2, task_noise=0.20,
        )
        stress = {
            "run_id": rep["run_id"],
            "scoreboard": rep["scoreboard"],
            "dsc_task": (rep.get("dsc") or rep["er"])["task_error"],
            "fly_task": rep["fly_adj"]["task_error"],
            "gaps": rep["gaps"],
            "md": rep.get("md_path"),
        }

    stamp = _utc()
    run_id = f"{args.neuropil}_micro_{stamp}"
    report = {
        "assay": "R004_microscope",
        "run_id": run_id,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "neuropil": args.neuropil,
        "n": args.n,
        "seed": args.seed,
        "dsc_family": dsc_sub.meta.get("family", args.dsc_family),
        "subgraph": sub_path.name,
        "fly_topology": fly_t,
        "dsc_topology": dsc_t,
        "deltas": deltas,
        "ranked_rel_gaps": ranked[:10],
        "stress": stress,
        "notes": [
            "Tooling only — does not edit dsc/ generators.",
            "Index-distance metrics are procedural proxies, not soma coordinates.",
            "Priority: ME_R first, then LO_R (same tool --neuropil LO_R).",
        ],
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{run_id}.json"
    md_path = out_dir / f"{run_id}.md"

    md = []
    md.append(f"# Microscope — `{args.neuropil}` fly vs DSC `{args.dsc_family}`")
    md.append("")
    md.append(f"- run: `{run_id}` · N={args.n} · seed={args.seed}")
    md.append(f"- fly subgraph: `{sub_path.name}` · edges fly={fly_t['n_edges']} dsc={dsc_t['n_edges']}")
    md.append("")
    md.append("## Layman")
    md.append("")
    md.append(
        "Same seat count and edge budget. Graph shape under glass: hub peakiness, "
        "two-way wires, clustering, and whether edges stay local on the sheet index. "
        "Biggest %-gaps are the first knobs to suspect when ME_R (then LO_R) loses on task."
    )
    md.append("")
    md.append("## Topology side-by-side")
    md.append("")
    md.append("| metric | fly | dsc | dsc−fly | rel % |")
    md.append("|--------|-----|-----|---------|-------|")
    for d in deltas:
        rel = "—" if d["rel_pct"] is None else f"{d['rel_pct']:+.2f}%"
        md.append(
            f"| `{d['metric']}` | {d['fly']:.6g} | {d['dsc']:.6g} | "
            f"{d['dsc_minus_fly']:.6g} | {rel} |"
        )
    md.append("")
    md.append("## Largest relative gaps")
    md.append("")
    for d in ranked[:8]:
        md.append(
            f"- **{d['metric']}**: fly={d['fly']:.4g} dsc={d['dsc']:.4g} "
            f"({d['rel_pct']:+.1f}%)"
        )
    if stress:
        md.append("")
        md.append("## Dynamics (Profile D hard, this seed)")
        md.append("")
        md.append(
            f"- scoreboard fly {stress['scoreboard']['fly_adj_wins']} · "
            f"dsc {stress['scoreboard']['dsc_wins']}"
        )
        md.append(
            f"- task_error dsc={stress['dsc_task']:.6g} fly={stress['fly_task']:.6g}"
        )
        md.append("")
        md.append("| metric | winner |")
        md.append("|--------|--------|")
        for g in stress["gaps"]:
            md.append(f"| {g['metric']} | **{g['winner']}** |")
    md.append("")
    md.append("## Next")
    md.append("")
    md.append(
        "Use ranked gaps for procedural generator tweaks (anti-overfit), "
        "re-run microscope + B017 ME_R-only. Then LO_R."
    )
    md_path.write_text(chr(10).join(md) + chr(10))
    report["json_path"] = str(json_path)
    report["md_path"] = str(md_path)
    json_path.write_text(json.dumps(report, indent=2) + chr(10))

    print(json.dumps({
        "run_id": run_id,
        "neuropil": args.neuropil,
        "dsc_family": args.dsc_family,
        "top_gaps": [{"metric": d["metric"], "rel_pct": d["rel_pct"]} for d in ranked[:5]],
        "stress": ({
            "scoreboard": stress["scoreboard"],
            "dsc_task": stress["dsc_task"],
            "fly_task": stress["fly_task"],
        } if stress else None),
        "md": md_path.name,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
