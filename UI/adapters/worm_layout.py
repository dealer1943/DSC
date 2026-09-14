"""C. elegans soma layout — elongated nervous system (anterior→posterior)."""
from __future__ import annotations

import math
import re
from typing import Dict, List, Sequence, Tuple

import numpy as np

# class id → glyph, color, label (for BrainField)
WORM_REGIONS: Tuple[Tuple[int, str, str, str], ...] = (
    (0, ".", "#555555", "other"),
    (1, "S", "#33d6ff", "sensory"),
    (2, "N", "#ffcc33", "nerve ring"),
    (3, "P", "#ee9944", "pharynx"),
    (4, "C", "#55ee66", "command"),
    (5, "V", "#b78cff", "ventral motor"),
    (6, "D", "#ff66aa", "dorsal motor"),
    (7, "T", "#ff3333", "tail"),
)
WORM_LEGEND = "S sense  N ring  P pharynx  C command  V vent  D dors  T tail"

_AMPHID = {
    "ASH", "ASE", "AWC", "ADL", "ADF", "ASG", "ASI", "ASJ", "ASK",
    "AWA", "AWB", "BAG", "URA", "URY", "OLQ", "OLL", "IL1", "IL2", "CEP",
}
_RING = {
    "RI", "RM", "SMB", "SMD", "SAA", "SIA", "SIB", "RIC", "RIS", "RIP", "RID",
    "AIA", "AIB", "AIY", "AIZ", "AIN", "AIM", "AIAL", "AIAR",
}
_COMMAND = {"AVA", "AVB", "AVD", "AVE", "PVC", "AVJ", "AVH", "AVF", "AVG", "AVL", "DVA", "DVB", "DVC"}
_PHARYNX_PREF = ("I1", "I2", "I3", "I4", "I5", "I6", "M1", "M2", "M3", "M4", "M5", "MI", "MCL", "MCR", "NSM")
_VENTRAL = {"VA", "VB", "VD", "AS", "VC"}
_DORSAL = {"DA", "DB", "DD"}
_TAIL = {"PLM", "PLN", "PVR", "PVW", "PVT", "PQR", "PDA", "PDB", "ALA", "DVA"}


def _base(name: str) -> str:
    """Strip L/R/digits: AVAL→AVA, VB02→VB, ASHL→ASH."""
    n = name.upper()
    # motor classes with numbers: VB1, AS10
    m = re.match(r"^([A-Z]{1,3})\d+", n)
    if m:
        return m.group(1)
    if n.endswith(("L", "R")) and len(n) > 2:
        return n[:-1]
    return n


def _side(name: str) -> float:
    """-1 left, +1 right, 0 midline."""
    n = name.upper()
    if len(n) >= 3 and n[-1] == "L" and n[-2].isalpha():
        return -1.0
    if len(n) >= 3 and n[-1] == "R" and n[-2].isalpha():
        return 1.0
    return 0.0


def classify(name: str) -> int:
    b = _base(name)
    n = name.upper()
    if b in _AMPHID or n.startswith(tuple(_AMPHID)):
        return 1
    if any(n.startswith(p) for p in _PHARYNX_PREF) or b in {"NSM", "M1", "M2", "M3", "M4", "M5", "MI"}:
        return 3
    if b in _COMMAND or n.startswith(("AVA", "AVB", "AVD", "AVE", "PVC")):
        return 4
    if b in _VENTRAL or re.match(r"^(VA|VB|VD|AS|VC)\d*", n):
        return 5
    if b in _DORSAL or re.match(r"^(DA|DB|DD)\d*", n):
        return 6
    if b in _TAIL or n.startswith(("PLM", "PLN", "PVR", "PQR", "PDA", "PDB")):
        return 7
    if b in _RING or n.startswith(tuple(_RING)):
        return 2
    # head interneurons default to ring neighborhood
    if n.startswith(("R", "S", "U", "O", "I")) and len(n) <= 5:
        return 2
    return 0


def place(name: str, rng: np.random.Generator) -> Tuple[float, float]:
    """Return (x,y) in [0,1]² — x anterior→posterior, y dorsal(0)→ventral(1)."""
    rid = classify(name)
    side = _side(name)
    jitter = lambda s: float(rng.normal(0, s))

    if rid == 1:  # sensory / amphid — head, L/R
        x = 0.06 + abs(jitter(0.02))
        y = 0.50 + side * 0.22 + jitter(0.04)
    elif rid == 3:  # pharynx — head center-ventral
        x = 0.12 + jitter(0.02)
        y = 0.58 + jitter(0.05)
    elif rid == 2:  # nerve ring — ellipse around pharynx
        ang = rng.uniform(0, 2 * math.pi)
        x = 0.18 + 0.06 * math.cos(ang) + jitter(0.01)
        y = 0.45 + 0.16 * math.sin(ang) + side * 0.05
    elif rid == 4:  # command — just behind ring
        x = 0.28 + jitter(0.03)
        y = 0.50 + side * 0.12 + jitter(0.03)
    elif rid == 5:  # ventral cord motor — body axis ventral
        # extract number if any for AP position
        m = re.search(r"(\d+)$", name.upper())
        t = (int(m.group(1)) / 12.0) if m else rng.random()
        x = 0.35 + 0.45 * min(1.0, t) + jitter(0.015)
        y = 0.72 + jitter(0.04)
    elif rid == 6:  # dorsal cord
        m = re.search(r"(\d+)$", name.upper())
        t = (int(m.group(1)) / 12.0) if m else rng.random()
        x = 0.35 + 0.45 * min(1.0, t) + jitter(0.015)
        y = 0.22 + jitter(0.04)
    elif rid == 7:  # tail
        x = 0.90 + jitter(0.03)
        y = 0.50 + side * 0.15 + jitter(0.05)
    else:
        x = 0.40 + 0.35 * rng.random()
        y = 0.35 + 0.30 * rng.random()
    return float(np.clip(x, 0.0, 1.0)), float(np.clip(y, 0.0, 1.0))


def build_layout(names: Sequence[str], seed: int = 7) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    names = list(names)
    n = len(names)
    x = np.zeros(n, dtype=np.float32)
    y = np.zeros(n, dtype=np.float32)
    region = np.zeros(n, dtype=np.uint8)
    for i, name in enumerate(names):
        xi, yi = place(name, rng)
        x[i], y[i] = xi, yi
        region[i] = classify(name)
    return {"names": np.array(names, dtype=object), "x": x, "y": y, "region": region}
