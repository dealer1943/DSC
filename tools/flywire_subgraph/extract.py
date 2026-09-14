"""Extract an N-node FlyWire subgraph (neuropil-filtered, degree-seeded)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


def extract_subgraph(
    feather: Path,
    n: int = 128,
    neuropil: str | None = "GNG",
    seed: int = 42,
    max_edges_scan: int = 2_000_000,
) -> dict[str, Any]:
    import pyarrow.feather as feather_api
    import pyarrow.compute as pc

    rng = np.random.default_rng(seed)
    cols = ["pre_pt_root_id", "post_pt_root_id", "syn_count"]
    table = feather_api.read_table(feather, columns=cols + ["neuropil"])
    if neuropil:
        mask = pc.equal(table["neuropil"], neuropil)
        table = table.filter(mask)
    if table.num_rows > max_edges_scan:
        # deterministic sample of rows for tractability
        idx = rng.choice(table.num_rows, size=max_edges_scan, replace=False)
        idx.sort()
        table = table.take(idx)

    pre = table["pre_pt_root_id"].to_numpy()
    post = table["post_pt_root_id"].to_numpy()
    syn = table["syn_count"].to_numpy() if "syn_count" in table.column_names else np.ones(len(pre))

    # degree proxy
    from collections import defaultdict

    deg: dict[int, float] = defaultdict(float)
    nbrs: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for a, b, w in zip(pre.tolist(), post.tolist(), syn.tolist()):
        a, b = int(a), int(b)
        if a == b:
            continue
        ww = float(w) if w is not None else 1.0
        deg[a] += ww
        deg[b] += ww * 0.5
        nbrs[a].append((b, ww))

    if not deg:
        raise RuntimeError("no edges after filter")

    # seed = top degree nodes, grow to N by weighted BFS
    ranked = sorted(deg.keys(), key=lambda k: deg[k], reverse=True)
    seeds = ranked[: max(8, n // 8)]
    chosen: list[int] = []
    seen: set[int] = set()
    frontier = list(seeds)
    rng.shuffle(frontier)
    while frontier and len(chosen) < n:
        u = frontier.pop()
        if u in seen:
            continue
        seen.add(u)
        chosen.append(u)
        # expand strongest neighbors first
        outs = sorted(nbrs.get(u, []), key=lambda t: -t[1])
        for v, _w in outs[:32]:
            if v not in seen:
                frontier.append(v)
        if len(frontier) > 10_000:
            frontier = frontier[:5000]

    if len(chosen) < n:
        for k in ranked:
            if k not in seen:
                chosen.append(k)
                seen.add(k)
            if len(chosen) >= n:
                break
    chosen = chosen[:n]
    id_map = {nid: i for i, nid in enumerate(chosen)}
    adj = np.zeros((n, n), dtype=np.uint8)
    edges = 0
    for a, b, w in zip(pre.tolist(), post.tolist(), syn.tolist()):
        ia, ib = id_map.get(int(a)), id_map.get(int(b))
        if ia is None or ib is None or ia == ib:
            continue
        if adj[ia, ib] == 0:
            adj[ia, ib] = 1
            edges += 1
    dens = float(edges) / max(1, n * (n - 1))
    meta = {
        "family": "flywire_subgraph",
        "n": n,
        "n_edges": edges,
        "density": dens,
        "neuropil": neuropil or "all_sampled",
        "seed": seed,
        "source": "proofread_connections_783",
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return {"adj": adj, "meta": meta, "root_ids": chosen}


def save_subgraph(bundle: dict[str, Any], out: Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, adj=bundle["adj"], root_ids=np.asarray(bundle["root_ids"], dtype=np.int64))
    meta_path = out.with_suffix(".json")
    meta_path.write_text(json.dumps(bundle["meta"], indent=2) + "\n")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Extract FlyWire subgraph for Profile D")
    ap.add_argument("--feather", type=Path, default=Path("MODELS/fly/flywire_v783/proofread_connections_783.feather"))
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--neuropil", type=str, default="GNG")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    out = args.out or Path(f"MODELS/fly/subgraphs/n{args.n}_{args.neuropil}_s{args.seed}.npz")
    bundle = extract_subgraph(args.feather, n=args.n, neuropil=args.neuropil, seed=args.seed)
    path = save_subgraph(bundle, out)
    print(json.dumps({"out": path.name, **bundle["meta"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
