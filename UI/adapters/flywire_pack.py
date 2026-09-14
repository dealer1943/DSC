"""FlyWire v783 pack adapter — samples for canvas; never draws the full brain."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .base import EdgeView, NodeView, ViewModel
from .fly_activity import FlyActivityEngine
from console.brain_field import BrainField

ADAPTER_NAME = "flywire"
IMPLEMENTED = True

DEFAULT_PACK = Path(__file__).resolve().parents[2] / "MODELS" / "fly" / "flywire_v783"
CONNECTIONS = "proofread_connections_783.feather"

def pack_label(path: Path) -> str:
    """Public display name only — never leak home/folder stack."""
    return Path(path).name or "pack"


# Keep canvas tiny for TUI demos
MAX_CANVAS_NODES = 48
MAX_CANVAS_EDGES = 120
SIGNAL_HISTORY = 64


class FlyWirePackAdapter:
    name = "flywire"

    def __init__(self, pack_dir: Optional[Path] = None):
        self.pack_dir = Path(pack_dir) if pack_dir else DEFAULT_PACK
        self.revision = "unloaded"
        self._df: Optional[pd.DataFrame] = None
        self._focus: Optional[str] = None  # neuropil substring or node id
        self._events: List[str] = []
        self._activity = FlyActivityEngine()
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
        path = self.pack_dir / CONNECTIONS
        if not path.exists():
            return [
                f"refuse: missing {CONNECTIONS} in pack {pack_label(self.pack_dir)}",
                "see root README.md → Getting biological packs (FlyWire v783)",
            ]
        cols = ["pre_pt_root_id", "post_pt_root_id", "neuropil", "syn_count"]
        self._prog(0.05, f"flywire: opening {path.name}")
        self._log(f"loading {path.name} …")
        self._prog(0.15, "flywire: reading edge table")
        self._df = pd.read_feather(path, columns=cols)
        self._prog(0.65, "flywire: indexing ids")
        # normalize ids to str for TUI
        self._df["pre"] = self._df["pre_pt_root_id"].astype(str)
        self._df["post"] = self._df["post_pt_root_id"].astype(str)
        self._df["neuropil"] = self._df["neuropil"].astype(str)
        n = len(self._df)
        self.revision = f"flywire_v783:{path.stat().st_size}"
        self._focus = None
        self._prog(0.8, "flywire: building canvas sample")
        self._rebuild_views()
        self._prog(1.0, f"flywire: ready · {pack_label(self.pack_dir)}")
        self._log(f"loaded proofread connections: {n:,} edges from {pack_label(self.pack_dir)}")
        try:
            self._prog(0.9, "flywire: activity field")
            self._activity.load()
            self._field = BrainField(
                self._activity.x, self._activity.y, self._activity.region,
                width=44, height=16,
            )
            self._activity.stim(["optic", "AL"], strength=0.28)
            self._stim_on = True
            self._prog(0.98, "flywire: activity field ready")
        except Exception as exc:  # noqa: BLE001
            self._field = None
            self._log(f"activity field unavailable: {exc}")
        return [
            f"FLYWIRE loaded · {n:,} edges · pack {pack_label(self.pack_dir)}",
            "tip: BRAIN MAP is live — /stim optic|AL|taste  ·  /pulse MB  ·  /rest  ·  /focus AL",
        ]

    def _filtered(self) -> pd.DataFrame:
        assert self._df is not None
        df = self._df
        if not self._focus:
            return df
        q = self._focus
        # neuropil match (case-insensitive substring) or node id exact
        mask = df["neuropil"].str.contains(q, case=False, na=False)
        if mask.any():
            return df.loc[mask]
        return df[(df["pre"] == q) | (df["post"] == q)]

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
            self._push_signals(0, 0, 0.0, 0.0)
            return

        # degree on filtered graph
        deg = Counter(df["pre"]) + Counter(df["post"])
        n_nodes = len(deg)
        mean_syn = float(df["syn_count"].mean()) if "syn_count" in df.columns else 0.0
        deg_vals = np.fromiter(deg.values(), dtype=np.float64)
        dent = self._degree_entropy(deg_vals)

        top = [nid for nid, _ in deg.most_common(MAX_CANVAS_NODES)]
        top_set = set(top)
        max_d = deg.most_common(1)[0][1]
        self._canvas_nodes = [
            NodeView(
                id=nid,
                label=nid[-6:],
                kind="neuron",
                activity=deg[nid] / max_d if max_d else 0.0,
            )
            for nid in top
        ]

        # edges among top nodes, heaviest first
        sub = df[df["pre"].isin(top_set) & df["post"].isin(top_set)]
        if len(sub) > MAX_CANVAS_EDGES:
            sub = sub.nlargest(MAX_CANVAS_EDGES, "syn_count")
        self._canvas_edges = [
            EdgeView(src=r.pre, dst=r.post, weight=float(r.syn_count), meta=str(r.neuropil))
            for r in sub.itertuples(index=False)
        ]

        focus_bit = f"focus={self._focus}" if self._focus else "focus=all"
        self._caption = (
            f"{focus_bit} · showing {len(self._canvas_nodes)} of {n_nodes:,} nodes · "
            f"{len(self._canvas_edges)} of {n_edges:,} edges (sampled)"
        )
        # neuropil histogram (top 8)
        np_counts = df["neuropil"].value_counts().head(8).to_dict()
        self._status = {
            "mode": "FLYWIRE",
            "pack": pack_label(self.pack_dir),
            "n_edges": n_edges,
            "n_nodes": n_nodes,
            "mean_syn": round(mean_syn, 3),
            "degree_entropy": round(dent, 3),
            "focus": self._focus,
            "top_neuropils": np_counts,
            "canvas_nodes": len(self._canvas_nodes),
            "canvas_edges": len(self._canvas_edges),
        }
        self._push_signals(n_edges, n_nodes, mean_syn, dent)

    def _push_signals(self, n_edges: int, n_nodes: int, mean_syn: float, dent: float) -> None:
        for key, val in (
            ("n_edges", float(n_edges)),
            ("n_nodes", float(n_nodes)),
            ("mean_syn", float(mean_syn)),
            ("degree_entropy", float(dent)),
        ):
            hist = self._signals.setdefault(key, [])
            hist.append(val)
            if len(hist) > SIGNAL_HISTORY:
                self._signals[key] = hist[-SIGNAL_HISTORY:]


    def sample_frame(self, phase: float) -> None:
        """Live activity tick → BRAIN MAP field + chart breathes."""
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
        e_pulse = 1.0 + 0.012 * math.sin(phase * 1.7)
        n_pulse = 1.0 + 0.008 * math.sin(phase * 2.1 + 0.4)
        s_pulse = mean_syn * (1.0 + 0.04 * math.sin(phase * 2.9 + 1.1))
        d_pulse = dent * (1.0 + 0.015 * math.sin(phase * 1.3 + 2.0))
        spikes = float(st.get("spikes_tick") or 0)
        live = min(1.0, spikes / 800.0) if spikes else (0.08 + 0.04 * math.sin(phase * 2.6))
        self._signals.setdefault("live", [])
        self._push_signals(n_edges * e_pulse, n_nodes * n_pulse, s_pulse, d_pulse)
        hist = self._signals["live"]
        hist.append(live)
        if len(hist) > SIGNAL_HISTORY:
            self._signals["live"] = hist[-SIGNAL_HISTORY:]
        sh = self._signals.setdefault("spikes_tick", [])
        sh.append(spikes)
        if len(sh) > SIGNAL_HISTORY:
            self._signals["spikes_tick"] = sh[-SIGNAL_HISTORY:]

    def focus(self, query: str) -> List[str]:
        if self._df is None:
            return ["refuse: nothing loaded — /load flywire first"]
        q = query.strip()
        if q in ("", "all", "*", "clear"):
            self._focus = None
            self._rebuild_views()
            self._log("focus cleared (all edges)")
            return ["focus=all", self._caption]
        self._focus = q
        self._rebuild_views()
        self._log(f"focus set to {q!r} · {self._status.get('n_edges', 0):,} edges")
        return [f"focus={q}", self._caption]

    def status(self) -> Dict[str, Any]:
        return dict(self._status)

    def snapshot(self) -> ViewModel:
        return ViewModel(
            mode="FLYWIRE" if self._df is not None else "EMPTY",
            revision=self.revision,
            caption=self._caption,
            nodes=list(self._canvas_nodes),
            edges=list(self._canvas_edges),
            signals={k: list(v) for k, v in self._signals.items()},
            events=list(self._events[-80:]),
            status=self.status(),
        )

    def request(self, verb: str, args: List[str]) -> List[str]:
        caps = self.capabilities()
        if verb in caps and not caps[verb] and verb not in ("help", "load", "status", "focus", "signal", "clear", "stim", "rest", "pulse"):
            return [f"refuse: /{verb} not supported on FLYWIRE adapter"]
        if verb == "load":
            pack = args[0] if args else None
            return self.load(pack)
        if verb == "status":
            st = self.status()
            if not st:
                return ["not loaded"]
            lines = [f"{k}: {v}" for k, v in st.items() if k != "top_neuropils"]
            tops = st.get("top_neuropils") or {}
            if tops:
                lines.append("top_neuropils: " + ", ".join(f"{k}={v}" for k, v in tops.items()))
            return lines
        if verb == "focus":
            return self.focus(" ".join(args) if args else "all")
        if verb == "signal":
            name = args[0] if args else None
            if not name:
                return ["signals: " + ", ".join(self._signals.keys())]
            if name not in self._signals:
                return [f"unknown signal {name!r}", "signals: " + ", ".join(self._signals.keys())]
            hist = self._signals[name]
            return [f"{name}: n={len(hist)} last={hist[-1] if hist else '—'}"]
        if verb == "clear":
            self._events.clear()
            return ["terminal cleared"]
        if verb == "stim":
            if self._field is None:
                return ["refuse: activity field not loaded"]
            regions = list(args) if args else ["optic", "AL"]
            strength = 0.35
            if args:
                try:
                    strength = float(args[-1])
                    regions = args[:-1] or ["optic", "AL"]
                except ValueError:
                    regions = list(args)
            ids = self._activity.stim(regions, strength=strength)
            self._stim_on = True
            self._log(f"stim → {ids} strength={strength:.2f}")
            return [f"stim on · regions={ids} · strength={strength:.2f}"]
        if verb == "pulse":
            if self._field is None:
                return ["refuse: activity field not loaded"]
            region = args[0] if args else "optic"
            strength = float(args[1]) if len(args) > 1 else 0.55
            ids = self._activity.pulse(region, strength=strength)
            self._stim_on = True
            return [f"pulse {region} · regions={ids} · strength={strength:.2f}"]
        if verb == "rest":
            if self._field is None:
                return ["refuse: activity field not loaded"]
            self._activity.rest()
            self._stim_on = False
            self._log("rest — drive cleared; field decaying")
            return ["rest · drive cleared · watch the map decay"]
        if verb in ("tick", "evolve", "bench", "rollback", "save"):
            return [f"refuse: /{verb} is DSC-only — FLYWIRE is comparison (+ live map)"]
        return [f"unknown verb /{verb}"]


    def brain_map_markup(self, focus: Optional[str] = None) -> str:
        """F019 live BRAIN MAP paint for the biology pane."""
        if self._field is None:
            return ""
        return self._field.paint_markup(focus=focus)


# module-level factory used by console
def create(pack_dir: Optional[str] = None) -> FlyWirePackAdapter:
    return FlyWirePackAdapter(Path(pack_dir) if pack_dir else None)
