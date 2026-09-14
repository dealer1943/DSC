"""Textual operator console — F012 (color + live sample)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.command import CommandPalette
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import Footer, Header, Input, ProgressBar, RichLog, Static

from adapters import dsc_runtime, flywire_pack, openworm_pack
from adapters.base import ViewModel
from console.color import legend_text, markup_fg, refresh_legend, set_signal_anchors
from console.themes import anchors_from_theme, dsc_themes
from console.render import canvas_panel, signal_panel, summary_panel
from console.biology import biology_panel, should_show_biology
from console.slash import (
    DEFAULT_SAMPLE_HZ,
    MAX_SAMPLE_HZ,
    MIN_SAMPLE_HZ,
    all_verbs,
    palette_lines,
    parse,
)

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"


class Banner(Static):
    def set_mode(self, mode: str, revision: str, extra: str = "", hz: float = 8.0) -> None:
        hz_bit = markup_fg(f"{hz:g} Hz", min(1.0, hz / 16.0))
        self.update(f" {markup_fg(mode, 0.7)}  ·  {revision}  {extra}  ·  sample {hz_bit}")


class OperatorConsole(App):
    # Ctrl+P system UI — call it Menu, not Palette
    ENABLE_COMMAND_PALETTE = True
    COMMAND_PALETTE_BINDING = "ctrl+p"
    COMMAND_PALETTE_DISPLAY = "Menu"
    CSS = """
    Screen {
        layout: vertical;
        background: $background;
        color: $foreground;
    }
    Header {
        background: $surface;
        color: $foreground;
    }
    Footer {
        background: $surface;
        color: $foreground;
    }
    #banner {
        dock: top;
        height: 1;
        background: $primary;
        color: $foreground;
        text-style: bold;
    }
    #main { height: 1fr; layout: vertical; }
    #midrow { height: 1fr; }
    #biology {
        width: 52;
        min-width: 52;
        border: tall $accent;
        padding: 0 1;
        background: $surface;
        color: $foreground;
        display: none;
        overflow-x: hidden;
        overflow-y: auto;
    }
    #biology.visible { display: block; }
    #canvas {
        width: 2fr;
        min-width: 28;
        border: tall $primary;
        padding: 0 1;
        background: $panel;
        color: $foreground;
        overflow-x: hidden;
    }
    #side {
        width: 3fr;
        min-width: 44;
        overflow-x: hidden;
    }
    #signals {
        height: 1fr;
        border: tall $secondary;
        padding: 0 1;
        background: $surface;
        color: $foreground;
        overflow-x: hidden;
    }
    #summary {
        height: 1fr;
        border: tall $accent;
        padding: 0 1;
        background: $panel;
        color: $foreground;
        overflow-x: hidden;
    }
    #terminal {
        height: 10;
        border: tall $error;
        background: $background;
        color: $foreground;
    }
    #slashmenu {
        height: auto;
        max-height: 8;
        background: $surface;
        color: $foreground;
        display: none;
        padding: 0 1;
        border-top: solid $primary;
    }
    #slashmenu.visible { display: block; }
    #loadprog {
        height: 3;
        display: none;
        background: $surface;
        padding: 0 1;
        border-top: solid $secondary;
    }
    #loadprog.visible { display: block; }
    #loadmsg { color: $foreground; height: 1; }
    #cmdline {
        dock: bottom;
        height: 3;
        background: $background;
        padding: 0 1;
    }
    Input {
        width: 1fr;
        background: $surface;
        color: $foreground;
        border: tall $accent;
    }
    Input:focus {
        border: tall $error;
    }
    CommandPalette {
        background: $background 80%;
    }
    CommandPalette #--input {
        background: $surface;
        border: tall $primary;
    }
    CommandPalette #--results {
        background: $panel;
        border: tall $secondary;
    }
    """

    TITLE = "DSC Operator Console"
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("escape", "clear_slash_menu", "Esc", show=False),
        Binding("slash", "open_slash_cmd", "/", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.adapter: Any = None
        self.mode = "EMPTY"
        self._term_lines: List[str] = []
        self.sample_hz = DEFAULT_SAMPLE_HZ
        self._phase = 0.0
        self._sample_timer: Optional[Timer] = None
        self._last_vm: Optional[ViewModel] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Banner(
            f" EMPTY  ·  /load flywire  ·  {legend_text()} ",
            id="banner",
        )
        with Vertical(id="main"):
            with Horizontal(id="midrow"):
                yield Static("", id="biology", markup=True)
                yield Static("(canvas)", id="canvas", markup=True)
                with Vertical(id="side"):
                    yield Static("(signals)", id="signals", markup=True)
                    yield Static("(summary)", id="summary", markup=True)
        yield RichLog(id="terminal", highlight=True, markup=True, wrap=True)
        yield Static(id="slashmenu", markup=True)
        with Vertical(id="loadprog"):
            yield Static("", id="loadmsg", markup=True)
            yield ProgressBar(total=100, show_eta=False, id="loadbar")
        with Horizontal(id="cmdline"):
            yield Input(
                placeholder="/load dsc|flywire|openworm   ·   /sample 16   ·   / for commands",
                id="cmd",
            )
        yield Footer()

    def on_mount(self) -> None:
        for th in dsc_themes().values():
            self.register_theme(th)
        # default DSC look
        if "dsc-violet" in self.available_themes:
            self.theme = "dsc-violet"
        self._apply_theme_signals()
        # Keep / from getting eaten by the scrollback log
        self.query_one("#terminal", RichLog).can_focus = False
        self.query_one("#cmd", Input).focus()
        self._term("operator console ready · F012 · Ctrl+P opens Menu (themes apply to chrome + signals)")
        self._term(f"live sample {self.sample_hz:g} Hz — /sample 16 for faster pulse")
        self._term("try: /load dsc  ·  /load flywire  ·  /load openworm")
        self._refresh_slash_menu("")
        self._arm_sampler()

    def watch_theme(self, theme_name: str) -> None:
        self._apply_theme_signals()
        if self._last_vm is not None:
            self._paint(self._last_vm, phase=self._phase, quiet=True)
        # skip boot chatter; only announce interactive Menu picks
        if getattr(self, "_theme_boot_done", False):
            self._term(f"menu theme → {theme_name}")
            self.call_after_refresh(self._focus_cmd)
        else:
            self._theme_boot_done = True

    def _apply_theme_signals(self) -> None:
        theme = self.current_theme
        low, mid, high = anchors_from_theme(theme)
        set_signal_anchors(low, mid, high)
        refresh_legend()

    def action_command_palette(self) -> None:
        """Ctrl+P opens Menu (not "palette")."""
        if self.use_command_palette and not CommandPalette.is_open(self):
            self.push_screen(
                CommandPalette(
                    placeholder="Menu — theme, keys, quit…",
                    id="--command-palette",
                )
            )


    def _arm_sampler(self) -> None:
        if self._sample_timer is not None:
            self._sample_timer.stop()
        interval = 1.0 / max(MIN_SAMPLE_HZ, min(MAX_SAMPLE_HZ, self.sample_hz))
        self._sample_timer = self.set_interval(interval, self._on_sample)

    def _on_sample(self) -> None:
        if self.adapter is None:
            return
        self._phase += 1.0 / self.sample_hz
        sample_frame = getattr(self.adapter, "sample_frame", None)
        if callable(sample_frame):
            sample_frame(self._phase)
        self._last_vm = self.adapter.snapshot()
        self._paint(self._last_vm, phase=self._phase, quiet=True)

    def _banner(self) -> Banner:
        return self.query_one("#banner", Banner)

    def _term(self, line: str) -> None:
        self._term_lines.append(line)
        self.query_one("#terminal", RichLog).write(line)

    def _refresh_slash_menu(self, text: str) -> None:
        pal = self.query_one("#slashmenu", Static)
        if text.startswith("/"):
            pal.add_class("visible")
            # color verbs lightly
            lines = []
            for i, line in enumerate(palette_lines(text, self.mode)):
                lvl = 0.25 + 0.08 * (i % 6)
                lines.append(markup_fg(line, lvl))
            pal.update("\n".join(lines))
        else:
            pal.remove_class("visible")
            pal.update("")

    def action_clear_slash_menu(self) -> None:
        inp = self.query_one("#cmd", Input)
        if inp.value.startswith("/"):
            inp.value = ""
        self._refresh_slash_menu("")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        # When the cmd Input already has focus, let "/" type normally
        if action == "open_slash_cmd" and isinstance(self.focused, Input):
            return False
        return True

    def action_open_slash_cmd(self) -> None:
        """Global / — focus the command box and open the slash menu."""
        inp = self.query_one("#cmd", Input)
        inp.focus()
        inp.value = "/"
        inp.cursor_position = 1
        self._refresh_slash_menu("/")

    def _focus_cmd(self) -> None:
        self.query_one("#cmd", Input).focus()

    @on(CommandPalette.Closed)
    def on_menu_closed(self, event: CommandPalette.Closed) -> None:
        self._focus_cmd()

    def _paint(self, vm: ViewModel, phase: float = 0.0, quiet: bool = False) -> None:
        self.mode = vm.mode
        self._banner().set_mode(
            vm.mode,
            vm.revision,
            f"· {vm.caption[:48]}",
            hz=self.sample_hz,
        )
        self.query_one("#canvas", Static).update(
            canvas_panel(vm.nodes, vm.edges, vm.caption, phase=phase)
        )
        bio = self.query_one("#biology", Static)
        focus = None
        if isinstance(vm.status, dict):
            focus = vm.status.get("focus")
        if should_show_biology(vm.mode):
            bio.add_class("visible")
            live = None
            if self.adapter is not None and hasattr(self.adapter, "brain_map_markup"):
                live = self.adapter.brain_map_markup(
                    focus=focus if isinstance(focus, str) else None
                ) or None
            bio.update(
                biology_panel(
                    vm.mode,
                    focus=focus if isinstance(focus, str) else None,
                    phase=phase,
                    live_markup=live,
                )
            )
        else:
            bio.remove_class("visible")
            bio.update("")
        self.query_one("#signals", Static).update(
            signal_panel(vm.signals, width=28, sample_hz=self.sample_hz)
        )
        self.query_one("#summary", Static).update(summary_panel(vm.status, phase=phase))
        if quiet:
            return
        if vm.events and (not self._term_lines or vm.events[-1] != self._term_lines[-1]):
            self._term(vm.events[-1])

    def _ensure_export_dir(self) -> Path:
        EXPORTS.mkdir(parents=True, exist_ok=True)
        return EXPORTS

    def _export(self) -> List[str]:
        if self.adapter is None:
            return ["refuse: nothing loaded"]
        vm = self.adapter.snapshot()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = self._ensure_export_dir() / f"export_{vm.mode}_{ts}.json"
        payload = {
            "mode": vm.mode,
            "revision": vm.revision,
            "caption": vm.caption,
            "status": vm.status,
            "signals": vm.signals,
            "sample_hz": self.sample_hz,
            "terminal_tail": self._term_lines[-100:],
            "canvas_nodes": [n.__dict__ for n in vm.nodes],
            "canvas_edges": [e.__dict__ for e in vm.edges],
        }
        out.write_text(json.dumps(payload, indent=2))
        return [f"exported {out}"]

    def _set_sample(self, args: List[str]) -> None:
        if not args:
            self._term(f"sample rate: {self.sample_hz:g} Hz (default {DEFAULT_SAMPLE_HZ:g})")
            return
        try:
            hz = float(args[0])
        except ValueError:
            self._term("usage: /sample [hz]  e.g. /sample 16")
            return
        if hz < MIN_SAMPLE_HZ or hz > MAX_SAMPLE_HZ:
            self._term(f"refuse: hz must be in [{MIN_SAMPLE_HZ:g}, {MAX_SAMPLE_HZ:g}]")
            return
        self.sample_hz = hz
        self._arm_sampler()
        self._term(markup_fg(f"sample rate → {hz:g} Hz", min(1.0, hz / 16.0)))
        if self._last_vm is not None:
            self._paint(self._last_vm, phase=self._phase, quiet=True)


    def _show_progress(self, frac: float, message: str) -> None:
        box = self.query_one("#loadprog", Vertical)
        box.add_class("visible")
        bar = self.query_one("#loadbar", ProgressBar)
        bar.update(progress=max(0, min(100, frac * 100)))
        # colorize message by progress level
        lvl = max(0.0, min(1.0, frac))
        self.query_one("#loadmsg", Static).update(markup_fg(f"{frac*100:5.1f}%  {message}", lvl))
        self.refresh()

    def _hide_progress(self) -> None:
        box = self.query_one("#loadprog", Vertical)
        box.remove_class("visible")
        self.query_one("#loadmsg", Static).update("")
        try:
            self.query_one("#loadbar", ProgressBar).update(progress=0)
        except Exception:
            pass

    def _dispatch(self, verb: str, args: List[str]) -> None:
        if verb == "help":
            for line in palette_lines("/", self.mode):
                self._term(line)
            self._term(f"color: {legend_text()}")
            return
        if verb == "quit":
            self.exit()
            return
        if verb == "sample":
            self._set_sample(args)
            return
        if verb == "export":
            for line in self._export():
                self._term(line)
            return
        if verb == "load":
            kind = (args[0].lower() if args else "")
            rest = args[1:]
            if kind not in ("flywire", "fly", "fw", "dsc", "active", "model", "openworm", "worm", "celegans", "c302"):
                self._term("usage: /load flywire|dsc|openworm [path]")
                return

            def on_prog(frac: float, message: str) -> None:
                self._show_progress(frac, message)

            self._show_progress(0.0, "starting load…")
            lines = []
            try:
                if kind in ("flywire", "fly", "fw"):
                    pack = rest[0] if rest else None
                    self.adapter = flywire_pack.create(pack)
                    self.adapter.set_progress(on_prog)
                    lines = self.adapter.load(pack)
                elif kind in ("openworm", "worm", "celegans", "c302"):
                    pack = rest[0] if rest else None
                    self.adapter = openworm_pack.create(pack)
                    self.adapter.set_progress(on_prog)
                    lines = self.adapter.load(pack)
                else:
                    path = rest[0] if rest else None
                    self.adapter = dsc_runtime.create(path)
                    self.adapter.set_progress(on_prog)
                    lines = self.adapter.load(path)
            except Exception as exc:
                self._term(f"load failed: {exc}")
                self._hide_progress()
                return
            finally:
                if lines:
                    self._show_progress(1.0, "done")
                    self.set_timer(0.6, self._hide_progress)

            for line in lines:
                self._term(line)
            self._phase = 0.0
            self._last_vm = self.adapter.snapshot()
            self._paint(self._last_vm, phase=self._phase)
            return

        if self.adapter is None:
            self._term("nothing loaded — /load flywire  or  /load dsc")
            return

        lines = self.adapter.request(verb, args)
        for line in lines:
            self._term(line)
        self._last_vm = self.adapter.snapshot()
        self._paint(self._last_vm, phase=self._phase)

    @on(Input.Changed, "#cmd")
    def on_input_changed(self, event: Input.Changed) -> None:
        self._refresh_slash_menu(event.value)

    @on(Input.Submitted, "#cmd")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        event.input.value = ""
        self._refresh_slash_menu("")
        if not raw:
            return
        if not raw.startswith("/"):
            self._term(f"(not a command) {raw} — commands start with /")
            return
        verb, args = parse(raw)
        if not verb:
            self._term("empty command")
            return
        if verb not in all_verbs():
            self._term(f"unknown /{verb} — /help")
            return
        self._dispatch(verb, args)


def run() -> None:
    OperatorConsole().run()
