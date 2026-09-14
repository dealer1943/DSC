"""F019 — Soma-projected live BRAIN MAP activity field (FlyBrains behavior)."""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# Region id → glyph / hex (FlyBrains legend)
REGIONS: Tuple[Tuple[int, str, str, str], ...] = (
    (0, ".", "#666666", "other"),
    (1, "L", "#33d6ff", "optic L"),
    (2, "R", "#27c0b0", "optic R"),
    (3, "V", "#b78cff", "visual"),
    (4, "C", "#ffcc33", "central"),
    (5, "S", "#ff9900", "sensory"),
    (6, "K", "#e6e600", "mushroom"),
    (7, "X", "#ff33cc", "CX"),
    (8, "N", "#55ee66", "antennal"),
    (9, "G", "#ee7722", "taste"),
    (10, "A", "#52cc52", "ascending"),
    (11, "D", "#ff3333", "descending"),
    (12, "M", "#ccee33", "motor"),
)
GLYPH: Dict[int, str] = {r[0]: r[1] for r in REGIONS}
COLOR: Dict[int, str] = {r[0]: r[2] for r in REGIONS}
LABEL: Dict[int, str] = {r[0]: r[3] for r in REGIONS}
LEGEND = "L/R  V  C  S  K=MB  X=CX  N=AL  G  A/D/M"
SILHOUETTE = " .:-=+*#%@"


def _hex_scale(hex_color: str, level: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    u = 0.0 if level < 0 else 1.0 if level > 1 else float(level)
    u = 0.28 + 0.72 * u
    return f"#{int(r * u):02x}{int(g * u):02x}{int(b * u):02x}"


class BrainField:
    """Project spikes onto a 2D grid; decay + neighbor bleed; paint region glyphs."""

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        region: np.ndarray,
        width: int = 44,
        height: int = 16,
        regions: Optional[Tuple[Tuple[int, str, str, str], ...]] = None,
        legend: Optional[str] = None,
        title: str = "BRAIN MAP",
    ):
        self.x = np.asarray(x, dtype=np.float32)
        self.y = np.asarray(y, dtype=np.float32)
        self.region = np.asarray(region, dtype=np.uint8)
        self.n_neurons = int(len(self.x))
        self.width = max(8, int(width))
        self.height = max(4, int(height))
        self._regions = regions if regions is not None else REGIONS
        self._glyph = {r[0]: r[1] for r in self._regions}
        self._color = {r[0]: r[2] for r in self._regions}
        self._label = {r[0]: r[3] for r in self._regions}
        self._legend = legend if legend is not None else LEGEND
        self._title = title
        self.energy = np.zeros((self.height, self.width), dtype=np.float64)
        self.hit = np.zeros((self.height, self.width), dtype=np.uint8)
        self.occupancy = np.zeros((self.height, self.width), dtype=np.float64)
        self._xs = np.zeros(self.n_neurons, dtype=np.int32)
        self._ys = np.zeros(self.n_neurons, dtype=np.int32)
        self._project()

    def _project(self) -> None:
        w, h = self.width, self.height
        self._xs = np.clip((self.x * (w - 1)).astype(np.int32), 0, w - 1)
        self._ys = np.clip((self.y * (h - 1)).astype(np.int32), 0, h - 1)
        occ = np.zeros((h, w), dtype=np.float64)
        np.add.at(occ, (self._ys, self._xs), 1.0)
        positive = occ[occ > 0]
        peak = float(np.percentile(positive, 90)) if positive.size else 1.0
        self.occupancy = np.clip(occ / max(peak, 1.0), 0.0, 1.0)
        self.energy = np.zeros((h, w), dtype=np.float64)
        self.hit = np.zeros((h, w), dtype=np.uint8)

    def resize(self, width: int, height: int) -> None:
        width, height = max(8, int(width)), max(4, int(height))
        if width == self.width and height == self.height:
            return
        self.width, self.height = width, height
        self._project()

    def tick(self, indices: Sequence[int], decay: float = 0.84) -> None:
        self.energy *= decay
        self.hit[self.energy < 0.08] = 0
        if not len(indices):
            self.energy = np.clip(self.energy, 0.0, 16.0)
            return
        idx = np.clip(np.asarray(indices, dtype=np.int64), 0, self.n_neurons - 1)
        xs, ys = self._xs[idx], self._ys[idx]
        np.add.at(self.energy, (ys, xs), 2.6)
        self.hit[ys, xs] = self.region[idx]
        h, w = self.height, self.width
        for dy, dx, weight in (
            (0, 1, 0.45),
            (0, -1, 0.45),
            (1, 0, 0.45),
            (-1, 0, 0.45),
        ):
            ny = np.clip(ys + dy, 0, h - 1)
            nx = np.clip(xs + dx, 0, w - 1)
            np.add.at(self.energy, (ny, nx), weight)
            empty = self.hit[ny, nx] == 0
            self.hit[ny[empty], nx[empty]] = self.region[idx][empty]
        self.energy = np.clip(self.energy, 0.0, 16.0)

    def reset(self) -> None:
        self.energy[:] = 0
        self.hit[:] = 0

    def paint_markup(self, focus: Optional[str] = None) -> str:
        """Rich markup lines for the biology pane."""
        from console.color import markup_fg

        peak = float(self.energy.max())
        scale = peak if peak > 0.12 else 1.0
        map_w = self.width
        lines: List[str] = [
            markup_fg(self._title.ljust(map_w)[:map_w], 0.55),
            markup_fg(self._legend[:map_w].ljust(map_w), 0.32),
        ]

        focus_u = (focus or "").strip().upper()
        # which glyphs match focus
        focus_glyphs = set()
        if focus_u and focus_u not in ("ALL", "OFF", "*", "CLEAR"):
            for rid, g, _c, lab in self._regions:
                blob = f"{g} {lab} {self._label.get(rid, '')}".upper()
                aliases = {
                    "OPTIC": "L R",
                    "MB": "K",
                    "CX": "X",
                    "AL": "N",
                    "TASTE": "G",
                    "GNG": "G",
                    "VIS": "V",
                    "SENSE": "S",
                    "CENTRAL": "C",
                }
                extra = aliases.get(focus_u, "")
                if (
                    focus_u == g
                    or focus_u in blob
                    or g in extra.split()
                    or focus_u in lab.upper()
                ):
                    focus_glyphs.add(g)

        nbsp = "\u00a0"
        for y in range(self.height):
            parts: List[str] = []
            for x in range(map_w):
                e = float(self.energy[y, x] / scale)
                rid = int(self.hit[y, x])
                if e >= 0.08 and rid:
                    ch = self._glyph.get(rid, "*")
                    hex_c = self._color.get(rid, "#ffffff")
                    if focus_glyphs and ch not in focus_glyphs:
                        parts.append(markup_fg(ch, 0.12))
                    else:
                        parts.append(f"[{_hex_scale(hex_c, e)}]{ch}[/]")
                else:
                    sil = float(self.occupancy[y, x])
                    if sil <= 0.02:
                        parts.append(nbsp)
                    else:
                        gi = min(len(SILHOUETTE) - 1, int(round(sil * (len(SILHOUETTE) - 1))))
                        parts.append(markup_fg(SILHOUETTE[gi], 0.18 + 0.25 * sil))
            lines.append("".join(parts))
        tip = focus_u if focus_u else "all"
        lines.append(markup_fg(f"focus:{tip}"[:map_w].ljust(map_w), 0.38))
        return "\n".join(lines)

    def spikes_active(self) -> int:
        return int(np.sum(self.energy >= 0.08))
