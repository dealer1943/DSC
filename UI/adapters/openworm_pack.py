"""OpenWorm / C. elegans pack adapter — live anatomical activity field."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import EdgeView, NodeView, ViewModel
from .worm_activity import WormActivityEngine
from .worm_layout import WORM_LEGEND, WORM_REGIONS
from console.brain_field import BrainField

ADAPTER_NAME = "openworm"
IMPLEMENTED = True

DEFAULT_PACK = Path(__file__).resolve().parents[2] / "MODELS" / "worm" / "openworm_c302"
EDGES_NEURAL = "edges_neural.csv"
EDGES_ALL = "edges.csv"

MAX_CANVAS_NODES = 48
MAX_CANVAS_EDGES = 120


def pack_label(path: Path) -> str:
    return Path(path).name or "pack"


class OpenWormPackAdapter:
    name = "openworm"

    def __init__(self, pack_dir: Optional[Path] = None):
        self.pack_dir = Path(pack_dir) if pack_dir else DEFAULT_PACK
        self.revision = "unloaded"
        self._df: Optional[pd.DataFrame] = None
        self._focus: Optional[str] = None
        self._events: List[str] = []
        self._activity = WormActivityEngine()
        self._field: Optional[BrainField] = None
        self._stim_on = False
        self._signals: Dict[str, List[float]] = {
            "n_edges": [],
            "n_nodes": [],
            "mean_syn": [],
            "degree_entropy": [],
        }
        self._canvas_nodes: List[NodeView] = []
        self._canvas_edges: List[EdgeView] = []
        self._caption = "not loaded"
        self._status: Dict[str, Any] = {}
        self._progress: Optional[Callable[[float, str], None]] = None

    def set_progress(self, cb: Optional[Callable[[float, str], None]]) -> None:
        self._progress = cb

    def _prog(self, frac: float, message: str) -> None:
        if self._progress:
            self._progress(frac, message)

    def capabilities(self) -> Dict[str, bool]:
        return {
            "load": True,
            "status": True,
            "focus": True,
            "signal": True,
            "export": True,
            "clear": True,
            "tick": False,
            "save": False,
            "evolve": False,
            "bench": False,
            "rollback": False,
            "stim": True,
            "rest": True,
            "pulse": True,
        }

    def _log(self, line: str) -> None:
        self._events.append(line)
        if len(self._events) > 400:
            self._events = self._events[-400:]

    def load(self, pack_dir: Optional[str] = None) -> List[str]:
        if pack_dir:
            self.pack_dir = Path(pack_dir)
        path = self.pack_dir / EDGES_NEURAL
        if not path.exists():
            path = self.pack_dir / EDGES_ALL
        if not path.exists():
            return [
                f"refuse: missing {EDGES_NEURAL} in pack {pack_label(self.pack_dir)}",
                "see MODELS/worm/openworm_c302/README.md",
            ]
        self._prog(0.1, f"openworm: reading {path.name}")
        self._df = pd.read_csv(path)
        self._df["pre"] = self._df["pre"].astype(str)
        self._df["post"] = self._df["post"].astype(str)
        self._df["type"] = self._df["type"].astype(str)
        if "synapses" not in self._df.columns:
            self._df["synapses"] = 1
        n = len(self._df)
        self.revision = f"openworm_c302:{n}"
        self._focus = None
        self._prog(0.55, "openworm: building canvas")
        self._rebuild_views()
        try:
            self._prog(0.8, "openworm: activity field")
            self._activity.load(self._df)
            self._field = BrainField(
                self._activity.x,
                self._activity.y,
                self._activity.region,
                width=44,
                height=12,
                regions=WORM_REGIONS,
                legend=WORM_LEGEND,
                title="WORM MAP",
            )
            self._activity.stim(["amphid", "ring"], strength=0.72)
            self._stim_on = True
            self._prog(0.98, "openworm: activity field ready")
        except Exception as exc:  # noqa: BLE001
            self._field = None
            self._log(f"activity field unavailable: {exc}")
        self._prog(1.0, f"openworm: ready · {pack_label(self.pack_dir)}")
        self._log(f"loaded {n:,} edges from {pack_label(self.pack_dir)}")
        return [
            f"OPENWORM loaded · {n:,} edges · pack {pack_label(self.pack_dir)}",
            "tip: WORM MAP live sensory — amphid+ring on · /stim · /pulse AVAL · /rest",
        ]

    def _filtered(self) -> pd.DataFrame:
        assert self._df is not None
        df = self._df
        if not self._focus:
            return df
        q = self._focus.upper()
        mask = (
            df["pre"].str.upper().str.contains(q, na=False)
            | df["post"].str.upper().str.contains(q, na=False)
            | df["type"].str.upper().str.contains(q, na=False)
        )
        return df.loc[mask]

    @staticmethod
    def _degree_entropy(degrees: np.ndarray) -> float:
        if degrees.size == 0:
            return 0.0
        total = degrees.sum()
        if total <= 0:
            return 0.0
        p = degrees / total
        p = p[p > 0]
        return float(-(p * np.log2(p)).sum())

    def _rebuild_views(self) -> None:
        if self._df is None:
            return
        df = self._filtered()
        n_edges = int(len(df))
        if n_edges == 0:
            self._canvas_nodes, self._canvas_edges = [], []
            self._caption = f"focus={self._focus!r} · 0 edges"
            self._status = {"n_edges": 0, "n_nodes": 0, "focus": self._focus}
            return

        deg = Counter(df["pre"]) + Counter(df["post"])
        n_nodes = len(deg)
        mean_syn = float(df["synapses"].mean())
        dent = self._degree_entropy(np.fromiter(deg.values(), dtype=np.float64))
        top = [nid for nid, _ in deg.most_common(MAX_CANVAS_NODES)]
        top_set = set(top)
        max_d = deg.most_common(1)[0][1]
        self._canvas_nodes = [
            NodeView(
                id=nid,
                label=nid[:8],
                kind="neuron",
                activity=deg[nid] / max_d if max_d else 0.0,
            )
            for nid in top
        ]
        sub = df[df["pre"].isin(top_set) & df["post"].isin(top_set)]
        if len(sub) > MAX_CANVAS_EDGES:
            sub = sub.nlargest(MAX_CANVAS_EDGES, "synapses")
        self._canvas_edges = [
            EdgeView(src=r.pre, dst=r.post, weight=float(r.synapses), meta=str(r.type))
            for r in sub.itertuples(index=False)
        ]
        focus_bit = f"focus={self._focus}" if self._focus else "focus=all"
        self._caption = (
            f"{focus_bit} · showing {len(self._canvas_nodes)} of {n_nodes:,} nodes · "
            f"{len(self._canvas_edges)} of {n_edges:,} edges"
        )
        type_counts = df["type"].value_counts().to_dict()
        self._status = {
            "mode": "OPENWORM",
            "pack": pack_label(self.pack_dir),
            "organism": "C. elegans",
            "n_edges": n_edges,
            "n_nodes": n_nodes,
            "mean_syn": round(mean_syn, 3),
            "degree_entropy": round(dent, 3),
            "focus": self._focus,
            "edge_types": type_counts,
            "canvas_nodes": len(self._canvas_nodes),
            "canvas_edges": len(self._canvas_edges),
        }
        for key, val in (
            ("n_edges", float(n_edges)),
            ("n_nodes", float(n_nodes)),
            ("mean_syn", float(mean_syn)),
            ("degree_entropy", float(dent)),
        ):
            h = self._signals.setdefault(key, [])
            h.append(val)
            if len(h) > 64:
                self._signals[key] = h[-64:]

    def status(self) -> Dict[str, Any]:
        return dict(self._status)

    def snapshot(self) -> ViewModel:
        return ViewModel(
            mode="OPENWORM",
            revision=self.revision,
            caption=self._caption,
            nodes=list(self._canvas_nodes),
            edges=list(self._canvas_edges),
            signals={k: list(v) for k, v in self._signals.items()},
            events=list(self._events[-80:]),
            status=self.status(),
        )

    def focus(self, query: str) -> List[str]:
        self._focus = query.strip() or None
        self._rebuild_views()
        st = self.status()
        return [f"focus → {self._focus or 'all'} · edges={st.get('n_edges')} nodes={st.get('n_nodes')}"]

    def sample_frame(self, phase: float) -> None:
        if self._df is None:
            return
        import math

        if self._field is not None and self._activity.loaded:
            indices = self._activity.tick()
            self._field.tick(indices)
            self._status["spikes_tick"] = self._activity.last_n_spikes
            self._status["field_active"] = self._field.spikes_active()
            self._status["stim"] = "on" if self._stim_on else "off"
            self._status["activity_ticks"] = self._activity.ticks
        st = self._status or {}
        n_edges = float(st.get("n_edges") or 0)
        n_nodes = float(st.get("n_nodes") or 0)
        mean_syn = float(st.get("mean_syn") or 0)
        dent = float(st.get("degree_entropy") or 0)
        spikes = float(st.get("spikes_tick") or 0)
        live = min(1.0, spikes / 80.0) if spikes else (0.08 + 0.04 * math.sin(phase * 2.6))
        for key, val in (
            ("n_edges", n_edges * (1.0 + 0.012 * math.sin(phase * 1.7))),
            ("n_nodes", n_nodes * (1.0 + 0.008 * math.sin(phase * 2.1))),
            ("mean_syn", mean_syn * (1.0 + 0.04 * math.sin(phase * 2.9))),
            ("degree_entropy", dent * (1.0 + 0.015 * math.sin(phase * 1.3))),
            ("live", live),
            ("spikes_tick", spikes),
        ):
            h = self._signals.setdefault(key, [])
            h.append(float(val))
            if len(h) > 64:
                self._signals[key] = h[-64:]

    def brain_map_markup(self, focus: Optional[str] = None) -> str:
        """Paint curated WORM MAP atlas from live White-edge activity levels."""
        if not self._activity.loaded:
            return ""
        from console.biology import worm_brain_ascii

        return worm_brain_ascii(
            focus=focus,
            phase=float(self._activity.ticks) * 0.15,
            levels=self._activity.glyph_levels(),
        )

    def request(self, verb: str, args: List[str]) -> List[str]:
        caps = self.capabilities()
        if verb in caps and not caps[verb] and verb not in (
            "help", "load", "status", "focus", "signal", "clear", "stim", "rest", "pulse",
        ):
            return [f"refuse: /{verb} not supported on OPENWORM adapter"]
        if verb == "load":
            return self.load(args[0] if args else None)
        if verb == "status":
            st = self.status()
            return [f"{k}: {v}" for k, v in st.items()] if st else ["not loaded"]
        if verb == "clear":
            self._events.clear()
            return ["terminal cleared"]
        if verb == "focus":
            return self.focus(" ".join(args))
        if verb == "signal":
            name = args[0] if args else None
            if not name:
                return ["signals: " + ", ".join(self._signals.keys())]
            if name not in self._signals:
                return [f"unknown signal {name!r}"]
            h = self._signals[name]
            return [f"{name}: n={len(h)} last={h[-1] if h else '—'}"]
        if verb == "stim":
            if self._field is None:
                return ["refuse: activity field not loaded"]
            regions = list(args) if args else ["amphid"]
            strength = 0.45
            if args:
                try:
                    strength = float(args[-1])
                    regions = args[:-1] or ["amphid"]
                except ValueError:
                    regions = list(args)
            ids = self._activity.stim(regions, strength=strength)
            self._stim_on = True
            return [f"stim on · {ids} · strength={strength:.2f}"]
        if verb == "pulse":
            if self._field is None:
                return ["refuse: activity field not loaded"]
            region = args[0] if args else "amphid"
            strength = float(args[1]) if len(args) > 1 else 0.65
            ids = self._activity.pulse(region, strength=strength)
            self._stim_on = True
            return [f"pulse {region} · {ids} · strength={strength:.2f}"]
        if verb == "rest":
            if self._field is None:
                return ["refuse: activity field not loaded"]
            self._activity.rest()
            self._stim_on = False
            return ["rest · drive cleared · watch the map decay"]
        if verb in ("tick", "evolve", "bench", "rollback", "save"):
            return [f"refuse: /{verb} is DSC-only — OPENWORM is comparison (+ live map)"]
        return [f"unknown verb /{verb}"]


def create(pack_dir: Optional[str] = None) -> OpenWormPackAdapter:
    return OpenWormPackAdapter(Path(pack_dir) if pack_dir else None)
