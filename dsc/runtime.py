"""DSC runtime — build, tick, signal snapshots for the operator console."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from dsc import defaults
from dsc.cells import Population, init_population, step_population
from dsc.harness import TemporalHarness, build_harness
from dsc.persist import load_active, save_active, save_model_bundle, sanitize_model_name
from dsc.progress import ProgressCb, emit
from dsc.substrate import Substrate, assert_invariants, generate_substrate
from dsc.utility import update_utilities
from dsc.differentiation import update_differentiation
from dsc.evolve import PopSnapshot, run_cycles

DEFAULT_ACTIVE = Path(__file__).resolve().parents[1] / "MODEL" / "active"


@dataclass
class DscRuntime:
    sub: Substrate
    pop: Population
    harness: TemporalHarness
    manifest: Dict[str, Any] = field(default_factory=dict)
    signal_hist: Dict[str, List[float]] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    last_good: Optional[PopSnapshot] = None
    evolve_count: int = 0

    def _push(self, name: str, value: float, maxlen: int = 64) -> None:
        h = self.signal_hist.setdefault(name, [])
        h.append(float(value))
        if len(h) > maxlen:
            self.signal_hist[name] = h[-maxlen:]

    def log(self, msg: str) -> None:
        self.events.append(msg)
        if len(self.events) > 400:
            self.events = self.events[-400:]

    @property
    def revision(self) -> str:
        return str(self.manifest.get("revision", "dsc"))

    def tick(self, n: int = 1) -> Dict[str, Any]:
        last = {}
        for _ in range(max(1, n)):
            x, y = self.harness.next_input_target()
            y_hat = step_population(self.pop, self.sub, x)
            err = self.harness.score(y_hat, y)
            reward = -err
            prev_u = self.pop.utility.copy()
            last = update_utilities(self.pop, reward)
            dstat = update_differentiation(self.pop, prev_u)
            last.update(dstat)
            last.update({"err": err, "y": y, "y_hat": y_hat, "t": self.harness.t})
            self._push("err", err)
            self._push("y_hat", y_hat)
            self._push("utility_mean", last["utility_mean"])
            self._push("activity_mean", float(self.pop.activity.mean()))
            self._push("coverage_mean", last["coverage_mean"])
            self._push("novelty_mean", last["novelty_mean"])
            self._push("diff_mean", last["diff_mean"])
            self._push("stem_frac", last["stem_frac"])
        self.log(f"tick t={self.harness.t} err={last.get('err', 0):.4f} util={last.get('utility_mean', 0):.4f}")
        return last

    def status(self) -> Dict[str, Any]:
        mix = self.pop.mixture()
        stem_frac = float((self.pop.differentiation < defaults.DIFF_STEM_LABEL).mean())
        return {
            "mode": "DSC",
            "pack": "active",
            "revision": self.revision,
            "n_nodes": self.sub.n,
            "n_edges": self.sub.n_edges,
            "density": round(self.sub.density, 4),
            "t": self.harness.t,
            "err": round(self.harness.last_err, 5),
            "utility_mean": round(float(self.pop.utility.mean()), 5),
            "stem_frac": round(stem_frac, 3),
            "activity_mean": round(float(self.pop.activity.mean()), 5),
            "task": defaults.TASK_NAME,
        }

    def canvas_nodes(self, limit=None, order: str = "id"):
        """
        order='id' → stable 0..N-1 (F015 grid).
        order='activity' → top-K by activity (legacy bars / FlyWire-style).
        limit=None → all cells when order='id'.
        """
        labels = self.pop.type_labels()
        act = self.pop.activity
        util = self.pop.utility
        amax = float(act.max()) + 1e-6
        n = self.pop.n
        if order == "activity":
            lim = 48 if limit is None else limit
            idxs = list(np.argsort(-act)[:lim])
        else:
            idxs = list(range(n if limit is None else min(n, limit)))
        nodes = []
        for i in idxs:
            nodes.append(
                {
                    "id": str(int(i)),
                    "label": f"c{int(i):03d}",
                    "kind": labels[int(i)],
                    "activity": float(act[i] / amax),
                    "utility": float(util[i]),
                }
            )
        return nodes

    def canvas_edges(self, node_ids, limit: int = 120):
        ids = [int(i) for i in node_ids]
        idset = set(ids)
        edges = []
        adj = self.sub.adj
        for i in ids:
            for j in np.flatnonzero(adj[i]):
                if int(j) in idset:
                    edges.append(
                        {
                            "src": str(i),
                            "dst": str(int(j)),
                            "weight": 1.0,
                            "meta": "syn",
                        }
                    )
                    if len(edges) >= limit:
                        return edges
        return edges



    def snapshot_good(self, note: str = "") -> PopSnapshot:
        snap = PopSnapshot.capture(
            self.pop, self.harness, signal_hist=self.signal_hist, note=note
        )
        self.last_good = snap
        return snap

    def evolve(self, n: int = 1, seed=None):
        """F006 cycles with F009 light auto-rollback; refreshes last_good on success."""
        n = int(n) if n is not None else defaults.EVOLVE_DEFAULT_CYCLES
        # batch-level last-good before any cycle
        self.snapshot_good(note=f"pre-evolve/{n}")
        # last_good stays as pre-batch anchor so /rollback undoes this /evolve
        reports = run_cycles(self.pop, self.harness, n, seed=seed)
        lines = []
        ok_cycles = 0
        for i, rep in enumerate(reports, 1):
            lines.extend(rep.lines(i))
            if not rep.rolled_back:
                ok_cycles += 1
                self.evolve_count += 1
            self._push("utility_mean", rep.util_after if not rep.rolled_back else rep.util_before)
            self._push("diff_mean", float(self.pop.differentiation.mean()))
            self._push("stem_frac", float((self.pop.differentiation < defaults.DIFF_STEM_LABEL).mean()))
        lines.append(
            f"evolve done · applied={ok_cycles}/{len(reports)} · "
            f"diff_mean={float(self.pop.differentiation.mean()):.3f} · "
            f"stem_frac={float((self.pop.differentiation < defaults.DIFF_STEM_LABEL).mean()):.3f}"
        )
        for ln in lines:
            self.log(ln)
        return {"reports": reports, "lines": lines, "applied": ok_cycles}

    def rollback(self) -> list:
        """Restore last-good snapshot (F009)."""
        if self.last_good is None:
            return ["refuse: no last-good snapshot — run /evolve first"]
        self.last_good.restore(self.pop, self.harness)
        if self.last_good.signal_hist:
            self.signal_hist = {k: list(v) for k, v in self.last_good.signal_hist.items()}
        msg = f"rollback ok · restored ({self.last_good.note or 'last-good'})"
        self.log(msg)
        return [msg]

    def save_named(self, name=None, progress=None) -> Path:
        """Persist session to MODEL/saves/*.model and refresh active tip."""
        root = Path(__file__).resolve().parents[1]
        saves = root / "MODEL" / "saves"
        active = root / "MODEL" / "active"
        path = save_model_bundle(
            saves,
            self.sub,
            self.pop,
            self.harness,
            name=name,
            progress=progress,
            also_active=active,
        )
        self.manifest = json_load_manifest(active)
        self.log(f"saved {path.name}")
        return path

    def save(self, root: Optional[Path] = None, progress: Optional[ProgressCb] = None) -> None:
        root = Path(root) if root else DEFAULT_ACTIVE
        save_active(root, self.sub, self.pop, self.harness, progress=progress)
        self.manifest = json_load_manifest(root)


def json_load_manifest(root: Path) -> Dict[str, Any]:
    import json
    return json.loads((Path(root) / "manifest.json").read_text())


def build_mvp(
    progress: Optional[ProgressCb] = None,
    save: bool = True,
    active_dir: Optional[Path] = None,
) -> DscRuntime:
    """Construct F001→F002→F003→F010→F005 stack and optionally persist."""
    active_dir = Path(active_dir) if active_dir else DEFAULT_ACTIVE

    def p(frac: float, msg: str) -> None:
        # map substages into global 0..1
        emit(progress, frac, msg)

    p(0.02, "DSC: starting MVP build")
    sub = generate_substrate(progress=lambda f, m: p(0.02 + 0.25 * f, m))
    assert_invariants(sub)
    pop = init_population(sub, progress=lambda f, m: p(0.30 + 0.25 * f, m))
    harness = build_harness(progress=lambda f, m: p(0.58 + 0.12 * f, m))
    rt = DscRuntime(sub=sub, pop=pop, harness=harness, manifest={})
    # warm a few ticks so activity/utilities nonzero for UI
    p(0.72, "DSC: warming ticks")
    for i in range(16):
        rt.tick(1)
        p(0.72 + 0.15 * (i + 1) / 16, f"DSC: warm tick {i+1}/16")
    if save:
        rt.save(active_dir, progress=lambda f, m: p(0.88 + 0.12 * f, m))
        rt.manifest = json_load_manifest(active_dir)
    else:
        rt.manifest = {
            "revision": f"r{defaults.SCHEMA_VERSION}-n{sub.n}-e{sub.n_edges}",
            "display_name": "active",
        }
    p(1.0, f"DSC: ready · {rt.revision}")
    rt.log(f"MVP built · {rt.revision} · density={sub.density:.4f}")
    return rt


def load_mvp(
    active_dir: Optional[Path] = None,
    progress: Optional[ProgressCb] = None,
) -> DscRuntime:
    active_dir = Path(active_dir) if active_dir else DEFAULT_ACTIVE
    sub, pop, harness, man = load_active(active_dir, progress=progress)
    rt = DscRuntime(sub=sub, pop=pop, harness=harness, manifest=man)
    rt.log(f"DSC loaded · {rt.revision}")
    return rt
