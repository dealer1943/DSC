"""F016 — built-in operator tutorial (guided slash beats)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class TutorialStep:
    id: str
    title: str
    lines: Tuple[str, ...]
    # verb that completes this step when the operator runs it (None = advance-only)
    expect_verb: Optional[str] = None
    # optional first arg match (lowercase); None = any args ok
    expect_arg0: Optional[str] = None


STEPS: Tuple[TutorialStep, ...] = (
    TutorialStep(
        id="welcome",
        title="Welcome",
        lines=(
            "DSC operator tutorial (F016) — ~a few minutes.",
            "Banner shows mode: DSC · FLYWIRE · OPENWORM.",
            "This is your instrument rack for the connectome.",
            "Type the hinted command, or /tutorial next to skip a beat.",
        ),
        expect_verb=None,
    ),
    TutorialStep(
        id="load_dsc",
        title="Load DSC",
        lines=(
            "Load the active DSC checkpoint (pack name only — no disk paths here).",
            "Hint: /load dsc",
            "Watch the progress bar (F013). Grid + signals should appear.",
        ),
        expect_verb="load",
        expect_arg0="dsc",
    ),
    TutorialStep(
        id="tick",
        title="Warm ticks",
        lines=(
            "Advance the DSC a few steps and watch err / activity move.",
            "Hint: /tick 8",
            "Note: warm ticks ≠ full evolution training. Non-monotonic err is normal.",
        ),
        expect_verb="tick",
    ),
    TutorialStep(
        id="sample",
        title="Live sample",
        lines=(
            "Speed up the live refresh. Colors go blue → purple → red with level.",
            "Hint: /sample 16",
        ),
        expect_verb="sample",
    ),
    TutorialStep(
        id="save",
        title="Save checkpoint",
        lines=(
            "Keep this session (F014). Optional name: /save my_run",
            "Hint: /save",
        ),
        expect_verb="save",
    ),
    TutorialStep(
        id="stim_rest",
        title="Stim / rest",
        lines=(
            "Wake the live display, then quiet it (I001 semantics).",
            "Hint: /stim   then later /rest",
            "On FlyWire, /stim can take regions (optic, AL, …). On DSC it wakes charts/grid.",
        ),
        expect_verb="stim",
    ),
    TutorialStep(
        id="evolve",
        title="Evolution",
        lines=(
            "Training loop lives here (F006): eval → select → reproduce → mutate.",
            "Hint: /evolve 1   (DSC mode only — stay on /load dsc for this beat)",
            "Use /rollback if a cycle looks bad (F009).",
        ),
        expect_verb="evolve",
    ),
    TutorialStep(
        id="flywire",
        title="FlyWire compare (optional)",
        lines=(
            "Optional: load the offline fly pack for comparison (~20–30 seconds to load).",
            "Hint: /load flywire   — then explore /focus /stim /rest",
            "DSC-only verbs (/tick /evolve /save) will refuse in FLYWIRE mode — that is correct.",
            "Advance this beat yourself after exploring (background load can take a bit).",
            "When finished exploring — or to skip — /tutorial next.",
        ),
        expect_verb=None,  # optional; operator advances manually
    ),
    TutorialStep(
        id="done",
        title="Done",
        lines=(
            "Tutorial complete. /help for the full palette.",
            "Benches live under BENCHMARKS/; features under FEATURES/.",
            "You can re-run anytime with /tutorial.",
        ),
        expect_verb=None,
    ),
)


def step_count() -> int:
    return len(STEPS)


def render_step(index: int) -> List[str]:
    if index < 0 or index >= len(STEPS):
        return ["tutorial: no such step — /tutorial to restart"]
    st = STEPS[index]
    out = [
        f"── tutorial {index + 1}/{len(STEPS)} · {st.title} ──",
        *st.lines,
    ]
    if st.expect_verb:
        hint = f"/{st.expect_verb}"
        if st.expect_arg0:
            hint += f" {st.expect_arg0}"
        out.append(f"(waiting for {hint} · or /tutorial next)")
    else:
        out.append("( /tutorial next to continue )")
    return out


def matches(index: int, verb: str, args: List[str]) -> bool:
    if index < 0 or index >= len(STEPS):
        return False
    st = STEPS[index]
    if not st.expect_verb:
        return False
    if verb != st.expect_verb:
        return False
    if st.expect_arg0 is None:
        return True
    got = (args[0].lower() if args else "")
    # allow aliases for load
    if st.expect_arg0 == "dsc":
        return got in ("dsc", "active", "model")
    if st.expect_arg0 == "flywire":
        return got in ("flywire", "fly", "fw")
    return got == st.expect_arg0
