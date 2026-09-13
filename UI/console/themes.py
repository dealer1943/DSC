"""DSC operator themes — map Textual themes to visible chrome + signal scale."""
from __future__ import annotations

from typing import Dict, Tuple

from textual.theme import Theme

# (low, mid, high) hex for activity / sparklines
SignalAnchors = Tuple[str, str, str]


def _hex(c: str | None, fallback: str) -> str:
    if not c:
        return fallback
    c = c.strip()
    if not c.startswith("#"):
        return fallback
    return c


def anchors_from_theme(theme: Theme) -> SignalAnchors:
    """Every visible signal color comes from the active theme."""
    v = theme.variables or {}
    low = _hex(v.get("signal-low") or theme.secondary, "#3b82f6")
    mid = _hex(v.get("signal-mid") or theme.accent or theme.primary, "#a855f7")
    high = _hex(v.get("signal-high") or theme.error, "#ef4444")
    return low, mid, high


def dsc_themes() -> Dict[str, Theme]:
    """Named themes where signal-low/mid/high are explicit and chrome matches."""
    return {
        "dsc-violet": Theme(
            name="dsc-violet",
            primary="#7c3aed",
            secondary="#3b82f6",
            accent="#a855f7",
            error="#ef4444",
            warning="#f59e0b",
            success="#22c55e",
            foreground="#f5f3ff",
            background="#0b0614",
            surface="#1a0b2e",
            panel="#10081f",
            dark=True,
            variables={
                "signal-low": "#3b82f6",
                "signal-mid": "#a855f7",
                "signal-high": "#ef4444",
            },
        ),
        "dsc-ocean": Theme(
            name="dsc-ocean",
            primary="#0ea5e9",
            secondary="#0369a1",
            accent="#22d3ee",
            error="#f43f5e",
            warning="#fbbf24",
            success="#34d399",
            foreground="#e0f2fe",
            background="#020617",
            surface="#0c4a6e",
            panel="#082f49",
            dark=True,
            variables={
                "signal-low": "#38bdf8",
                "signal-mid": "#818cf8",
                "signal-high": "#fb7185",
            },
        ),
        "dsc-ember": Theme(
            name="dsc-ember",
            primary="#f97316",
            secondary="#b45309",
            accent="#fb923c",
            error="#dc2626",
            warning="#facc15",
            success="#84cc16",
            foreground="#fff7ed",
            background="#1c1917",
            surface="#292524",
            panel="#44403c",
            dark=True,
            variables={
                "signal-low": "#fbbf24",
                "signal-mid": "#f97316",
                "signal-high": "#ef4444",
            },
        ),
        "dsc-mono": Theme(
            name="dsc-mono",
            primary="#a1a1aa",
            secondary="#71717a",
            accent="#d4d4d8",
            error="#fafafa",
            warning="#a1a1aa",
            success="#e4e4e7",
            foreground="#fafafa",
            background="#09090b",
            surface="#18181b",
            panel="#27272a",
            dark=True,
            variables={
                "signal-low": "#52525b",
                "signal-mid": "#a1a1aa",
                "signal-high": "#fafafa",
            },
        ),
    }
