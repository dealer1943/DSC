"""R005 regime-mode tooling — graph stats → r → family mix (no neuropil hardcodes)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Soft regime axes (values in ~[0,1] after calibration vs ER baseline)
REGIME_KEYS = ("hub", "local", "recip", "cluster", "dense")
# NOTE: "local" is extract_order_local_frac (|i-j| after BFS id_map) — NOT anatomy.
# Always report permute_ablation alongside; do not claim retinotopy from this axis alone.

# Procedural families the mixer may weight (aliases match generate_substrate)
FAMILIES = ("preferential", "sheet_hub", "modular", "laminar", "erdos_renyi")


def _topo_raw(adj: np.ndarray) -> Dict[str, float]:
    A = (adj > 0).astype(np.uint8)
    n = int(A.shape[0])
    n_edges = int(A.sum())
    in_deg = A.sum(axis=0).astype(np.float64)
    out_deg = A.sum(axis=1).astype(np.float64)
    tot = in_deg + out_deg
    recip_edges = int((A & A.T).sum())
    recip_rate = float(recip_edges / max(1, n_edges))
    U = ((A + A.T) > 0).astype(np.uint8)
    np.fill_diagonal(U, 0)
    deg_u = U.sum(axis=1).astype(np.float64)
    wedges = float(np.sum(deg_u * (deg_u - 1) / 2.0))
    if n <= 2048 and wedges > 0:
        clustering = float(3.0 * (np.trace(U @ (U @ U)) / 6.0) / wedges)
    else:
        clustering = 0.0
    k = max(1, int(round(0.05 * n)))
    top = np.argsort(out_deg)[-k:]
    hub_share = float(out_deg[top].sum() / max(1.0, out_deg.sum()))
    src, dst = np.where(A)
    if len(src):
        hop = np.abs(src.astype(np.float64) - dst.astype(np.float64))
        local_frac = float(np.mean(hop <= max(1, n // 16)))
    else:
        local_frac = 0.0
    m = float(tot.mean()) if n else 0.0
    s = float(tot.std()) or 1.0
    skew = float(np.mean(((tot - m) / s) ** 3)) if n else 0.0
    density = float(n_edges / max(1, n * (n - 1)))
    return {
        "n": float(n),
        "n_edges": float(n_edges),
        "density": density,
        "degree_skew": skew,
        "hub_out_share_top5pct": hub_share,
        "extract_order_local_frac": local_frac,
        "reciprocity_edge_frac": recip_rate,
        "clustering_undirected": clustering,
    }


def _sigmoid(x: float) -> float:
    x = float(np.clip(x, -20.0, 20.0))
    return float(1.0 / (1.0 + np.exp(-x)))



def permute_index_ablation(adj: np.ndarray, *, seed: int = 0, n_perm: int = 8) -> Dict[str, float]:
    """Mean extract_order_local_frac after random node-index permutations.

    If raw local ≈ permuted mean, the axis was mostly id_map packing (BFS discovery
    order), not anatomy. Always report; never claim retinotopy from this alone.
    """
    A = (adj > 0).astype(np.uint8)
    n = int(A.shape[0])
    rng = np.random.default_rng(seed + 77)
    vals = []
    for _ in range(max(1, n_perm)):
        perm = rng.permutation(n)
        Ap = A[np.ix_(perm, perm)]
        vals.append(_topo_raw(Ap)["extract_order_local_frac"])
    raw_local = _topo_raw(A)["extract_order_local_frac"]
    mean_p = float(np.mean(vals))
    return {
        "extract_order_local_frac": float(raw_local),
        "permuted_local_mean": mean_p,
        "permuted_local_std": float(np.std(vals)),
        "local_minus_permuted": float(raw_local - mean_p),
        "local_likely_extract_artifact": bool(abs(raw_local - mean_p) < 0.05),
        "n_perm": int(n_perm),
        "note": "local axis is |i-j| on extract id_map order — not soma geometry",
    }


def _er_baseline(n: int, n_edges: int, seed: int = 0) -> Dict[str, float]:
    """Neutral procedural baseline (ER), same N/E — never a fly snapshot."""
    from dsc.substrate import generate_substrate

    sub = generate_substrate(
        n=n,
        seed=seed + 911,
        family="erdos_renyi_directed",
        target_edges=n_edges,
    )
    return _topo_raw(sub.adj)


def regime_features(
    adj: np.ndarray,
    *,
    baseline: Optional[Dict[str, float]] = None,
    baseline_seed: int = 0,
) -> Dict[str, Any]:
    """
    Map adjacency → soft regime vector r in [0,1]^k.
    Calibration is vs ER with same N/E (procedural), not vs FlyWire.
    """
    raw = _topo_raw(adj)
    n = int(raw["n"])
    n_edges = int(raw["n_edges"])
    if baseline is None:
        baseline = _er_baseline(n, n_edges, seed=baseline_seed)

    def z(key: str, scale: float) -> float:
        return (raw[key] - baseline.get(key, 0.0)) / scale

    # scales = typical ER noise floors; keep simple and documented
    r = {
        "hub": _sigmoid(0.85 * z("degree_skew", 0.75) + 0.85 * z("hub_out_share_top5pct", 0.05)),
        "local": _sigmoid(1.2 * z("extract_order_local_frac", 0.08)),
        "recip": _sigmoid(1.0 * z("reciprocity_edge_frac", 0.05)),
        "cluster": _sigmoid(1.0 * z("clustering_undirected", 0.03)),
        "dense": _sigmoid(1.0 * z("density", 0.01)),
    }
    ablation = permute_index_ablation(adj, seed=baseline_seed)
    # If local is likely an extract artifact, shrink its influence on r (honesty)
    if ablation.get("local_likely_extract_artifact"):
        r["local"] = float(r["local"] * 0.25)
    return {
        "r": r,
        "raw": raw,
        "baseline_er": baseline,
        "permute_ablation": ablation,
        "note": (
            "r calibrated vs ER same N/E — not vs fly anatomy; "
            "local=extract_order_local_frac (|i-j| on BFS id_map), see permute_ablation"
        ),
    }





def hub_governor_plan(r: Dict[str, float]) -> Dict[str, float]:
    """F031: on-ramp + soft ceilings for hub formation (from r only).

    hub_demand high ⇒ allow preferential genes; local high ⇒ suppress.
    Ceilings are z-score caps vs ER same N/E — not fly ME constants.
    """
    hub = float(r.get("hub", 0.0))
    local = float(r.get("local", 0.0))
    # On-ramp: integration demand net of sheet-local pressure
    hub_demand = float(np.clip(hub * (1.0 - 0.55 * local), 0.0, 1.0))
    # Soft ceilings (ASSAY knobs — same hand ER-z floors as R005; not fly-fitted)
    z_skew_max = float(1.0 + 2.2 * hub_demand)          # ~1..3.2 assay
    z_hub_share_max = float(0.8 + 2.0 * hub_demand)     # ~0.8..2.8 assay
    alpha_cap = float(1.0 + 0.50 * hub_demand)          # ≤~1.5
    beta_cap = float(1.0 + 0.30 * hub_demand)
    # sigma: do not over-tighten when hubs are also rising (overshoot interaction)
    sigma_floor = float(np.clip(0.55 + 0.20 * (1.0 - hub_demand), 0.50, 0.85))
    return {
        "hub_demand": hub_demand,
        "z_skew_max": z_skew_max,
        "z_hub_share_max": z_hub_share_max,
        "alpha_cap": alpha_cap,
        "beta_cap": beta_cap,
        "sigma_floor": sigma_floor,
        "ceiling_note": "assay ER-z hand scales (R005-aligned); not fly ME constants",
    }


def govern_substrate_genes(
    r: Dict[str, float],
    genes: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Clip sheet_hub genes through F031 hub governor (pre-generate)."""
    g = dict(genes or substrate_genes_from_r(r))
    plan = hub_governor_plan(r)
    g["alpha"] = float(np.clip(float(g.get("alpha", 1.0)), 0.75, plan["alpha_cap"]))
    g["beta"] = float(np.clip(float(g.get("beta", 1.0)), 0.75, plan["beta_cap"]))
    # Prevent ultra-tight σ while α is elevated (v0.2 overshoot mode)
    g["sigma_scale"] = float(max(float(g.get("sigma_scale", 1.0)), plan["sigma_floor"]))
    g["sigma_scale"] = float(np.clip(g["sigma_scale"], 0.45, 1.0))
    if "p_recip_scale" in g:
        g["p_recip_scale"] = float(np.clip(float(g["p_recip_scale"]), 0.85, 1.40))
    return {"genes": g, "plan": plan}


def _z_vs_er(raw: Dict[str, float], baseline: Dict[str, float], key: str, scale: float) -> float:
    return (float(raw.get(key, 0.0)) - float(baseline.get(key, 0.0))) / max(scale, 1e-9)


def generate_sheet_hub_governed(
    *,
    n: int,
    target_edges: int,
    seed: int,
    r: Dict[str, float],
    genes: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Build sheet_hub with F031 governor: clip genes, generate, one backoff regenerate if needed."""
    from dsc.substrate import generate_substrate

    gov0 = govern_substrate_genes(r, genes)
    genes0 = gov0["genes"]
    plan = gov0["plan"]
    sub0 = generate_substrate(
        n=n, seed=seed, family="sheet_hub", target_edges=target_edges, sheet_genes=genes0
    )
    raw0 = _topo_raw(sub0.adj.astype(np.uint8))
    base = _er_baseline(n, int(target_edges), seed=seed + 911)
    z_skew0 = _z_vs_er(raw0, base, "degree_skew", 0.75)
    z_hub0 = _z_vs_er(raw0, base, "hub_out_share_top5pct", 0.05)
    overshoot = bool(z_skew0 > plan["z_skew_max"] or z_hub0 > plan["z_hub_share_max"])
    report = {
        "plan": plan,
        "genes_initial": dict(genes0),
        "genes_final": dict(genes0),
        "overshoot_initial": overshoot,
        "regenerated": False,
        "z_skew": float(z_skew0),
        "z_hub_share": float(z_hub0),
        "raw": {k: float(raw0[k]) for k in (
            "degree_skew", "hub_out_share_top5pct", "extract_order_local_frac",
            "reciprocity_edge_frac", "clustering_undirected", "n_edges",
        )},
        "gather_hub_out_exp_nudge": 0.0,
    }
    sub = sub0
    if overshoot:
        genes1 = dict(genes0)
        genes1["alpha"] = float(np.clip(genes1["alpha"] * 0.85, 0.75, plan["alpha_cap"]))
        genes1["beta"] = float(np.clip(genes1["beta"] * 0.85, 0.75, plan["beta_cap"]))
        genes1["sigma_scale"] = float(np.clip(genes1["sigma_scale"] * 1.08, plan["sigma_floor"], 1.0))
        sub1 = generate_substrate(
            n=n, seed=seed, family="sheet_hub", target_edges=target_edges, sheet_genes=genes1
        )
        raw1 = _topo_raw(sub1.adj.astype(np.uint8))
        z_skew1 = _z_vs_er(raw1, base, "degree_skew", 0.75)
        z_hub1 = _z_vs_er(raw1, base, "hub_out_share_top5pct", 0.05)
        # Prefer regenerate if it reduces overshoot magnitude
        score0 = max(0.0, z_skew0 - plan["z_skew_max"]) + max(0.0, z_hub0 - plan["z_hub_share_max"])
        score1 = max(0.0, z_skew1 - plan["z_skew_max"]) + max(0.0, z_hub1 - plan["z_hub_share_max"])
        if score1 <= score0:
            sub = sub1
            report["genes_final"] = dict(genes1)
            report["regenerated"] = True
            report["z_skew"] = float(z_skew1)
            report["z_hub_share"] = float(z_hub1)
            report["raw"] = {k: float(raw1[k]) for k in report["raw"]}
            report["overshoot_final"] = bool(score1 > 0)
        else:
            report["overshoot_final"] = True
        # Peer: nudge only if FINAL still overshoots — else contaminates gene-only A/B
        if report["overshoot_final"]:
            report["gather_hub_out_exp_nudge"] = 0.08
        else:
            report["gather_hub_out_exp_nudge"] = 0.0
    else:
        report["overshoot_final"] = False
    report["substrate"] = sub
    return report


def substrate_genes_from_r(r: Dict[str, float]) -> Dict[str, float]:
    """Map soft regime vector r → sheet_hub generator genes (R005).

    Still one procedural family — only σ/α/β/p_recip change. No neuropil if,
    no fly constant tables. Aimed at R004 gaps: peakier hubs + tighter local
    kernel when r_hub/r_local are high.

    Layman: fat book ⇒ stronger preferential; ultra-local book ⇒ tighter
    spatial kernel; reciprocal edges ⇒ slightly more recip completion.
    """
    hub = float(r.get("hub", 0.0))
    local = float(r.get("local", 0.0))
    recip = float(r.get("recip", 0.0))
    cluster = float(r.get("cluster", 0.0))
    # v0.2 softer — v0.1 (α≈2.25, σ≈0.37) overshot degree_skew (9.8 vs fly 4.8)
    alpha = float(np.clip(1.0 + 0.55 * hub, 0.75, 1.75))
    beta = float(np.clip(1.0 + 0.35 * hub, 0.75, 1.55))
    # <1 tightens σ (more ultra-local edges)
    sigma_scale = float(np.clip(1.0 / (1.0 + 0.70 * local + 0.20 * cluster), 0.45, 1.0))
    p_recip_scale = float(np.clip(1.0 + 0.30 * recip, 0.85, 1.40))
    return {
        "alpha": alpha,
        "beta": beta,
        "sigma_scale": sigma_scale,
        "p_recip_scale": p_recip_scale,
    }


def gather_knobs_from_r(r: Dict[str, float]) -> Dict[str, Any]:
    """Map soft regime vector r → message-gather defaults (R005).

    No adjacency blend, no neuropil strings. Discrete family pick stays separate.
    Knobs are functions of r only (generalization test: same r ⇒ same knobs).

    Layman: fat hubs ⇒ damp hub shout; ultra-local book ⇒ listen more to the
    closest wired seat. Bilayer/talk are opt-in extremes (v0.1 mostly off).
    """
    hub = float(r.get("hub", 0.0))
    local = float(r.get("local", 0.0))
    cluster = float(r.get("cluster", 0.0))
    recip = float(r.get("recip", 0.0))
    # Continuous hub damp (default stack uses 0.5)
    hub_out_exp = float(np.clip(0.35 + 0.35 * hub, 0.25, 0.75))
    # Soft local blend — modest; full NEAREST_EXACT hurt task (R003)
    local_gather_mix = float(np.clip(0.02 + 0.28 * local, 0.0, 0.35))
    # v0.1: bilayer/talk off unless absurdly saturated (ME_R r~1 auto-on hurt)
    bilayer = bool(cluster >= 0.995)
    bilayer_mix = float(np.clip(0.12 + 0.38 * cluster, 0.08, 0.55))
    talk_board = bool(recip >= 0.995)
    talk_mix = float(np.clip(0.08 + 0.28 * recip, 0.05, 0.40))
    return {
        "HUB_AWARE": True,
        "HUB_OUT_EXP": hub_out_exp,
        "LOCAL_GATHER_MIX": local_gather_mix,
        "BILAYER": bilayer,
        "BILAYER_MIX": bilayer_mix,
        "TALK_BOARD": talk_board,
        "TALK_MIX": talk_mix,
        "NEAREST_EXACT": False,
        "note": "gather knobs from r only (hub+local primary); no adj blend; no neuropil if",
    }




def mode_weights(r: Dict[str, float]) -> Dict[str, float]:
    """Soft mix over procedural families from regime vector (R005 mixer sketch).

    Dense is ignored here (matched N/E makes r_dense uninformative).
    Recip bumps sheet_hub/modular lightly. Weights are diagnostic; v0 pick is argmax only
    (no fake adjacency blend, no hysteresis yet).
    """
    hub = float(r.get("hub", 0.0))
    local = float(r.get("local", 0.0))
    cluster = float(r.get("cluster", 0.0))
    recip = float(r.get("recip", 0.0))
    scores = {
        "preferential": 0.15 + 1.4 * hub,
        "sheet_hub": 0.15 + 1.1 * local + 0.5 * hub * local + 0.25 * recip,
        "modular": 0.10 + 1.2 * cluster + 0.20 * recip,
        "laminar": 0.10 + 1.0 * local * (1.0 - 0.7 * hub),
        "erdos_renyi": 0.15 + 0.35 * (1.0 - hub) * (1.0 - local),
    }
    s = sum(scores.values()) or 1.0
    return {k: float(v / s) for k, v in scores.items()}


def pick_family(weights: Dict[str, float]) -> str:
    return max(weights.items(), key=lambda kv: kv[1])[0]


def sense_adj(adj: np.ndarray, *, baseline_seed: int = 0) -> Dict[str, Any]:
    feat = regime_features(adj, baseline_seed=baseline_seed)
    w = mode_weights(feat["r"])
    knobs = gather_knobs_from_r(feat["r"])
    genes = substrate_genes_from_r(feat["r"])
    return {
        **feat,
        "weights": w,
        "pick": pick_family(w),
        "pick_is_discrete_argmax": True,
        "gather_knobs": knobs,
        "substrate_genes": genes,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="R005 regime-mode tooling")
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--neuropil", type=str, default="ME_R",
                    help="exam venue only — used to load a subgraph, never as an if-branch in dsc/")
    ap.add_argument("--sense", type=str, default="fly",
                    choices=("fly", "dsc"),
                    help="which adj to sense: fly subgraph or a generated DSC family")
    ap.add_argument("--dsc-family", type=str, default="sheet_hub",
                    help="control family for --with-stress A/B; also family when --sense dsc")
    ap.add_argument("--with-stress", action="store_true",
                    help="run Profile D hard with mixer pick vs fixed --dsc-family control")
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

    if args.sense == "fly":
        sensed = sense_adj(fly_adj, baseline_seed=args.seed)
        sense_label = f"fly:{args.neuropil}"
    else:
        dsc_sub = generate_substrate(
            n=args.n, seed=args.seed, family=args.dsc_family, target_edges=fly_edges
        )
        sensed = sense_adj(dsc_sub.adj, baseline_seed=args.seed)
        sense_label = f"dsc:{args.dsc_family}"

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"regime_{args.neuropil}_{stamp}"
    report: Dict[str, Any] = {
        "assay": "R005_regime_mode_tooling",
        "run_id": run_id,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n": args.n,
        "seed": args.seed,
        "exam_neuropil": args.neuropil,
        "sense": args.sense,
        "sense_label": sense_label,
        "subgraph": sub_path.name,
        "r": sensed["r"],
        "weights": sensed["weights"],
        "pick": sensed["pick"],
        "raw": sensed["raw"],
        "baseline_er": sensed["baseline_er"],
        "permute_ablation": sensed.get("permute_ablation"),
        "local_axis": "extract_order_local_frac",
        "notes": [
            "Tooling only. Neuropil selects the exam subgraph, not a dsc/ if-branch.",
            "r calibrated vs ER same N/E.",
            "pick = argmax family weight from mixer.",
        ],
    }

    stress = None
    if args.with_stress:
        from tools.flywire_stress import run_stress

        pick = sensed["pick"]
        control = args.dsc_family
        print(f"stress pick={pick} control={control}", flush=True)
        rep_pick = run_stress(
            n=args.n,
            neuropil=args.neuropil,
            seed=args.seed,
            ticks=args.ticks,
            warm=32,
            evolve=2,
            out_dir=args.out,
            dsc_family=pick,
            experiment=f"R005_regime_pick_{pick}_s{args.seed}",
            task_lag=2,
            task_noise=0.20,
        )
        rep_ctrl = run_stress(
            n=args.n,
            neuropil=args.neuropil,
            seed=args.seed,
            ticks=args.ticks,
            warm=32,
            evolve=2,
            out_dir=args.out,
            dsc_family=control,
            experiment=f"R005_regime_ctrl_{control}_s{args.seed}",
            task_lag=2,
            task_noise=0.20,
        )
        def _brief(rep):
            return {
                "run_id": rep["run_id"],
                "family": rep.get("dsc_family"),
                "scoreboard": rep["scoreboard"],
                "dsc_task": (rep.get("dsc") or rep["er"])["task_error"],
                "fly_task": rep["fly_adj"]["task_error"],
            }
        degenerate = str(pick).replace("_directed", "") == str(control).replace("_directed", "")
        stress = {
            "pick": _brief(rep_pick),
            "control": _brief(rep_ctrl),
            "dsc_family_requested_control": control,
            "regime_pick": pick,
            "degenerate_ab": degenerate,
            "note": (
                "pick==control — A/B is not informative"
                if degenerate else "pick differs from control"
            ),
        }
        report["stress"] = stress

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{run_id}.json"
    md_path = out_dir / f"{run_id}.md"

    md: List[str] = [
        f"# Regime mode — sense `{sense_label}`",
        "",
        f"- run: `{run_id}` · N={args.n} · seed={args.seed} · exam={args.neuropil}",
        f"- pick: **`{sensed['pick']}`**",
        "",
        "## Layman",
        "",
        "Read the graph-shape stats (vs a plain ER graph), then weight regime modes. "
        "The neuropil name only chooses which exam tape we loaded.",
        "",
        "## Regime vector r",
        "",
        "| axis | value |",
        "|------|-------|",
    ]
    for k in REGIME_KEYS:
        md.append(f"| `{k}` | {sensed['r'][k]:.4f} |")
    abl = sensed.get("permute_ablation") or {}
    md += ["", "## Local-axis honesty (permute ablation)", ""]
    if abl:
        md.append(
            f"- extract_order_local={abl.get('extract_order_local_frac', 0):.4f} · "
            f"permuted_mean={abl.get('permuted_local_mean', 0):.4f} · "
            f"Δ={abl.get('local_minus_permuted', 0):.4f}"
        )
        if abl.get("local_likely_extract_artifact"):
            md.append(
                "- **warn:** local ≈ permuted — treat r_local as extract-order artifact, "
                "not anatomy (r_local shrunk for mixer)."
            )
        else:
            md.append("- local exceeds permute baseline — still extract-order metric, not soma geometry.")
    md += [
        "",
        "## Family mix",
        "",
        "| family | weight |",
        "|--------|--------|",
    ]
    for k, v in sorted(sensed["weights"].items(), key=lambda kv: -kv[1]):
        mark = " ← pick" if k == sensed["pick"] else ""
        md.append(f"| `{k}` | {v:.4f}{mark} |")

    if stress:
        md += [
            "",
            "## Dynamics A/B (Profile D hard, this seed)",
            "",
            f"| arm | family | task dsc | task fly | scoreboard D/F |",
            f"|-----|--------|----------|----------|----------------|",
        ]
        for name, brief in (("pick", stress["pick"]), ("control", stress["control"])):
            sb = brief["scoreboard"]
            md.append(
                f"| {name} | `{brief['family']}` | {brief['dsc_task']:.6g} | "
                f"{brief['fly_task']:.6g} | {sb['dsc_wins']}/{sb['fly_adj_wins']} |"
            )

    md += [
        "",
        "## Next",
        "",
        "Wire pick into multi-seed B017 ME_R cell; keep GNG sanity. "
        "Still no neuropil if-branches in dsc/.",
    ]
    md_path.write_text(chr(10).join(md) + chr(10))
    report["json_path"] = str(json_path)
    report["md_path"] = str(md_path)
    json_path.write_text(json.dumps(report, indent=2) + chr(10))

    print(json.dumps({
        "run_id": run_id,
        "sense": sense_label,
        "r": sensed["r"],
        "weights": sensed["weights"],
        "pick": sensed["pick"],
        "stress": stress,
        "md": md_path.name,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
