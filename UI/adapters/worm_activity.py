"""OpenWorm live activity — graph propagation on White 1986 edges."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Set

import numpy as np
import pandas as pd

from .worm_layout import WORM_LEGEND, WORM_REGIONS, build_layout, classify

# drive aliases → class ids or name prefixes
DRIVE_ALIASES: Dict[str, Set[int]] = {
    "SENSORY": {1},
    "SENSE": {1},
    "AMPHID": {1},
    "S": {1},
    "RING": {2},
    "N": {2},
    "NERVE": {2},
    "PHARYNX": {3},
    "P": {3},
    "COMMAND": {4},
    "C": {4},
    "VENTRAL": {5},
    "MOTOR": {5, 6},
    "V": {5},
    "DORSAL": {6},
    "D": {6},
    "TAIL": {7},
    "T": {7},
}


class WormActivityEngine:
    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(7)
        self.names: List[str] = []
        self.name_to_i: Dict[str, int] = {}
        self.x = np.zeros(0, dtype=np.float32)
        self.y = np.zeros(0, dtype=np.float32)
        self.region = np.zeros(0, dtype=np.uint8)
        self.out_adj: List[List[tuple]] = []  # i → [(j, w), ...]
        self.by_class: Dict[int, np.ndarray] = {}
        self.drive: Dict[int, float] = {}
        self.name_drive: Set[str] = set()
        self.volt = np.zeros(0, dtype=np.float32)
        self.ticks = 0
        self.last_n_spikes = 0
        self.loaded = False

    def load(self, edges: pd.DataFrame) -> None:
        nodes = sorted(set(edges["pre"].astype(str)) | set(edges["post"].astype(str)))
        lay = build_layout(nodes, seed=7)
        self.names = [str(x) for x in lay["names"]]
        self.name_to_i = {n: i for i, n in enumerate(self.names)}
        self.x, self.y, self.region = lay["x"], lay["y"], lay["region"]
        n = len(self.names)
        self.volt = np.zeros(n, dtype=np.float32)
        adj: List[List[tuple]] = [[] for _ in range(n)]
        for row in edges.itertuples(index=False):
            a = self.name_to_i.get(str(row.pre))
            b = self.name_to_i.get(str(row.post))
            if a is None or b is None:
                continue
            w = float(getattr(row, "synapses", 1) or 1)
            # electrical both ways lightly
            typ = str(getattr(row, "type", "chemical")).lower()
            adj[a].append((b, w))
            if "electric" in typ:
                adj[b].append((a, w * 0.8))
        self.out_adj = adj
        self.by_class = {}
        for rid in range(8):
            idx = np.where(self.region == rid)[0]
            if len(idx):
                self.by_class[rid] = idx.astype(np.int32)
        self.drive.clear()
        self.name_drive.clear()
        self.ticks = 0
        self.loaded = True

    def rest(self) -> None:
        self.drive.clear()
        self.name_drive.clear()
        self.volt *= 0.3

    def stim(self, regions: Sequence[str], strength: float = 0.4) -> List[str]:
        hit: Set[int] = set()
        named: Set[str] = set()
        for raw in regions:
            key = raw.strip().upper()
            if not key:
                continue
            if key in DRIVE_ALIASES:
                hit |= DRIVE_ALIASES[key]
            elif key in self.name_to_i:
                named.add(key)
            elif key.startswith("AVA") or key in {"AVAL", "AVAR", "AVBL", "AVBR"}:
                named |= {n for n in self.names if n.upper().startswith(key[:3])}
            else:
                # prefix match on neuron names
                pref = [n for n in self.names if n.upper().startswith(key)]
                named.update(pref[:40])
        if not hit and not named:
            hit = {1}  # default amphid/sensory
        for rid in hit:
            self.drive[rid] = float(np.clip(strength, 0.05, 0.95))
        self.name_drive |= {n.upper() for n in named}
        return sorted({str(r) for r in hit}) + sorted(self.name_drive)[:8]

    def pulse(self, region: str, strength: float = 0.6) -> List[str]:
        self.drive.clear()
        self.name_drive.clear()
        return self.stim([region], strength=strength)

    def tick(self, max_spikes: int = 120) -> np.ndarray:
        if not self.loaded:
            return np.zeros(0, dtype=np.int32)
        n = len(self.names)
        # inject drive as voltage
        for rid, p in self.drive.items():
            pool = self.by_class.get(rid)
            if pool is None:
                continue
            k = max(2, int(len(pool) * p * 0.35))
            choose = self.rng.choice(pool, size=min(k, len(pool)), replace=False)
            self.volt[choose] += self.rng.uniform(0.8, 1.4, size=len(choose)).astype(np.float32)
        if self.name_drive:
            for nm in self.name_drive:
                i = self.name_to_i.get(nm)
                if i is not None:
                    self.volt[i] += float(self.rng.uniform(1.0, 1.6))

        # fire
        thr = 1.0
        fired = np.where(self.volt >= thr)[0]
        self.volt[fired] = 0.0
        # synaptic kick
        for i in fired:
            for j, w in self.out_adj[i]:
                self.volt[j] += 0.15 * min(w, 8.0)
        # leak
        self.volt *= 0.82
        np.clip(self.volt, 0.0, 4.0, out=self.volt)

        self.ticks += 1
        if len(fired) > max_spikes:
            fired = self.rng.choice(fired, size=max_spikes, replace=False)
        self.last_n_spikes = int(len(fired))
        return fired.astype(np.int32)
