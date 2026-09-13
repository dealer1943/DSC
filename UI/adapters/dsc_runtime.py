"""DSC runtime adapter — loads MODEL/active via dsc package."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .base import EdgeView, NodeView, ViewModel

ADAPTER_NAME = "dsc"
IMPLEMENTED = True

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACTIVE = REPO_ROOT / "MODEL" / "active"

# import dsc from repo root
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dsc.runtime import build_mvp, load_mvp  # noqa: E402


def active_label(path: Path) -> str:
    return Path(path).name or "active"


class DscRuntimeAdapter:
    name = "dsc"

    def __init__(self, active_dir: Optional[Path] = None):
        self.active_dir = Path(active_dir) if active_dir else DEFAULT_ACTIVE
        self.revision = "unloaded"
        self._rt = None
        self._events: List[str] = []
        self._progress: Optional[Callable[[float, str], None]] = None

    def set_progress(self, cb: Optional[Callable[[float, str], None]]) -> None:
        self._progress = cb

    def capabilities(self) -> Dict[str, bool]:
        return {
            "load": True,
            "status": True,
            "focus": True,
            "signal": True,
            "export": True,
            "clear": True,
            "tick": True,
            "save": True,
            "evolve": True,
            "bench": False,
            "rollback": True,
        }

    def load(self, path: Optional[str] = None, build_if_missing: bool = True) -> List[str]:
        if path:
            self.active_dir = Path(path)
        ckpt = self.active_dir / "checkpoint.npz"
        man = self.active_dir / "manifest.json"

        def prog(f: float, m: str) -> None:
            if self._progress:
                self._progress(f, m)

        if ckpt.exists() and man.exists():
            self._rt = load_mvp(self.active_dir, progress=prog)
        elif build_if_missing:
            prog(0.0, "DSC: no checkpoint — building MVP")
            self._rt = build_mvp(progress=prog, save=True, active_dir=self.active_dir)
        else:
            return [f"refuse: missing checkpoint in {active_label(self.active_dir)}"]

        self.revision = self._rt.revision
        self._events.extend(self._rt.events[-20:])
        return [
            f"DSC loaded · {active_label(self.active_dir)} · {self.revision}",
            "tip: /tick 8   ·   /status   ·   /sample 16",
        ]

    def status(self) -> Dict[str, Any]:
        if self._rt is None:
            return {}
        return self._rt.status()

    def snapshot(self) -> ViewModel:
        if self._rt is None:
            return ViewModel(mode="EMPTY", revision="unloaded", caption="not loaded")
        st = self._rt.status()
        nodes_raw = self._rt.canvas_nodes(order="id")  # all cells for F015 grid
        # edges: sample among full population for the strip under the grid
        edges_raw = self._rt.canvas_edges([n["id"] for n in nodes_raw], 80)
        nodes = [
            NodeView(
                id=n["id"],
                label=n["label"],
                kind=n["kind"],
                activity=n["activity"],
                utility=n.get("utility"),
            )
            for n in nodes_raw
        ]
        edges = [
            EdgeView(src=e["src"], dst=e["dst"], weight=e["weight"], meta=e["meta"])
            for e in edges_raw
        ]
        caption = (
            f"DSC {self.revision} · 12×12 grid · {len(nodes)}/{st.get('n_nodes', 0)} cells · "
            f"{len(edges)} edges (sampled)"
        )
        return ViewModel(
            mode="DSC",
            revision=self.revision,
            caption=caption,
            nodes=nodes,
            edges=edges,
            signals={k: list(v) for k, v in self._rt.signal_hist.items()},
            events=list(self._events[-80:]) + list(self._rt.events[-40:]),
            status=st,
        )

    def focus(self, query: str) -> List[str]:
        return ["focus: DSC grid shows all cells (F015); STEM vs typed uses differentiation (F004)"]

    def sample_frame(self, phase: float) -> None:
        """Live pulse: one quiet tick every few frames keeps signals moving."""
        if self._rt is None:
            return
        # light tick every ~1s equivalent depends on sample hz; always nudge activity display
        # optional micro-tick disabled by default to avoid racing harness — just re-push activity
        act = float(self._rt.pop.activity.mean())
        import math
        live = 0.5 + 0.5 * math.sin(phase * 2.6)
        self._rt._push("live", live)
        self._rt._push("activity_mean", act * (0.85 + 0.15 * live))

    def request(self, verb: str, args: List[str]) -> List[str]:
        if verb == "load":
            return self.load(args[0] if args else None)
        if verb == "status":
            st = self.status()
            return [f"{k}: {v}" for k, v in st.items()] if st else ["not loaded"]
        if verb == "clear":
            self._events.clear()
            if self._rt:
                self._rt.events.clear()
            return ["terminal cleared"]
        if verb == "save":
            if self._rt is None:
                return ["refuse: nothing loaded"]
            name = " ".join(args) if args else None
            def prog(f, m):
                if self._progress:
                    self._progress(f, m)
            path = self._rt.save_named(name, progress=prog)
            self.revision = self._rt.revision
            # display basename only
            return [f"saved {path.name}", "active tip updated"]
        if verb == "tick":
            if self._rt is None:
                return ["refuse: nothing loaded"]
            n = int(args[0]) if args else 1
            last = self._rt.tick(n)
            return [f"ticked {n} · t={last.get('t')} err={last.get('err', 0):.4f}"]
        if verb == "signal":
            if self._rt is None:
                return ["not loaded"]
            name = args[0] if args else None
            sigs = self._rt.signal_hist
            if not name:
                return ["signals: " + ", ".join(sigs.keys())]
            if name not in sigs:
                return [f"unknown signal {name!r}"]
            h = sigs[name]
            return [f"{name}: n={len(h)} last={h[-1] if h else '—'}"]
        if verb == "focus":
            return self.focus(" ".join(args))
        if verb == "evolve":
            if self._rt is None:
                return ["refuse: nothing loaded"]
            n = 1
            if args:
                try:
                    n = int(args[0])
                except ValueError:
                    return ["usage: /evolve [n]"]
            from dsc import defaults as d
            n = max(1, min(n, d.EVOLVE_MAX_CYCLES))
            out = self._rt.evolve(n)
            return list(out["lines"])
        if verb == "rollback":
            if self._rt is None:
                return ["refuse: nothing loaded"]
            return self._rt.rollback()
        if verb == "bench":
            return ["refuse: /bench not wired — see BENCHMARKS/"]
        return [f"unknown verb /{verb}"]


def create(active_dir: Optional[str] = None) -> DscRuntimeAdapter:
    return DscRuntimeAdapter(Path(active_dir) if active_dir else None)
