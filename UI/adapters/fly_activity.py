"""F019 — Offline FlyWire activity tick (spatial kNN propagation + region drive)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set

import numpy as np

# Region name / glyph → region ids
REGION_ALIASES: Dict[str, Set[int]] = {
    "L": {1},
    "R": {2},
    "OPTIC": {1, 2},
    "V": {3},
    "VIS": {3},
    "VISUAL": {3},
    "C": {4},
    "CENTRAL": {4},
    "S": {5},
    "SENSE": {5},
    "SENSORY": {5},
    "K": {6},
    "MB": {6},
    "MUSHROOM": {6},
    "X": {7},
    "CX": {7},
    "N": {8},
    "AL": {8},
    "ANTENNAL": {8},
    "G": {9},
    "TASTE": {9},
    "GNG": {9},
    "A": {10},
    "ASCENDING": {10},
    "D": {11},
    "DESCENDING": {11},
    "M": {12},
    "MOTOR": {12},
}


def _assets_dir() -> Path:
    # UI/adapters/ -> UI/assets/biology
    return Path(__file__).resolve().parent.parent / "assets" / "biology"


class FlyActivityEngine:
    """Per-tick spike indices from region drive + spatial neighbor recruitment."""

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(42)
        self.x: Optional[np.ndarray] = None
        self.y: Optional[np.ndarray] = None
        self.region: Optional[np.ndarray] = None
        self.knn: Optional[np.ndarray] = None
        self.n = 0
        self.by_region: Dict[int, np.ndarray] = {}
        # drive: region_id → probability a sampled cell fires this tick
        self.drive: Dict[int, float] = {}
        self.recruit: np.ndarray  # per-neuron latent recruitment [0,1]
        self.recruit = np.zeros(0, dtype=np.float32)
        self.ticks = 0
        self.last_n_spikes = 0
        self.loaded = False
        self._ema = np.zeros(13, dtype=np.float64)

    def load(self, layout_path: Optional[Path] = None, knn_path: Optional[Path] = None) -> None:
        base = _assets_dir()
        layout_path = Path(layout_path) if layout_path else base / "flywire_layout.npz"
        knn_path = Path(knn_path) if knn_path else base / "flywire_knn8.npz"
        d = np.load(layout_path)
        self.x = d["x"].astype(np.float32) / 65535.0
        self.y = d["y"].astype(np.float32) / 65535.0
        self.region = d["region"].astype(np.uint8)
        self.n = int(len(self.x))
        k = np.load(knn_path)
        self.knn = k["knn"].astype(np.int32)
        if self.knn.shape[0] != self.n:
            raise RuntimeError("knn/layout length mismatch")
        self.by_region = {}
        for rid in range(13):
            idx = np.where(self.region == rid)[0]
            if len(idx):
                self.by_region[rid] = idx.astype(np.int32)
        self.recruit = np.zeros(self.n, dtype=np.float32)
        self.drive.clear()
        self.ticks = 0
        self.last_n_spikes = 0
        self.loaded = True
        self._ema = np.zeros(13, dtype=np.float64)

    def glyph_levels(self) -> Dict[str, float]:
        """Map atlas glyph → [0,1] from live region EMA."""
        from console.brain_field import GLYPH

        out: Dict[str, float] = {}
        for rid, g in GLYPH.items():
            out[g] = float(np.clip(self._ema[rid] if rid < len(self._ema) else 0.0, 0.0, 1.0))
        return out

    def rest(self) -> None:
        """Hard quiet — clear drive so BRAIN MAP + list can go still."""
        self.drive.clear()
        if hasattr(self, 'volt') and self.volt is not None:
            self.volt[:] = 0.0
        if hasattr(self, '_ema') and self._ema is not None:
            self._ema[:] = 0.0
        self.last_n_spikes = 0

    def stim(
        self,
        regions: Sequence[str],
        strength: float = 0.35,
        *,
        allow_default: bool = True,
    ) -> List[str]:
        """Enable drive on named regions (optic, AL, taste, …).

        Unknown names raise ValueError (caller should surface them) instead of
        silently falling back — that made /stim ME_R look like a no-op.
        """
        hit: Set[int] = set()
        unknown: List[str] = []
        for raw in regions:
            key = raw.strip().upper()
            if not key:
                continue
            ids = REGION_ALIASES.get(key)
            if ids:
                hit |= ids
            elif key.isdigit():
                hit.add(int(key))
            else:
                unknown.append(raw)
        if unknown:
            known = ", ".join(sorted({k for k in REGION_ALIASES if len(k) > 1}))
            raise ValueError(f"unknown region(s) {unknown} — try: {known}")
        if not hit:
            if not allow_default:
                raise ValueError("no regions")
            # default sensory: both optics + antennal + sense
            hit = {1, 2, 5, 8}
        strength = float(np.clip(strength, 0.05, 0.95))
        for rid in hit:
            # never accidentally dim an already-louder drive on bare re-stim
            prev = float(self.drive.get(rid, 0.0))
            self.drive[rid] = max(prev, strength)
            # onset kick so the atlas visibly jumps even if drive was already on
            pool = self.by_region.get(rid)
            if pool is not None and len(pool):
                n_kick = int(min(len(pool), max(24, strength * 120)))
                choose = self.rng.choice(pool, size=n_kick, replace=False)
                self.recruit[choose] = np.clip(self.recruit[choose] + 0.55, 0.0, 1.0)
                nbr = self.knn[choose].ravel() if self.knn is not None else []
                if len(nbr):
                    self.recruit[nbr] = np.clip(self.recruit[nbr] + 0.25, 0.0, 1.0)
        return [str(r) for r in sorted(hit)]

    def pulse(self, region: str, strength: float = 0.55) -> List[str]:
        self.drive.clear()
        return self.stim([region], strength=strength)

    def tick(self, max_spikes: int = 1800) -> np.ndarray:
        """Return neuron indices that 'fire' this frame."""
        if not self.loaded or self.region is None or self.knn is None:
            return np.zeros(0, dtype=np.int32)
        fired: List[np.ndarray] = []
        # 1) region drive sampling
        for rid, p in list(self.drive.items()):
            pool = self.by_region.get(rid)
            if pool is None or len(pool) == 0:
                continue
            n_take = int(min(len(pool), max(8, p * 400)))
            choose = self.rng.choice(pool, size=n_take, replace=False)
            mask = self.rng.random(n_take) < p
            sel = choose[mask]
            if len(sel):
                fired.append(sel)
                # recruit spatial neighbors
                nbr = self.knn[sel].ravel()
                self.recruit[nbr] = np.clip(self.recruit[nbr] + 0.22, 0.0, 1.0)

        # 2) recruited latent fires
        hot = np.where(self.recruit > 0.12)[0]
        if len(hot):
            p_fire = self.recruit[hot]
            mask = self.rng.random(len(hot)) < p_fire
            sel = hot[mask]
            if len(sel):
                fired.append(sel)
                nbr = self.knn[sel].ravel()
                self.recruit[nbr] = np.clip(self.recruit[nbr] + 0.12, 0.0, 1.0)

        # decay recruitment
        self.recruit *= 0.90
        self.ticks += 1

        if not fired:
            self.last_n_spikes = 0
            self._ema *= 0.90
            return np.zeros(0, dtype=np.int32)
        idx = np.unique(np.concatenate(fired)).astype(np.int32)
        if len(idx) > max_spikes:
            idx = self.rng.choice(idx, size=max_spikes, replace=False).astype(np.int32)
        self.last_n_spikes = int(len(idx))
        instant = np.zeros(13, dtype=np.float64)
        for rid in self.region[idx]:
            r = int(rid)
            if 0 <= r < 13:
                instant[r] += 1.0
        peak = float(instant.max()) or 1.0
        instant /= peak
        # recruitment glow so neighbor spread shows on atlas
        for rid, pool in self.by_region.items():
            if pool is None or len(pool) == 0 or rid >= 13:
                continue
            glow = float(np.mean(self.recruit[pool]))
            instant[rid] = max(instant[rid], min(1.0, glow))
        self._ema = 0.78 * self._ema + 0.22 * instant
        return idx
