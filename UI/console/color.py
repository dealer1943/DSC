"""Signal color scale — anchors come from the active Textual theme."""
from __future__ import annotations

from typing import Tuple

# Defaults match dsc-violet (overwritten on theme apply)
BLUE = (59, 130, 246)
PURPLE = (168, 85, 247)
RED = (239, 68, 68)


def _parse_hex(h: str) -> Tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def set_signal_anchors(low_hex: str, mid_hex: str, high_hex: str) -> None:
    """Called when the operator Menu theme changes."""
    global BLUE, PURPLE, RED
    BLUE = _parse_hex(low_hex)
    PURPLE = _parse_hex(mid_hex)
    RED = _parse_hex(high_hex)


def _lerp(a: Tuple[int, int, int], b: Tuple[int, int, int], u: float) -> Tuple[int, int, int]:
    return tuple(int(round(x + (y - x) * u)) for x, y in zip(a, b))  # type: ignore[return-value]


def signal_rgb(level: float) -> Tuple[int, int, int]:
    t = 0.0 if level < 0 else 1.0 if level > 1 else float(level)
    if t < 0.5:
        return _lerp(BLUE, PURPLE, t * 2.0)
    return _lerp(PURPLE, RED, (t - 0.5) * 2.0)


def rgb_hex(level: float) -> str:
    r, g, b = signal_rgb(level)
    return f"#{r:02x}{g:02x}{b:02x}"


def markup_fg(text: str, level: float) -> str:
    return f"[{rgb_hex(level)}]{text}[/]"


def legend_text() -> str:
    return (
        f"{markup_fg('██ low', 0.08)}  "
        f"{markup_fg('██ mid', 0.5)}  "
        f"{markup_fg('██ high', 0.95)}"
    )


# Prefer legend_text() at call sites; LEGEND kept for older imports (refresh on theme)
LEGEND = legend_text()


def refresh_legend() -> None:
    global LEGEND
    LEGEND = legend_text()
