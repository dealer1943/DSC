"""F018 — Biology identity maps (FlyWire BRAIN MAP · C. elegans wiring geometry)."""
from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Tuple

from console.color import markup_fg


def _hi(text: str, on: bool, level: float = 0.92) -> str:
    if on:
        return markup_fg(text, level)
    return markup_fg(text, 0.22)


def _any_hit(focus: Optional[str], keys: Iterable[str]) -> bool:
    """Match neuropil focus without false positives (AL ⊄ LATERAL/CENTRAL)."""
    if not focus:
        return False
    f = focus.strip().upper()
    if not f:
        return False
    for raw in keys:
        k = raw.upper()
        if f == k:
            return True
        if k.startswith(f + "_") or f.startswith(k + "_"):
            return True
        if len(f) >= 4 and (f in k or k in f):
            return True
    return False


def markup_hex(text: str, hex_color: str) -> str:
    """Fixed-hex Rich markup (biology region palette)."""
    return f"[{hex_color}]{text}[/]"


# --- FlyWire BRAIN MAP (from iLandsAI flywire_layout atlas, compacted) ---

# Glyph → (hex color, focus aliases)
FLY_GLYPH: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "L": ("#33d6ff", ("L", "OPTIC", "ME", "LO", "LOP", "AME", "OL", "LEFT", "OPTIC_L")),
    "R": ("#27c0b0", ("R", "OPTIC", "ME", "LO", "LOP", "AME", "OL", "RIGHT", "OPTIC_R")),
    "V": ("#b78cff", ("V", "VIS", "VISUAL", "VP", "VC")),
    "C": ("#ffcc33", ("C", "CENTRAL", "CB", "INTRINSIC")),
    "S": ("#ff9900", ("S", "SENSE", "SENSORY")),
    "K": ("#e6e600", ("K", "MB", "MUSHROOM", "CALYX", "PEDUNCLE", "KC", "MBON")),
    "X": ("#ff33cc", ("X", "CX", "CENTRAL COMPLEX", "FB", "EB", "PB", "NO")),
    "N": ("#55ee66", ("N", "AL", "ANTENNAL")),
    "G": ("#ee7722", ("G", "GNG", "TASTE", "GNATHAL", "SOG")),
    "A": ("#52cc52", ("A", "ASCENDING")),
    "D": ("#ff3333", ("D", "DESCENDING")),
    "M": ("#ccee33", ("M", "MOTOR")),
    ".": ("#666666", (".", "OTHER")),
}

FLY_REGIONS = {
    "AL": FLY_GLYPH["N"][1],
    "MB": FLY_GLYPH["K"][1],
    "CX": FLY_GLYPH["X"][1],
    "GNG": FLY_GLYPH["G"][1],
    "OPTIC": ("L", "R", "OPTIC", "ME", "LO", "LOP", "AME", "OL"),
    "ME": ("ME", "MEDULLA", "OPTIC", "L", "R"),
    "LO": ("LO", "LOBULA", "OPTIC"),
}

# Compacted majority atlas (iLandsAI region_atlas_ascii → mid-pane width)
FLY_BRAIN_MAP = (
    " SSSS",
    "LSSSSS",
    "SSSSSSS  LLLL       G S   S      RRRRRRSSS",
    "SSSSSSS LLLLLL      SSCCCSSC   RRRRRRRRRSRR",
    "SSSSSSLLLLLLLLLL  CCSCAAACSCCCRRRRRRRRRRRSR",
    "SSSSSLLLLLLLLLLLLCCCSDAAAADSCCRRRRRRRRRRRSR",
    "LSSSSLLLLLLLLLLVLLSSCCDCCNNCNRRVVRRRRRRRRSSS",
    " SSSSLLLLLLLLLCVVLNNNNC.NNNNNCVRRRRRRRRRRSS",
    "   SSLLLLLLLLVVVVCNNNCCNCNNNNCCVCRRRRRRRRSR",
    "   LSLLLLLLLLLCVVCCNCCCNNNCCCCCCCVRRRRRRRRR",
    "     SSLLLLLLVCCCCKKXXCXCXXXKKCCCVRRRRRSS",
    "     SSSLLLLLCCCCCKKXCCCXXCXKKCCCCCRRRRR",
    "           LCCCCCCKKKCCCCXCKKCKKKCV",
    "             CCCCCKKKKCCCXKKKCKKC",
    "                  CCCC SS",
    "                        S",
)

FLY_LEGEND = "L/R  V  C  S  K=MB  X=CX  N=AL  G"


def _fly_glyph_hit(focus: Optional[str], glyph: str) -> bool:
    if not focus:
        return False
    meta = FLY_GLYPH.get(glyph)
    if not meta:
        return False
    return _any_hit(focus, meta[1])


def _hex_pulse(hex_color: str, level: float) -> str:
    """Scale a region hex toward black by level in [0,1] (live activity feel)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    u = 0.0 if level < 0 else 1.0 if level > 1 else float(level)
    # keep a floor so glyphs never vanish
    u = 0.22 + 0.78 * u
    return f"#{int(r * u):02x}{int(g * u):02x}{int(b * u):02x}"


def _glyph_wave(ch: str, col: int, row: int, phase: float) -> float:
    """Per-cell phase wave — optic lobes / central / MB drift out of sync."""
    seed = (ord(ch) * 17 + col * 13 + row * 29) % 997
    return 0.5 + 0.5 * math.sin(phase * 2.4 + seed * 0.09)


def _paint_fly_line(
    raw: str,
    focus: Optional[str],
    phase: float = 0.0,
    row: int = 0,
    levels: Optional[Dict[str, float]] = None,
) -> str:
    parts: List[str] = []
    nbsp = " "
    for col, ch in enumerate(raw):
        if ch in (" ", nbsp):
            parts.append(nbsp)
            continue
        meta = FLY_GLYPH.get(ch)
        if not meta:
            parts.append(markup_fg(ch, 0.35))
            continue
        hex_c, _ = meta
        wave = _glyph_wave(ch, col, row, phase)
        live = None if not levels else float(levels.get(ch, 0.0))
        if live is not None:
            # neuro-map response: live level dominates, tiny wave for texture
            level = max(0.08, min(1.0, 0.12 + 0.88 * live + 0.08 * wave))
            if focus and not _fly_glyph_hit(focus, ch):
                level *= 0.22
            parts.append(markup_hex(ch, _hex_pulse(hex_c, level)))
        elif focus is None:
            parts.append(markup_hex(ch, _hex_pulse(hex_c, wave)))
        elif _fly_glyph_hit(focus, ch):
            parts.append(markup_hex(ch, _hex_pulse(hex_c, 0.55 + 0.45 * wave)))
        else:
            parts.append(markup_fg(ch, 0.10 + 0.06 * wave))
    return "".join(parts)


def fly_brain_ascii(focus: Optional[str] = None, phase: float = 0.0, levels: Optional[Dict[str, float]] = None) -> str:
    """iLandsAI BRAIN MAP — left mid-row; glyphs pulse with sample phase."""
    map_w = max(len(r) for r in FLY_BRAIN_MAP)
    pad = " "
    out: List[str] = [
        markup_fg("BRAIN MAP".ljust(map_w), 0.55),
        markup_fg(FLY_LEGEND[:map_w].ljust(map_w), 0.32),
        markup_fg(pad * map_w, 0.05),
    ]
    for ri, raw in enumerate(FLY_BRAIN_MAP):
        padded = raw.ljust(map_w).replace(" ", pad)
        out.append(_paint_fly_line(padded, focus, phase=phase, row=ri, levels=levels))
    out.append(markup_fg(pad * map_w, 0.05))
    tip = (focus or "all")[: max(1, map_w - 7)]
    out.append(markup_fg(f"focus:{tip}".ljust(map_w), 0.38))
    return "\n".join(out)


# --- C. elegans body map (OpenWorm-style S-curve glyph atlas) ---
# Inspired by the classic OpenWorm whole-nervous-system render: dense nerve
# ring at the head, longitudinal cords, circumferential “cage”, sparse tail.
# Glyph language mirrors FLY_BRAIN_MAP so the mid-pane feels the same.

WORM_GLYPH: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "S": ("#33d6ff", ("S", "SENSORY", "AMPHID", "ASH", "ASE", "AWC", "ADL", "HEAD")),
    "N": ("#ffcc33", ("N", "RING", "NERVE RING", "RI", "RM", "URY", "OLQ", "CEP")),
    "P": ("#ee9944", ("P", "PHARYNX", "I1", "I2", "M1", "NSM", "PHARYNGEAL")),
    "C": ("#55ee66", ("C", "COMMAND", "AVA", "AVB", "AVD", "AVE", "PVC", "AVAL", "AVAR")),
    "V": ("#b78cff", ("V", "VENTRAL", "MOTOR_V", "MOTOR", "VA", "VB", "VD", "AS", "VC")),
    "D": ("#ff66aa", ("D", "DORSAL", "MOTOR_D", "MOTOR", "DA", "DB", "DD")),
    "T": ("#ff3333", ("T", "TAIL", "PLM", "PLN", "PVR", "PQR", "PDA", "PDB")),
    ".": ("#555555", (".", "OTHER", "CORD", "PROCESS")),
}

WORM_LEGEND = "S sense  N ring  P pharynx  C cmd  V vent  D dors  T tail"

# Anterior (head) LEFT → posterior (tail) RIGHT. ~44 cols, S-curve silhouette
# matching the OpenWorm 3D nervous-system cage (ring dense, cords, taper).
WORM_BODY_MAP = (
    "  SSS.NNN.                                  ",
    " SNNNNNNNNPP.                     ..D..TT   ",
    "SSNNNNNNNNPPPCC.              ..DDDDVVVTTT  ",
    " SNNNNNN.PPCCCCCVV..    ...DDDDDVVVVVV.TT   ",
    "  NNNNN..P.CCCCCVVVVVVVVVVVVVVDDDDDD..T     ",
    "   NN....P..CCCVVVVVVVVVVVVVVVDDDDD...      ",
    "    ......C..VVVVVVVVVVVVVVDDDD.....        ",
    "      ......VVVVVVVVVVVDDD......            ",
    "         .....VVVVVV........                ",
    "             ..........                     ",
)

# Focus token aliases (slash commands) → still light the matching glyphs
WORM_TOKENS: Dict[str, Tuple[str, ...]] = {
    "ASHL": ("ASHL", "ASH", "AMPHID", "SENSORY", "S"),
    "ASHR": ("ASHR", "ASH", "AMPHID", "SENSORY", "S"),
    "ASEL": ("ASEL", "ASE", "AMPHID", "SENSORY", "S"),
    "ASER": ("ASER", "ASE", "AMPHID", "SENSORY", "S"),
    "AWCL": ("AWCL", "AWC", "AMPHID", "SENSORY", "S"),
    "AWCR": ("AWCR", "AWC", "AMPHID", "SENSORY", "S"),
    "RING": ("RING", "NERVE RING", "N", "RI", "RM", "URY", "OLQ", "CEP"),
    "AVAL": ("AVAL", "AVA", "COMMAND", "C"),
    "AVAR": ("AVAR", "AVA", "COMMAND", "C"),
    "AVBL": ("AVBL", "AVB", "COMMAND", "C"),
    "AVBR": ("AVBR", "AVB", "COMMAND", "C"),
    "AVDL": ("AVDL", "AVD", "COMMAND", "C"),
    "AVDR": ("AVDR", "AVD", "COMMAND", "C"),
    "PVCL": ("PVCL", "PVC", "COMMAND", "C", "TAIL", "T"),
    "PVCR": ("PVCR", "PVC", "COMMAND", "C", "TAIL", "T"),
    "VA": ("VA", "MOTOR", "VENTRAL", "MOTOR_V", "V"),
    "VB": ("VB", "MOTOR", "VENTRAL", "MOTOR_V", "V"),
    "VD": ("VD", "MOTOR", "VENTRAL", "MOTOR_V", "V"),
    "DA": ("DA", "MOTOR", "DORSAL", "MOTOR_D", "D"),
    "DB": ("DB", "MOTOR", "DORSAL", "MOTOR_D", "D"),
    "DD": ("DD", "MOTOR", "DORSAL", "MOTOR_D", "D"),
    "AS": ("AS", "MOTOR", "VENTRAL", "MOTOR_V", "V"),
    "PHARYNX": ("PHARYNX", "I1", "I2", "M1", "NSM", "PHARYNGEAL", "P"),
}


def _worm_glyph_hit(focus: Optional[str], glyph: str) -> bool:
    if not focus:
        return False
    meta = WORM_GLYPH.get(glyph)
    if not meta:
        return False
    if _any_hit(focus, meta[1]):
        return True
    # also allow named neuron tokens to light their region glyph
    for _tok, aliases in WORM_TOKENS.items():
        if _any_hit(focus, aliases) and glyph in aliases:
            return True
        if _any_hit(focus, aliases):
            # map token → primary glyph letter if present in aliases
            for a in aliases:
                if len(a) == 1 and a in WORM_GLYPH and a == glyph:
                    return True
    return False


def _paint_worm_line(
    raw: str,
    focus: Optional[str],
    phase: float = 0.0,
    row: int = 0,
    levels: Optional[Dict[str, float]] = None,
) -> str:
    parts: List[str] = []
    for col, ch in enumerate(raw):
        if ch == " " or ch == " ":
            parts.append(ch)
            continue
        meta = WORM_GLYPH.get(ch)
        if not meta:
            parts.append(markup_fg(ch, 0.22))
            continue
        hex_c, _aliases = meta
        wave = _glyph_wave(ch, col, row, phase)
        live = None if not levels else float(levels.get(ch, 0.0))
        if live is not None:
            level = max(0.08, min(1.0, 0.12 + 0.88 * live + 0.08 * wave))
            if focus and not _worm_glyph_hit(focus, ch):
                level *= 0.22
        elif focus:
            level = 0.95 if _worm_glyph_hit(focus, ch) else 0.18
        else:
            level = wave
        parts.append(markup_hex(ch, _hex_pulse(hex_c, level)))
    return "".join(parts)


def worm_brain_ascii(focus: Optional[str] = None, phase: float = 0.0, levels: Optional[Dict[str, float]] = None) -> str:
    """OpenWorm-style C. elegans nervous-system glyph map (fly mid-pane twin)."""
    map_w = max(len(r) for r in WORM_BODY_MAP)
    pad = "\u00a0"
    out: List[str] = [
        markup_fg("WORM MAP".ljust(map_w), 0.55),
        markup_fg(WORM_LEGEND[:map_w].ljust(map_w), 0.32),
        markup_fg(("ant." + " " * (map_w - 8) + "post.")[:map_w].ljust(map_w), 0.28),
        markup_fg(pad * map_w, 0.05),
    ]
    for ri, raw in enumerate(WORM_BODY_MAP):
        padded = raw.ljust(map_w).replace(" ", pad)
        out.append(_paint_worm_line(padded, focus, phase=phase, row=ri, levels=levels))
    out.append(markup_fg(pad * map_w, 0.05))
    tip = (focus or "all")[: max(1, map_w - 7)]
    out.append(markup_fg(f"focus:{tip}".ljust(map_w), 0.38))
    return "\n".join(out)


def biology_panel(
    mode: str,
    focus: Optional[str] = None,
    phase: float = 0.0,
    live_markup: Optional[str] = None,
) -> str:
    """Markup for the mid-row biology pane, or empty to hide.

    Prefer live atlas markup (neuro-map response) when the adapter provides it.
    """
    m = (mode or "").upper()
    if m in ("FLYWIRE", "FLY"):
        if live_markup:
            return live_markup
        return fly_brain_ascii(focus, phase=phase)
    if m in ("OPENWORM", "WORM", "CELEGANS"):
        if live_markup:
            return live_markup
        return worm_brain_ascii(focus, phase=phase)
    return ""


def should_show_biology(mode: str) -> bool:
    return (mode or "").upper() in ("FLYWIRE", "FLY", "OPENWORM", "WORM", "CELEGANS")
