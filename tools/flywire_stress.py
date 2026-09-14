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
    bilayer: bool = False,
    talk_board: bool = False,
    nearest_exact: bool = False,
    regime_mode: bool = False,
    regime_gather: bool = False,
    regime_substrate: bool = False,
    hub_governor: bool = False,
    edge_frac: float = 1.0,
    state_table_k: int = 0,
    state_table_mix: float = 0.25,
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
    edge_frac = float(edge_frac)
    if edge_frac <= 0 or edge_frac > 1.5:
        raise ValueError(f"edge_frac must be in (0, 1.5], got {edge_frac}")
    dsc_edge_target = max(n, int(round(fly_edges * edge_frac)))
    regime_info = None
    dsc_family_requested = dsc_family
    sheet_genes = None
    hub_gov_report = None
    # F031 hub-governor implies substrate genes path (sheet_hub)
    use_hub_gov = bool(hub_governor)
    use_substrate = bool(regime_substrate or use_hub_gov)
    # Peer risk: --hub-governor alone must not silently remap GNG → sheet_hub
    if use_hub_gov:
        req = str(dsc_family).replace("_directed", "").strip().lower()
        optic_ok = str(neuropil).upper() in {"ME_R", "ME_L", "LO_R", "LO_L", "LOP_R", "LOP_L", "OPTIC"}
        explicit_sheet = req in {"sheet_hub", "hybrid", "sheet_pa"}
        if not (optic_ok or explicit_sheet):
            raise ValueError(
                "F031 --hub-governor refuses silent non-optic remap: "
                f"neuropil={neuropil!r} dsc_family_requested={dsc_family!r}. "
                "Use an optic venue (ME_*/LO_*) or pass --dsc-family sheet_hub explicitly."
            )
    apply_regime_sense = bool(regime_mode or regime_gather or use_substrate)
    if apply_regime_sense:
        from tools.regime_mode import sense_adj
        sensed = sense_adj(bundle["adj"].astype(np.uint8), baseline_seed=seed)
        if regime_mode:
            dsc_family = sensed["pick"]
        if use_substrate:
            # genes only apply to sheet_hub family — force that family (record request)
            dsc_family = "sheet_hub"
            sheet_genes = sensed.get("substrate_genes")
        # slim copy for ledger (avoid huge baseline dumps)
        regime_info = {
            "pick": sensed["pick"],
            "r": sensed["r"],
            "weights": sensed["weights"],
            "gather_knobs": sensed.get("gather_knobs") if (regime_gather or regime_mode) else None,
            "substrate_genes": sheet_genes,
            "permute_ablation": {
                k: sensed.get("permute_ablation", {}).get(k)
                for k in (
                    "extract_order_local_frac",
                    "permuted_local_mean",
                    "local_minus_permuted",
                    "local_likely_extract_artifact",
                    "note",
                )
            },
            "local_axis": "extract_order_local_frac",
            "dsc_family_requested": dsc_family_requested,
            "family_overridden": bool(regime_mode or use_substrate),
            "gather_applied": bool(regime_gather or regime_mode),
            "substrate_applied": bool(use_substrate),
            "hub_governor": bool(use_hub_gov),
            "degenerate_vs_requested": (
                str(sensed["pick"]).replace("_directed", "")
                == str(dsc_family_requested).replace("_directed", "")
            ),
        }
    # DSC side: chosen family; match fly edge budget when not pure ER-p
    if use_hub_gov and regime_info is not None:
        from tools.regime_mode import generate_sheet_hub_governed
        gov = generate_sheet_hub_governed(
            n=n,
            target_edges=dsc_edge_target,
            seed=seed,
            r=regime_info["r"],
            genes=sheet_genes,
        )
        dsc_sub = gov["substrate"]
        sheet_genes = gov.get("genes_final") or sheet_genes
        hub_gov_report = {k: gov[k] for k in gov if k != "substrate"}
        if regime_info is not None:
            regime_info["substrate_genes"] = sheet_genes
            regime_info["hub_governor_report"] = hub_gov_report
    else:
        dsc_sub = generate_substrate(
            n=n,
            seed=seed,
            family=dsc_family,
            target_edges=dsc_edge_target,
            sheet_genes=sheet_genes,
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
        if bilayer:
            _override("BILAYER", True)
        if talk_board:
            _override("TALK_BOARD", True)
        if nearest_exact:
            _override("NEAREST_EXACT", True)

        if int(state_table_k) > 0:
            _override("STATE_TABLE_K", int(state_table_k))
            _override("STATE_TABLE_MIX", float(state_table_mix))
            # rebuild runtimes so dataclass picks up table
            rt_er = _build_on_adj(dsc_sub.adj, dsc_sub.meta, seed=seed)
            # fly exam tape: leave STATE_TABLE off unless explicitly set
        def _warm_evolve(rt):
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

        # Fly exam tape: CLI gather flags only (not regime knobs from r).
        _warm_evolve(rt_fly)
        fly_m = _eval_runtime(rt_fly, ticks=ticks, seed=seed + 1)

        # R005: gather knobs from r apply to DSC only (no adj blend; no neuropil if).
        # Substrate genes already baked into dsc_sub; gather is separate opt-in.
        if regime_info and regime_info.get("gather_applied") and regime_info.get("gather_knobs"):
            gk = regime_info["gather_knobs"]
            for name in ("HUB_AWARE", "HUB_OUT_EXP", "LOCAL_GATHER_MIX"):
                if name in gk:
                    _override(name, gk[name])
            if not bilayer and "BILAYER" in gk:
                _override("BILAYER", bool(gk["BILAYER"]))
                if "BILAYER_MIX" in gk:
                    _override("BILAYER_MIX", float(gk["BILAYER_MIX"]))
            if not talk_board and "TALK_BOARD" in gk:
                _override("TALK_BOARD", bool(gk["TALK_BOARD"]))
                if "TALK_MIX" in gk:
                    _override("TALK_MIX", float(gk["TALK_MIX"]))
            if not nearest_exact and gk.get("NEAREST_EXACT"):
                _override("NEAREST_EXACT", True)

        # F031: gather damp only if FINAL still overshoots (Peer: don't contaminate A/B)
        if (
            hub_gov_report
            and hub_gov_report.get("overshoot_final")
            and float(hub_gov_report.get("gather_hub_out_exp_nudge") or 0) > 0
        ):
            nudge = float(hub_gov_report["gather_hub_out_exp_nudge"])
            cur = float(getattr(defaults, "HUB_OUT_EXP", 0.5))
            _override("HUB_AWARE", True)
            _override("HUB_OUT_EXP", float(min(0.9, cur + nudge)))

        _warm_evolve(rt_er)
        dsc_m = _eval_runtime(rt_er, ticks=ticks, seed=seed + 1)
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
        "bilayer": bool(bilayer),
        "talk_board": bool(talk_board),
        "nearest_exact": bool(nearest_exact),
        "regime_mode": bool(regime_mode),
        "regime_gather": bool(regime_gather or regime_mode),
        "regime_substrate": bool(regime_substrate or hub_governor),
        "hub_governor": bool(hub_governor),
        "edge_frac": float(edge_frac),
        "dsc_edge_target": int(dsc_edge_target),
        "fly_edges": int(fly_edges),
        "dsc_edges": int(dsc_sub.adj.sum()),
        "state_table_k": int(state_table_k),
        "state_table_mix": float(state_table_mix) if int(state_table_k) > 0 else None,
        "state_table": (rt_er.state_table.report() if getattr(rt_er, "state_table", None) else None),
        "dsc_family_requested": dsc_family_requested,
        "family_forced_sheet_hub": bool(
            use_substrate
            and str(dsc_family_requested).replace("_directed", "").strip().lower()
            not in {"sheet_hub", "hybrid", "sheet_pa"}
        ),
        "regime_pick": (regime_info or {}).get("pick"),
        "gather_knobs": (regime_info or {}).get("gather_knobs"),
        "substrate_genes": sheet_genes or (dsc_sub.meta or {}).get("sheet_genes"),
        "hub_governor_report": hub_gov_report,
        "regime": regime_info,
        # True when final family matches requested (collapsed/unlabeled A/B).
        # family_forced_sheet_hub flags forced remap when requested≠sheet_hub.
        # Family-level A/B vacuous only when override active AND final == requested
        # for a *non-sheet* request. If user already asked sheet_hub/hybrid/sheet_pa,
        # same-family vs governor/genes is intentional gene-level A/B — not degenerate_ab.
        "degenerate_ab": (
            bool(regime_mode or use_substrate)
            and str((dsc_sub.meta or {}).get("family", dsc_family)).replace("_directed", "").strip().lower()
            == str(dsc_family_requested).replace("_directed", "").strip().lower()
            and str(dsc_family_requested).replace("_directed", "").strip().lower()
            not in {"sheet_hub", "hybrid", "sheet_pa"}
        ),
        "nearest_k": int(__import__("dsc.defaults", fromlist=["NEAREST_K"]).NEAREST_K) if nearest_exact else None,
        "nearest_rule": str(__import__("dsc.defaults", fromlist=["NEAREST_RULE"]).NEAREST_RULE) if nearest_exact else None,
        "nearest_note": (
            "replaces mean/hub gather; sheet rule is |i-j| index proxy (not anatomical nn); "
            "BILAYER/TALK still apply if those flags are on — leave them off for a pure nearest A/B"
            if nearest_exact else None
        ),
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
        f"- edge_frac: `{report.get('edge_frac')}` · dsc_edges: `{report.get('dsc_edges')}` / fly_edges: `{report.get('fly_edges')}`",
        f"- state_table_k: `{report.get('state_table_k')}` · state_table: `{report.get('state_table')}`",
        f"- hub_governor: `{report.get('hub_governor')}` · regime_substrate: `{report.get('regime_substrate')}` · family_forced_sheet_hub: `{report.get('family_forced_sheet_hub')}`",
        f"- substrate_genes: `{report.get('substrate_genes')}`",
        (
            f"- hub_gov: overshoot_final=`{(report.get('hub_governor_report') or {}).get('overshoot_final')}` "
            f"regenerated=`{(report.get('hub_governor_report') or {}).get('regenerated')}` "
            f"nudge=`{(report.get('hub_governor_report') or {}).get('gather_hub_out_exp_nudge')}`"
            if report.get("hub_governor") else "- hub_gov: off"
        ),
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
        "dsc_family_requested": report.get("dsc_family_requested"),
        "regime_mode": report.get("regime_mode"),
        "regime_gather": report.get("regime_gather"),
        "regime_substrate": report.get("regime_substrate"),
        "hub_governor": report.get("hub_governor"),
        "edge_frac": report.get("edge_frac"),
        "state_table_k": report.get("state_table_k"),
        "dsc_edges": report.get("dsc_edges"),
        "fly_edges": report.get("fly_edges"),
        "family_forced_sheet_hub": report.get("family_forced_sheet_hub"),
        "regime_pick": report.get("regime_pick"),
        "regime_r": (report.get("regime") or {}).get("r"),
        "gather_knobs": report.get("gather_knobs"),
        "substrate_genes": report.get("substrate_genes"),
        "hub_gov_overshoot_final": (report.get("hub_governor_report") or {}).get("overshoot_final"),
        "hub_gov_regenerated": (report.get("hub_governor_report") or {}).get("regenerated"),
        "hub_gov_nudge": (report.get("hub_governor_report") or {}).get("gather_hub_out_exp_nudge"),
        "degenerate_ab": report.get("degenerate_ab"),
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
    ap.add_argument("--easy-harness", action="store_true",
                    help="Use lag-1/noise=0.05 instead of Profile D hard default")
    ap.add_argument("--bilayer", action="store_true",
                    help="F029 folded-sheet elevated state channel")
    ap.add_argument("--talk-board", action="store_true",
                    help="F030 shared talk bitset + edge-masked glance")
    ap.add_argument("--nearest-exact", action="store_true",
                    help="R003 nearest-neighbor exact signal (no mean gather)")
    ap.add_argument("--regime-mode", action="store_true",
                    help="R005: override --dsc-family with regime pick from fly adj "
                         "(requested family still recorded; check degenerate_ab)")
    ap.add_argument("--regime-gather", action="store_true",
                    help="R005: keep --dsc-family; apply gather knobs from fly r "
                        "(HUB_OUT_EXP, LOCAL_GATHER_MIX, optional bilayer/talk)")
    ap.add_argument("--regime-substrate", action="store_true",
                    help="R005: force sheet_hub; set σ/α/β/p_recip genes from fly r "
                        "(no gather unless also --regime-gather)")
    ap.add_argument("--edge-frac", type=float, default=1.0,
                    help="DSC edge budget as fraction of matched fly edges (wire footprint)")
    ap.add_argument("--state-table-k", type=int, default=0,
                    help="F032: discrete state table size (0=off); DSC only")
    ap.add_argument("--state-table-mix", type=float, default=0.25,
                    help="F032: blend weight of table prior into y_hat")
    ap.add_argument("--hub-governor", action="store_true",
                    help="F031: hub formation governor (on-ramp+ceiling+one regenerate); "
                        "implies sheet_hub genes from r")
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
        task_lag=(1 if args.easy_harness else (args.task_lag if args.task_lag is not None else 2)),
        task_noise=(0.05 if args.easy_harness else (args.task_noise if args.task_noise is not None else 0.20)),
        bilayer=bool(args.bilayer),
        talk_board=bool(args.talk_board),
        nearest_exact=bool(args.nearest_exact),
        regime_mode=bool(args.regime_mode),
        regime_gather=bool(getattr(args, "regime_gather", False)),
        regime_substrate=bool(getattr(args, "regime_substrate", False)),
        hub_governor=bool(getattr(args, "hub_governor", False)),
    )
    _append_ledger(report, Path(args.out) / "stress_ledger.jsonl")
    print(json.dumps({
        "run_id": report["run_id"],
        "experiment": report.get("experiment"),
        "dsc_family": report.get("dsc_family"),
        "hub_aware": report.get("hub_aware"),
        "bilayer": report.get("bilayer"),
        "talk_board": report.get("talk_board"),
        "nearest_exact": report.get("nearest_exact"),
        "regime_mode": report.get("regime_mode"),
        "regime_gather": report.get("regime_gather"),
        "regime_substrate": report.get("regime_substrate"),
        "hub_governor": report.get("hub_governor"),
        "edge_frac": report.get("edge_frac"),
        "state_table_k": report.get("state_table_k"),
        "dsc_edges": report.get("dsc_edges"),
        "fly_edges": report.get("fly_edges"),
        "family_forced_sheet_hub": report.get("family_forced_sheet_hub"),
        "dsc_family_requested": report.get("dsc_family_requested"),
        "regime_pick": report.get("regime_pick"),
        "regime_r": (report.get("regime") or {}).get("r") if report.get("regime") else None,
        "gather_knobs": report.get("gather_knobs"),
        "substrate_genes": report.get("substrate_genes"),
        "hub_governor_overshoot": (report.get("hub_governor_report") or {}).get("overshoot_final"),
        "hub_governor_regenerated": (report.get("hub_governor_report") or {}).get("regenerated"),
        "degenerate_ab": report.get("degenerate_ab"),
        "nearest_rule": report.get("nearest_rule"),
        "nearest_note": report.get("nearest_note"),
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
