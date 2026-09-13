"""ASCII helpers for canvas + sparkline charts (blue→purple→red)."""
from __future__ import annotations

import math
from typing import Dict, List, Optional

from adapters.base import EdgeView, NodeView
from console.color import legend_text, markup_fg

BLOCKS = " ▁▂▃▄▅▆▇█"
GRID_ROWS = 12
GRID_COLS = 12
GRID_SLOTS = GRID_ROWS * GRID_COLS  # 144
# F015: cells 0..127 map row-major into slots; 128..143 empty (true void)
CELL_GLYPH = "●"  # equal visual diameter for every cell
EMPTY_GLYPH = "\u00a0"  # NBSP void — holds column width (plain spaces collapse)
GRID_DISPLAY_WIDTH = GRID_COLS * 2 - 1  # 12 glyphs + 11 spacers = 23


def _clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def rule_line(width: int = 48) -> str:
    """Single-span horizontal rule — avoid per-dash markup (wraps into extra rows)."""
    w = max(8, min(int(width), 56))
    return markup_fg("─" * w, 0.35)


def live_activity(base: float, node_id: str, phase: float) -> float:
    """Pulse activity so the canvas breathes."""
    h = sum(ord(c) for c in node_id[-8:]) % 997
    wave = 0.5 + 0.5 * math.sin(phase * 2.3 + h * 0.07)
    return _clamp01(base * (0.42 + 0.58 * wave) + 0.08 * wave)


def sparkline(values: List[float], width: int = 40, colored: bool = True) -> str:
    if not values:
        return "·" * min(width, 8)
    seq = values[-width:]
    lo, hi = min(seq), max(seq)
    span = (hi - lo) or 1.0
    out = []
    for v in seq:
        u = (v - lo) / span
        idx = int(u * (len(BLOCKS) - 1))
        ch = BLOCKS[idx]
        out.append(markup_fg(ch, u) if colored else ch)
    return "".join(out)


def signal_panel(signals: Dict[str, List[float]], width: int = 42, sample_hz: float = 8.0) -> str:
    head = f"signals  ·  {sample_hz:g} Hz  ·  {legend_text()}"
    if not signals:
        return head + "\n(no signals)"
    lines = [head]
    for name, hist in signals.items():
        last_v = hist[-1] if hist else 0.0
        if hist:
            lo, hi = min(hist), max(hist)
            lvl = 0.5 if hi <= lo else (last_v - lo) / (hi - lo)
        else:
            lvl = 0.0
        last = markup_fg(f"{last_v:.4g}", _clamp01(lvl))
        lines.append(f"{name:<16} {sparkline(hist, width)}  {last}")
    return "\n".join(lines)


def _is_dsc_full_grid(nodes: List[NodeView]) -> bool:
    """True when nodes look like a full DSC population (stable ids 0..N-1)."""
    if len(nodes) < 64:
        return False
    try:
        ids = sorted(int(n.id) for n in nodes)
    except ValueError:
        return False
    return ids == list(range(len(nodes)))



def _empty_slot() -> str:
    """Width-stable empty cell (not a stem). NBSP inside markup so pipes stay aligned."""
    return markup_fg("\u00a0", 0.05)


def cell_grid_body(nodes: List[NodeView], phase: float = 0.0) -> List[str]:
    """12 body rows of equal ● (and void). No caption. Fixed display width."""
    by_id = {int(n.id): n for n in nodes}
    n_cells = len(nodes)
    spacer = markup_fg("\u00a0", 0.05)  # NBSP spacer — won't collapse before │
    rows = []
    for r in range(GRID_ROWS):
        row_parts = []
        for c in range(GRID_COLS):
            slot = r * GRID_COLS + c
            if slot >= n_cells:
                row_parts.append(_empty_slot())
            else:
                node = by_id.get(slot)
                if node is None:
                    row_parts.append(_empty_slot())
                else:
                    act = live_activity(node.activity, node.id, phase)
                    if node.utility is not None:
                        u = _clamp01(0.5 + 0.5 * math.tanh(float(node.utility)))
                        act = _clamp01(0.7 * act + 0.3 * u)
                    row_parts.append(markup_fg(CELL_GLYPH, act))
            if c < GRID_COLS - 1:
                row_parts.append(spacer)
        rows.append("".join(row_parts))
    return rows


def activity_side_list(
    nodes: List[NodeView],
    phase: float = 0.0,
    limit: int = 12,
) -> List[str]:
    """Top activity bars (legacy list) — for the right column."""
    ranked = sorted(nodes, key=lambda n: n.activity, reverse=True)[:limit]
    lines = []
    for n in ranked:
        act = live_activity(n.activity, n.id, phase)
        bar_w = max(1, int(act * 16))
        bar_chars = []
        for i in range(16):
            if i < bar_w:
                lvl = _clamp01(0.15 + act * (0.35 + 0.5 * (i + 1) / 16))
                bar_chars.append(markup_fg("█", lvl))
            else:
                bar_chars.append(markup_fg("·", 0.12))
        label = markup_fg(f"{n.label:>5}", act)
        kind = markup_fg(n.kind[:4], _clamp01(act * 0.7 + 0.15))
        lines.append(f"{label} {''.join(bar_chars)} {kind}")
    while len(lines) < GRID_ROWS:
        lines.append("")
    return lines[:GRID_ROWS]


def cell_grid_panel(
    nodes: List[NodeView],
    caption: str,
    phase: float = 0.0,
    width: int = 72,
) -> List[str]:
    """Caption + legend + 12×12 grid only (no side list)."""
    n_cells = len(nodes)
    lines = [
        caption[:width],
        markup_fg(
            f"cell grid 12×12 · {n_cells} cells · {GRID_SLOTS - n_cells} empty · equal ●",
            0.45,
        ),
        rule_line(48),
    ]
    lines.extend(cell_grid_body(nodes, phase=phase))
    return lines


def dsc_grid_with_side_list(
    nodes: List[NodeView],
    edges: List[EdgeView],
    caption: str,
    phase: float = 0.0,
    width: int = 96,
) -> str:
    """F015 grid on the left, legacy top-activity list on the right."""
    n_cells = len(nodes)
    sep = markup_fg("\u00a0│\u00a0", 0.35)
    lines = [
        caption[:width],
        f"{markup_fg(f'12×12 · {n_cells} cells · 16 empty · equal ●', 0.45)}"
        f"     {legend_text()}",
        rule_line(48),
    ]
    grid_label = markup_fg("grid", 0.5) + markup_fg("\u00a0", 0.05) * (GRID_DISPLAY_WIDTH - 4)
    lines.append(grid_label + sep + markup_fg("top activity", 0.5))

    grid_rows = cell_grid_body(nodes, phase=phase)
    side_rows = activity_side_list(nodes, phase=phase, limit=GRID_ROWS)
    for g, s in zip(grid_rows, side_rows):
        if s:
            lines.append(f"{g}{sep}{s}")
        else:
            lines.append(g)

    lines.append(rule_line(48))
    if edges:
        weights = [e.weight for e in edges]
        wmax = max(weights) or 1.0
        hot = int(phase * 3.1) % max(1, min(len(edges), 6))
        shown = 0
        for i, e in enumerate(edges):
            if shown >= 5:
                lines.append(markup_fg(f"  … +{len(edges) - shown} edges", 0.25))
                break
            lvl = _clamp01(e.weight / wmax)
            if i == hot:
                lvl = _clamp01(lvl * 0.55 + 0.45)
            arrow = markup_fg("→", lvl)
            lines.append(
                f"  {markup_fg(e.src, lvl)} {arrow} {markup_fg(e.dst, lvl)}  "
                f"{markup_fg(e.meta, _clamp01(lvl * 0.8))}"
            )
            shown += 1
    return "\n".join(lines)


def _bar_canvas(
    nodes: List[NodeView],
    edges: List[EdgeView],
    caption: str,
    width: int,
    height: int,
    phase: float,
) -> str:
    """Legacy / FlyWire: top activity bars + edge sample."""
    lines = [
        caption[:width],
        rule_line(48),
    ]
    if not nodes:
        lines.append("(empty canvas)")
        return "\n".join(lines)

    for n in nodes[: max(1, height - 5)]:
        act = live_activity(n.activity, n.id, phase)
        bar_w = max(1, int(act * 24))
        bar_chars = []
        for i in range(24):
            if i < bar_w:
                lvl = _clamp01(0.15 + act * (0.35 + 0.5 * (i + 1) / 24))
                bar_chars.append(markup_fg("█", lvl))
            else:
                bar_chars.append(markup_fg("·", 0.12))
        label = markup_fg(f"{n.label:>8}", act)
        kind = markup_fg(n.kind, _clamp01(act * 0.7 + 0.15))
        lines.append(f"{label} {''.join(bar_chars)}  {kind}")

    lines.append(rule_line(48))
    if edges:
        weights = [e.weight for e in edges]
        wmax = max(weights) or 1.0
        hot = int(phase * 3.1) % max(1, min(len(edges), 8))
        shown = 0
        for i, e in enumerate(edges):
            if shown >= 7:
                lines.append(markup_fg(f"  … +{len(edges) - shown} edges", 0.25))
                break
            lvl = _clamp01(e.weight / wmax)
            if i == hot:
                lvl = _clamp01(lvl * 0.55 + 0.45)
            arrow = markup_fg("→", lvl)
            lines.append(
                f"  {markup_fg(e.src[-6:], lvl)} {arrow} {markup_fg(e.dst[-6:], lvl)}  "
                f"{markup_fg('w=' + f'{e.weight:.0f}', lvl)}  "
                f"{markup_fg(e.meta, _clamp01(lvl * 0.8))}"
            )
            shown += 1
    return "\n".join(lines)


def canvas_panel(
    nodes: List[NodeView],
    edges: List[EdgeView],
    caption: str,
    width: int = 72,
    height: int = 14,
    phase: float = 0.0,
) -> str:
    """
    DSC full population → F015 12×12 equal ● grid (replaces top-K bars).
    FlyWire / partial → activity bars + edge strip.
    """
    if _is_dsc_full_grid(nodes):
        return dsc_grid_with_side_list(nodes, edges, caption, phase=phase, width=max(width, 96))

    return _bar_canvas(nodes, edges, caption, width, height, phase)


def summary_panel(status: dict, phase: float = 0.0) -> str:
    if not status:
        return "(no status)"
    lines = []
    for k, v in status.items():
        if k == "top_neuropils":
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            lvl = 0.35 + 0.25 * (0.5 + 0.5 * math.sin(phase + hash(k) % 13))
            lines.append(f"{k}: {markup_fg(str(v), _clamp01(lvl))}")
        else:
            lines.append(f"{k}: {v}")
    tops = status.get("top_neuropils") or {}
    if tops:
        lines.append("")
        lines.append(markup_fg("top neuropils", 0.55))
        mx = max(tops.values()) if tops else 1
        for name, cnt in tops.items():
            lvl = _clamp01(cnt / mx)
            bar = markup_fg("█" * max(1, int(lvl * 14)), lvl)
            lines.append(f"  {markup_fg(name, lvl)} {bar} {cnt}")
    return "\n".join(lines)
