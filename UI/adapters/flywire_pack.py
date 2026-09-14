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
        self._canvas_base: Dict[str, float] = {}
        self._canvas_neuropil: Dict[str, str] = {}
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
        try:
            mb = path.stat().st_size / (1024 * 1024)
            size_bit = f" (~{mb:.0f} MB)"
        except OSError:
            size_bit = ""
        self._prog(0.12, f"flywire: reading edge table{size_bit} — please wait…")
        self._df = pd.read_feather(path, columns=cols)
        self._prog(0.55, f"flywire: feather loaded · {len(self._df):,} rows — indexing ids")
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
            self._activity.stim(["optic", "AL", "SENSE"], strength=0.55)
            self._stim_on = True
            self._prog(0.98, "flywire: activity field ready")
        except Exception as exc:  # noqa: BLE001
            self._field = None
            self._log(f"activity field unavailable: {exc}")
        return [
            f"FLYWIRE loaded · {n:,} edges · pack {pack_label(self.pack_dir)}",
            "tip: BRAIN MAP live — sensory already on · /stim kicks louder · /rest then /stim for cold start · /pulse MB",
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
        self._canvas_base = {}
        self._canvas_neuropil = {}
        if "neuropil" in df.columns:
            for nid in top:
                hits = df[(df["pre"] == nid) | (df["post"] == nid)]["neuropil"].astype(str)
                self._canvas_neuropil[nid] = (
                    str(hits.mode().iloc[0]) if len(hits) and len(hits.mode()) else ""
                )
        self._canvas_nodes = []
        for nid in top:
            base = float(deg[nid] / max_d) if max_d else 0.0
            self._canvas_base[nid] = base
            self._canvas_nodes.append(
                NodeView(
                    id=nid,
                    label=nid[-6:],
                    kind="neuron",
                    activity=base,
                )
            )

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



    def _neuropil_to_region_ids(self, neuropil: str):
        """Map feather neuropil label → coarse layout region ids (fly_activity)."""
        from .fly_activity import REGION_ALIASES
        u = (neuropil or "").strip().upper()
        if not u:
            return set()
        hit = set()
        for key, ids in REGION_ALIASES.items():
            if len(key) < 2:
                continue
            if key == u or u.startswith(key) or key in u:
                hit |= set(ids)
        if any(tag in u for tag in ("ME_", "LO_", "LOP", "LA_", "LP_", "OC_", "AME")):
            hit |= {1, 2, 3}
        if "GNG" in u or "GUST" in u:
            hit |= {9}
        return hit

    def _sync_canvas_from_activity(self) -> None:
        """Drive the 48-list from the same region EMA as the BRAIN MAP."""
        if not self._canvas_nodes:
            return
        driven = bool(self._stim_on and self._activity.loaded and self._activity.drive)
        levels = self._activity._ema if self._activity.loaded else None
        for node in self._canvas_nodes:
            base = float(self._canvas_base.get(node.id, node.activity))
            if not driven or levels is None:
                node.activity = 0.0  # hard quiet at /rest
                continue
            rids = self._neuropil_to_region_ids(self._canvas_neuropil.get(node.id, ""))
            if rids:
                glow = max((float(levels[r]) for r in rids if r < len(levels)), default=0.0)
            else:
                glow = max(
                    (float(levels[r]) for r in self._activity.drive if r < len(levels)),
                    default=0.0,
                )
            node.activity = min(1.0, base * (0.22 + 0.78 * glow))

    def sample_frame(self, phase: float) -> None:
        """Live activity → BRAIN MAP + 48-list from same field (no ambient at rest)."""
        if self._df is None:
            return
        driven = bool(self._stim_on and self._activity.loaded and self._activity.drive)
        if self._field is not None and self._activity.loaded and driven:
            indices = self._activity.tick()
            self._field.tick(indices)
            self._status["spikes_tick"] = self._activity.last_n_spikes
            self._status["field_active"] = self._field.spikes_active()
            self._status["stim"] = "on"
            self._status["activity_ticks"] = self._activity.ticks
            self._sync_canvas_from_activity()
        else:
            # /rest: skip heavy spike tick + field paint (was bogging the sample loop)
            self._status["stim"] = "on" if (self._stim_on and driven) else "off"
            self._status["spikes_tick"] = 0
            if self._activity.loaded:
                self._sync_canvas_from_activity()
        st = self._status or {}
        n_edges = float(st.get("n_edges") or 0)
        n_nodes = float(st.get("n_nodes") or 0)
        mean_syn = float(st.get("mean_syn") or 0)
        dent = float(st.get("degree_entropy") or 0)
        spikes = float(st.get("spikes_tick") or 0)
        driven = bool(self._stim_on and self._activity.loaded and self._activity.drive)
        live = min(1.0, spikes / 800.0) if driven else 0.0
        self._push_signals(n_edges, n_nodes, mean_syn, dent)
        self._signals.setdefault("live", [])
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
            if self._field is None or not self._activity.loaded:
                return ["refuse: activity field not loaded — /load flywire first"]
            strength = 0.55
            regions: list = []
            if args:
                try:
                    strength = float(args[-1])
                    regions = list(args[:-1])
                except ValueError:
                    regions = list(args)
            if not regions:
                regions = ["optic", "AL", "SENSE"]
            already = bool(self._stim_on and self._activity.drive)
            try:
                ids = self._activity.stim(regions, strength=strength)
            except ValueError as exc:
                return [f"refuse: {exc}"]
            self._stim_on = True
            # force an immediate tick so the map jumps this frame
            indices = self._activity.tick()
            self._field.tick(indices)
            self._status["spikes_tick"] = self._activity.last_n_spikes
            self._status["stim"] = "on"
            note = "boost" if already else "on"
            self._log(f"stim {note} → {ids} strength={strength:.2f}")
            return [
                f"stim {note} · regions={ids} · strength={strength:.2f}",
                ("(sensory was already driving — kicked the field louder; "
                 "/rest then /stim to see a cold start)")
                if already
                else "(watch BRAIN MAP — optic/AL/sense glyphs should brighten)",
            ]
        if verb == "pulse":
            if self._field is None or not self._activity.loaded:
                return ["refuse: activity field not loaded — /load flywire first"]
            region = args[0] if args else "optic"
            strength = float(args[1]) if len(args) > 1 else 0.7
            try:
                ids = self._activity.pulse(region, strength=strength)
            except ValueError as exc:
                return [f"refuse: {exc}"]
            self._stim_on = True
            indices = self._activity.tick()
            self._field.tick(indices)
            self._status["spikes_tick"] = self._activity.last_n_spikes
            self._status["stim"] = "on"
            return [f"pulse {region} · regions={ids} · strength={strength:.2f} · watch the map"]
        if verb == "rest":
            if self._field is None or not self._activity.loaded:
                return ["refuse: activity field not loaded"]
            self._activity.rest()
            self._field.reset()
            self._stim_on = False
            self._status["stim"] = "off"
            self._status["spikes_tick"] = 0
            self._sync_canvas_from_activity()
            self._log("rest — drive+recruit cleared")
            return ["rest · drive cleared · map + neuron list should go quiet (then /stim to wake)"]
        if verb in ("tick", "evolve", "bench", "rollback", "save"):
            return [f"refuse: /{verb} is DSC-only — FLYWIRE is comparison (+ live map)"]
        return [f"unknown verb /{verb}"]


    def brain_map_markup(self, focus: Optional[str] = None) -> str:
        """Paint curated BRAIN MAP atlas from live kNN/region activity levels."""
        if not self._activity.loaded:
            return ""
        from console.biology import fly_brain_ascii

        return fly_brain_ascii(
            focus=focus,
            phase=float(self._activity.ticks) * 0.12,
            levels=self._activity.glyph_levels(),
        )


# module-level factory used by console
def create(pack_dir: Optional[str] = None) -> FlyWirePackAdapter:
    return FlyWirePackAdapter(Path(pack_dir) if pack_dir else None)
