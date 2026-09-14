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
        if focus is None:
            parts.append(markup_hex(ch, _hex_pulse(hex_c, wave)))
        elif _fly_glyph_hit(focus, ch):
            # focused region: brighter pulse
            parts.append(markup_hex(ch, _hex_pulse(hex_c, 0.55 + 0.45 * wave)))
        else:
            parts.append(markup_fg(ch, 0.10 + 0.06 * wave))
    return "".join(parts)


def fly_brain_ascii(focus: Optional[str] = None, phase: float = 0.0) -> str:
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
        out.append(_paint_fly_line(padded, focus, phase=phase, row=ri))
    out.append(markup_fg(pad * map_w, 0.05))
    tip = (focus or "all")[: max(1, map_w - 7)]
    out.append(markup_fg(f"focus:{tip}".ljust(map_w), 0.38))
    return "\n".join(out)


# --- C. elegans geometric wiring map ---

# Tokens that can light under /focus → aliases
WORM_TOKENS: Dict[str, Tuple[str, ...]] = {
    "ASHL": ("ASHL", "ASH", "AMPHID", "SENSORY"),
    "ASHR": ("ASHR", "ASH", "AMPHID", "SENSORY"),
    "ASEL": ("ASEL", "ASE", "AMPHID", "SENSORY"),
    "ASER": ("ASER", "ASE", "AMPHID", "SENSORY"),
    "AWCL": ("AWCL", "AWC", "AMPHID", "SENSORY"),
    "AWCR": ("AWCR", "AWC", "AMPHID", "SENSORY"),
    "RING": ("RING", "NERVE RING", "RI", "RM", "URY", "OLQ", "CEP"),
    "AVAL": ("AVAL", "AVA", "COMMAND"),
    "AVAR": ("AVAR", "AVA", "COMMAND"),
    "AVBL": ("AVBL", "AVB", "COMMAND"),
    "AVBR": ("AVBR", "AVB", "COMMAND"),
    "AVDL": ("AVDL", "AVD", "COMMAND"),
    "AVDR": ("AVDR", "AVD", "COMMAND"),
    "PVCL": ("PVCL", "PVC", "COMMAND", "TAIL"),
    "PVCR": ("PVCR", "PVC", "COMMAND", "TAIL"),
    "VA": ("VA", "MOTOR", "VENTRAL", "MOTOR_V"),
    "VB": ("VB", "MOTOR", "VENTRAL", "MOTOR_V"),
    "VD": ("VD", "MOTOR", "VENTRAL", "MOTOR_V"),
    "DA": ("DA", "MOTOR", "DORSAL", "MOTOR_D"),
    "DB": ("DB", "MOTOR", "DORSAL", "MOTOR_D"),
    "DD": ("DD", "MOTOR", "DORSAL", "MOTOR_D"),
    "AS": ("AS", "MOTOR", "VENTRAL", "MOTOR_V"),
    "PHARYNX": ("PHARYNX", "I1", "I2", "M1", "NSM", "PHARYNGEAL"),
}


def _worm_token_on(focus: Optional[str], token: str) -> bool:
    if not focus:
        return False
    return _any_hit(focus, WORM_TOKENS.get(token, (token,)))


def _w(token: str, focus: Optional[str], idle: float = 0.45) -> str:
    """Paint a named neuron/region token."""
    on = _worm_token_on(focus, token) if focus else True
    if focus is None:
        return markup_fg(token, idle)
    return _hi(token, on, 0.95)


def worm_brain_ascii(focus: Optional[str] = None, phase: float = 0.0) -> str:
    """Geometric C. elegans wiring sketch — head→tail with ring, commands, cords."""
    # Build as plain geometry; substitute painted tokens.
    ash_l = _w("ASHL", focus)
    ase_l = _w("ASEL", focus)
    awc_l = _w("AWCL", focus)
    ash_r = _w("ASHR", focus)
    ase_r = _w("ASER", focus)
    awc_r = _w("AWCR", focus)
    ring = _w("RING", focus)
    aval = _w("AVAL", focus)
    avar = _w("AVAR", focus)
    avbl = _w("AVBL", focus)
    avbr = _w("AVBR", focus)
    avdl = _w("AVDL", focus)
    avdr = _w("AVDR", focus)
    pvcl = _w("PVCL", focus)
    pvcr = _w("PVCR", focus)
    va = _w("VA", focus)
    vb = _w("VB", focus)
    vd = _w("VD", focus)
    da = _w("DA", focus)
    db = _w("DB", focus)
    dd = _w("DD", focus)
    asa = _w("AS", focus)
    phx = _w("PHARYNX", focus)

    # Fixed-width geometric body (~38 cols) for mid-pane
    dim = lambda s: markup_fg(s, 0.28)
    lines = [
        markup_fg("C. elegans  ·  wiring map", 0.55),
        dim("ant.") + " " + dim("─" * 28) + " " + dim("post."),
        "",
        f"  {ash_l} {ase_l}          {ase_r} {ash_r}",
        f"    {awc_l}   \\        /   {awc_r}",
        f"         {dim('╭──')}{ring}{dim('──╮')}",
        f"         {dim('│')}  {phx}   {dim('│')}",
        f"         {dim('╰────┬─────╯')}",
        f"      {aval}─{avar}  {dim('│')}  {avbl}─{avbr}",
        f"      {avdl}─{avdr}  {dim('│')}",
        f"  {dim('═')}{da}{dim('═')}{db}{dim('═')}{dd}{dim('═')}{dim(' dors')}",
        f"  {dim('═')}{va}{dim('═')}{vb}{dim('═')}{vd}{dim('═')}{asa}{dim('═ vent')}",
        f"              {dim('│')}",
        f"           {pvcl}─{pvcr}",
        f"              {dim('▼')} {dim('tail')}",
        "",
        markup_fg(f"focus: {focus or 'all'}  ·  /focus AVAL|amphid|motor|ring", 0.38),
    ]
    return "\n".join(lines)


def biology_panel(
    mode: str,
    focus: Optional[str] = None,
    phase: float = 0.0,
    live_markup: Optional[str] = None,
) -> str:
    """Markup for the mid-row biology pane, or empty to hide.

    FlyWire: prefer F019 live activity field markup when provided.
    """
    del phase  # kept for call-site compatibility
    m = (mode or "").upper()
    if m in ("FLYWIRE", "FLY"):
        if live_markup:
            return live_markup
        return fly_brain_ascii(focus)
    if m in ("OPENWORM", "WORM", "CELEGANS"):
        return worm_brain_ascii(focus)
    return ""


def should_show_biology(mode: str) -> bool:
    return (mode or "").upper() in ("FLYWIRE", "FLY", "OPENWORM", "WORM", "CELEGANS")
