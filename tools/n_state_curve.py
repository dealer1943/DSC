"""B018 — n-state curve: discrete state-table cardinality K ∈ {10,50,100}.

Assay: collect a fingerprint trajectory after warm/evolve,
quantize to K regimes (equal-mass on 1st PC), score empirical next-state
tables on a held-out suffix. One trajectory per (seed, arm); rebin per K.

ME_R is exam tape only — no neuropil hardcodes in generators.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from dsc import defaults
from dsc.substrate import generate_substrate
from tools.flywire_stress import _build_on_adj, _eval_runtime
from tools.flywire_subgraph.extract import extract_subgraph


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _fingerprint(rt, tick_out: dict) -> np.ndarray:
    """Compact stable fingerprint for regime quantization."""
    mix = rt.pop.mixture()  # (N, T)
    type_mean = mix.mean(axis=0)  # (T,)
    err = float(tick_out.get("err", rt.harness.last_err))
    y_hat = float(tick_out.get("y_hat", rt.harness.last_y_hat))
    util = float(tick_out.get("utility_mean", float(rt.pop.utility.mean())))
    act = float(tick_out.get("activity_mean", float(rt.pop.activity.mean())))
    stem = float(tick_out.get("stem_frac", 0.0))
    diff = float(tick_out.get("diff_mean", float(rt.pop.differentiation.mean())))
    return np.concatenate(
        [np.array([y_hat, err, util, act, stem, diff], dtype=np.float64), type_mean.astype(np.float64)]
    )


def _collect_trajectory(rt, warm: int, evolve: int, collect: int, seed: int) -> tuple[np.ndarray, float]:
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

    feats: list[np.ndarray] = []
    errs: list[float] = []
    for _ in range(collect):
        out = rt.tick(1)
        feats.append(_fingerprint(rt, out))
        errs.append(float(out.get("err", rt.harness.last_err)))
    # match Profile D: task_error on second half of collect window
    task_error = float(np.mean(errs[len(errs) // 2 :])) if errs else 1.0
    return np.stack(feats, axis=0), task_error


def _zscore_fit(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd < 1e-9, 1.0, sd)
    return mu, sd


def _pc1_scores(X: np.ndarray, mu: np.ndarray, sd: np.ndarray, eigvec: np.ndarray | None = None):
    Z = (X - mu) / sd
    if eigvec is None:
        # covariance eig: first principal direction
        C = np.cov(Z, rowvar=False)
        w, V = np.linalg.eigh(C)
        eigvec = V[:, -1]  # largest eigenvalue
    scores = Z @ eigvec
    return scores, eigvec


def _quantile_edges(train_scores: np.ndarray, k: int) -> np.ndarray:
    qs = np.linspace(0.0, 1.0, k + 1)
    edges = np.quantile(train_scores, qs)
    # ensure strictly increasing edges for digitize
    for i in range(1, len(edges)):
        if edges[i] <= edges[i - 1]:
            edges[i] = edges[i - 1] + 1e-9
    return edges


def _assign(scores: np.ndarray, edges: np.ndarray) -> np.ndarray:
    # bins 0..K-1
    return np.clip(np.digitize(scores, edges[1:-1], right=False), 0, len(edges) - 2)



def _outgoing_probs(states: np.ndarray, k: int) -> np.ndarray:
    counts = np.ones((k, k), dtype=np.float64)  # Laplace
    for a, b in zip(states[:-1], states[1:]):
        counts[int(a), int(b)] += 1.0
    return counts / counts.sum(axis=1, keepdims=True)


def consolidate_states(
    states: np.ndarray,
    k: int,
    l1_merge: float = 0.25,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Merge source states whose outgoing rows are near-duplicates.

    If many table entries go the same place with the same shape, collapse to
    one row and average the probabilities. Footprint = kept rows (and massy edges).
    """
    if k <= 1 or len(states) < 4:
        return states.copy(), {
            "k_raw": k, "k_eff": k, "merged_groups": 0,
            "footprint_rows": k, "footprint_edges": k, "l1_merge": l1_merge,
        }
    probs = _outgoing_probs(states, k)
    # Union-find merge when L1(P_i, P_j) < l1_merge AND same modal next
    parent = list(range(k))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    modal = probs.argmax(axis=1)
    for i in range(k):
        for j in range(i + 1, k):
            if modal[i] != modal[j]:
                continue
            if float(np.abs(probs[i] - probs[j]).sum()) <= l1_merge:
                union(i, j)

    roots = [find(i) for i in range(k)]
    uniq = sorted(set(roots))
    remap = {r: idx for idx, r in enumerate(uniq)}
    k_eff = len(uniq)
    new_states = np.array([remap[find(int(s))] for s in states], dtype=np.int64)

    # averaged rows among merged members
    massy = 0
    probs_eff = _outgoing_probs(new_states, k_eff)
    massy = int((probs_eff > (1.0 / max(k_eff, 1) + 0.02)).sum())
    merged_groups = sum(1 for r in uniq if roots.count(r) > 1)
    return new_states, {
        "k_raw": int(k),
        "k_eff": int(k_eff),
        "merged_groups": int(merged_groups),
        "footprint_rows": int(k_eff),
        "footprint_edges": massy,
        "l1_merge": float(l1_merge),
        "compression": float(k_eff / max(k, 1)),
    }


def _transition_metrics(states: np.ndarray, k: int, train_frac: float = 0.7) -> dict[str, Any]:
    n = len(states)
    split = max(2, int(n * train_frac))
    train, test = states[:split], states[split:]
    counts = np.ones((k, k), dtype=np.float64)  # Laplace
    for a, b in zip(train[:-1], train[1:]):
        counts[int(a), int(b)] += 1.0
    probs = counts / counts.sum(axis=1, keepdims=True)
    pred = probs.argmax(axis=1)

    hits = 0
    nll = 0.0
    pairs = 0
    for a, b in zip(test[:-1], test[1:]):
        a_i, b_i = int(a), int(b)
        hits += int(pred[a_i] == b_i)
        nll += -float(np.log(max(probs[a_i, b_i], 1e-12)))
        pairs += 1
    occupied = int(np.unique(states).size)
    return {
        "next_state_hit": float(hits / max(pairs, 1)),
        "mean_surprisal": float(nll / max(pairs, 1)),
        "occupied_states": occupied,
        "occupied_frac": float(occupied / k),
        "train_n": int(len(train)),
        "test_n": int(len(test)),
        "test_pairs": int(pairs),
        "k": int(k),
    }


def _score_ks(
    feats: np.ndarray,
    ks: list[int],
    train_frac: float = 0.7,
    consolidate: bool = True,
    l1_merge: float = 0.25,
) -> list[dict[str, Any]]:
    n = len(feats)
    split = max(10, int(n * train_frac))
    train_X = feats[:split]
    mu, sd = _zscore_fit(train_X)
    train_scores, eigvec = _pc1_scores(train_X, mu, sd)
    all_scores, _ = _pc1_scores(feats, mu, sd, eigvec=eigvec)
    rows = []
    for k in ks:
        edges = _quantile_edges(train_scores, k)
        states = _assign(all_scores, edges)
        m = _transition_metrics(states, k, train_frac=train_frac)
        m["consolidated"] = False
        rows.append(m)
        if consolidate and k >= 10:
            c_states, c_meta = consolidate_states(states, k, l1_merge=l1_merge)
            cm = _transition_metrics(c_states, int(c_meta["k_eff"]), train_frac=train_frac)
            cm["consolidated"] = True
            cm["k_raw"] = k
            cm.update(c_meta)
            # keep k key as raw for grouping; expose k_eff separately
            cm["k"] = k
            rows.append(cm)
    return rows


def _load_fly_bundle(n: int, neuropil: str, seed: int, feather: Path | None) -> dict:
    """Prefer cached Profile D subgraph; else extract from proofread feather."""
    cache = Path(f"MODELS/fly/subgraphs/n{n}_{neuropil}_s{seed}.npz")
    if cache.is_file():
        data = np.load(cache, allow_pickle=True)
        adj = data["adj"].astype(np.uint8)
        meta_path = cache.with_suffix(".json")
        meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {
            "n": n, "neuropil": neuropil, "seed": seed, "n_edges": int(adj.sum()),
            "source": "flywire_cached",
        }
        return {"adj": adj, "meta": meta}
    from tools.flywire_subgraph.extract import extract_subgraph as _ex
    feather = feather or Path("MODELS/fly/flywire_v783/proofread_connections_783.feather")
    return _ex(feather, n=n, neuropil=neuropil, seed=seed)


def _build_pair(
    n: int,
    neuropil: str,
    seed: int,
    dsc_family: str,
    feather: Path | None,
) -> tuple[Any, Any, dict]:
    bundle = _load_fly_bundle(n, neuropil, seed, feather)
    fly_edges = int(bundle["adj"].sum())
    dsc_sub = generate_substrate(
        n=n,
        seed=seed,
        family=dsc_family,
        target_edges=fly_edges,
    )
    rt_dsc = _build_on_adj(dsc_sub.adj, dsc_sub.meta, seed=seed)
    rt_fly = _build_on_adj(bundle["adj"], bundle["meta"], seed=seed)
    meta = {
        "n": n,
        "neuropil": neuropil,
        "seed": seed,
        "dsc_family": dsc_sub.meta.get("family", dsc_family),
        "fly_edges": fly_edges,
        "dsc_edges": int(dsc_sub.adj.sum()),
    }
    return rt_dsc, rt_fly, meta


def run_curve(
    n: int = 512,
    neuropil: str = "ME_R",
    seeds: list[int] | None = None,
    ks: list[int] | None = None,
    warm: int = 64,
    evolve: int = 2,
    collect: int = 800,
    dsc_family: str = "sheet_hub",
    out_dir: Path | None = None,
    feather: Path | None = None,
) -> dict[str, Any]:
    seeds = seeds or [17, 22, 46]
    ks = ks or [10, 50, 100]
    # ensure enough ticks for K=100
    collect = max(collect, 8 * max(ks))
    out_dir = Path(out_dir or "BENCHMARKS/runs")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in seeds:
        print(f"[B018] seed={seed} building ME_R pair…", flush=True)
        rt_dsc, rt_fly, meta = _build_pair(n, neuropil, seed, dsc_family, feather)
        for arm, rt in (("dsc", rt_dsc), ("fly_adj", rt_fly)):
            print(f"[B018] seed={seed} arm={arm} warm={warm} evolve={evolve} collect={collect}", flush=True)
            feats, task_error = _collect_trajectory(rt, warm, evolve, collect, seed=seed)
            for m in _score_ks(feats, ks):
                row = {
                    **meta,
                    "arm": arm,
                    "warm": warm,
                    "evolve": evolve,
                    "collect": collect,
                    "task_error": task_error,
                    **m,
                }
                rows.append(row)
                tag = "consol" if m.get("consolidated") else "raw"
                ke = m.get("k_eff", m["k"])
                print(
                    f"  K={m['k']:3d} {tag:6s} hit={m['next_state_hit']:.3f} "
                    f"surprisal={m['mean_surprisal']:.3f} occ={m['occupied_frac']:.2f} "
                    f"k_eff={ke} task_err={task_error:.5f}",
                    flush=True,
                )

    # aggregates (raw vs consolidated)
    agg: dict[str, Any] = {}
    for arm in ("dsc", "fly_adj"):
        agg[arm] = {}
        for k in ks:
            for flag, tag in ((False, "raw"), (True, "consolidated")):
                sub = [r for r in rows if r["arm"] == arm and r["k"] == k and bool(r.get("consolidated")) == flag]
                if not sub:
                    continue
                def _stat(key: str, sub=sub) -> dict[str, float]:
                    vals = np.array([float(r[key]) for r in sub if key in r], dtype=np.float64)
                    return {
                        "mean": float(vals.mean()) if len(vals) else float("nan"),
                        "std": float(vals.std(ddof=0)) if len(vals) else float("nan"),
                        "n": int(len(vals)),
                    }
                block = {
                    "next_state_hit": _stat("next_state_hit"),
                    "mean_surprisal": _stat("mean_surprisal"),
                    "occupied_frac": _stat("occupied_frac"),
                    "task_error": _stat("task_error"),
                }
                if flag:
                    block["k_eff"] = _stat("k_eff")
                    block["compression"] = _stat("compression")
                    block["footprint_rows"] = _stat("footprint_rows")
                agg[arm].setdefault(str(k), {})[tag] = block

    stamp = _utc_stamp()
    report = {
        "protocol": "B018_n_state_curve_v0",
        "run_id": f"B018_{stamp}_n{n}_{neuropil}",
        "n": n,
        "neuropil": neuropil,
        "dsc_family": dsc_family,
        "seeds": seeds,
        "ks": ks,
        "warm": warm,
        "evolve": evolve,
        "collect": collect,
        "wall_s": round(time.perf_counter() - t0, 2),
        "rows": rows,
        "aggregate": agg,
        "note": (
            "One trajectory per (seed,arm); rebin at each K. "
            "Quantizer: z-score → PC1 → equal-mass quantile bins on train 70%. "
            "Laplace-smoothed transition table; hit = argmax next vs held-out."
        ),
    }
    json_path = out_dir / f"{report['run_id']}.json"
    md_path = out_dir / f"{report['run_id']}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(_md_summary(report), encoding="utf-8")
    report["json_path"] = str(json_path)
    report["md_path"] = str(md_path)
    print(f"[B018] wrote {json_path}", flush=True)
    return report


def _md_summary(report: dict) -> str:
    lines = [
        f"# {report['run_id']}",
        "",
        f"- protocol: `{report['protocol']}`",
        f"- N={report['n']} neuropil=`{report['neuropil']}` family=`{report['dsc_family']}`",
        f"- seeds={report['seeds']} ks={report['ks']}",
        f"- warm={report['warm']} evolve={report['evolve']} collect={report['collect']}",
        f"- wall_s={report['wall_s']}",
        "",
        "## Aggregate (mean ± std)",
        "",
        "| arm | K | version | next_state_hit | surprisal | occupied_frac | k_eff | compression | task_error |",
        "|-----|---:|---------|---------------:|----------:|--------------:|------:|------------:|-----------:|",
    ]
    for arm in ("dsc", "fly_adj"):
        for k in report["ks"]:
            for tag in ("raw", "consolidated"):
                a = report["aggregate"].get(arm, {}).get(str(k), {}).get(tag)
                if not a:
                    continue
                ke = a.get("k_eff", {}).get("mean", k)
                comp = a.get("compression", {}).get("mean", 1.0)
                lines.append(
                    "| {arm} | {k} | {tag} | {h:.3f}±{hs:.3f} | {s:.3f}±{ss:.3f} | {o:.2f}±{os:.2f} | {ke:.1f} | {c:.2f} | {t:.5f}±{ts:.5f} |".format(
                        arm=arm,
                        k=k,
                        tag=tag,
                        h=a["next_state_hit"]["mean"],
                        hs=a["next_state_hit"]["std"],
                        s=a["mean_surprisal"]["mean"],
                        ss=a["mean_surprisal"]["std"],
                        o=a["occupied_frac"]["mean"],
                        os=a["occupied_frac"]["std"],
                        ke=ke,
                        c=comp,
                        t=a["task_error"]["mean"],
                        ts=a["task_error"]["std"],
                    )
                )
    lines.extend(["", f"_note:_ {report['note']}", ""])
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="B018 n-state curve assay")
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--neuropil", type=str, default="ME_R")
    ap.add_argument("--dsc-family", type=str, default="sheet_hub")
    ap.add_argument("--seeds", type=str, default="17,22,46")
    ap.add_argument("--ks", type=str, default="10,50,100")
    ap.add_argument("--warm", type=int, default=64)
    ap.add_argument("--evolve", type=int, default=2)
    ap.add_argument("--collect", type=int, default=800)
    ap.add_argument("--out-dir", type=str, default="BENCHMARKS/runs")
    ap.add_argument("--feather", type=str, default="")
    args = ap.parse_args()
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    ks = [int(x) for x in args.ks.split(",") if x.strip()]
    feather = Path(args.feather) if args.feather else None
    run_curve(
        n=args.n,
        neuropil=args.neuropil,
        seeds=seeds,
        ks=ks,
        warm=args.warm,
        evolve=args.evolve,
        collect=args.collect,
        dsc_family=args.dsc_family,
        out_dir=Path(args.out_dir),
        feather=feather,
    )


if __name__ == "__main__":
    main()
