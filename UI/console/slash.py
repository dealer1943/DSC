"""Slash command registry + palette filtering."""
from __future__ import annotations

from typing import List, Tuple

# (verb, help, dsc?, flywire?)
COMMANDS: List[Tuple[str, str, bool, bool]] = [
    ("help", "list commands", True, True),
    ("load", "load: /load dsc|flywire|openworm [path]", True, True),
    ("status", "mode, sizes, focus", True, True),
    ("focus", "narrow canvas: neuropil / id / all", False, True),
    ("stim", "wake live display / drive regions (fly: optic|AL|…) [strength]", True, True),
    ("pulse", "pulse one region: /pulse MB", False, True),
    ("rest", "quiet live display / clear drive (map + neuron list)", True, True),
    ("signal", "list or pin a signal series", True, True),
    ("sample", "live refresh Hz (default 8); e.g. /sample 16", True, True),
    ("tick", "advance DSC n steps", True, False),
    ("save", "checkpoint: /save  or  /save my_name", True, False),
    ("evolve", "evolution cycles: /evolve [n]", True, False),
    ("bench", "run named benchmark", True, False),
    ("rollback", "restore last-good after /evolve", True, False),
    ("export", "dump frame + log under UI/exports/", True, True),
    ("clear", "clear terminal scrollback", True, True),
    ("quit", "exit console", True, True),
]

DEFAULT_SAMPLE_HZ = 8.0
MIN_SAMPLE_HZ = 1.0
MAX_SAMPLE_HZ = 30.0


def all_verbs() -> List[str]:
    return [c[0] for c in COMMANDS]


def palette_lines(prefix: str = "/", mode: str = "EMPTY") -> List[str]:
    """Filter commands for the strip above the input."""
    raw = prefix[1:] if prefix.startswith("/") else prefix
    raw = raw.split()[0] if raw.strip() else ""
    lines = []
    for verb, help_, dsc_ok, fly_ok in COMMANDS:
        if raw and not verb.startswith(raw):
            continue
        if mode in ("FLYWIRE", "OPENWORM") and not fly_ok:
            avail = "· dsc-only"
        elif mode == "DSC" and not dsc_ok:
            avail = "· static-only"
        else:
            avail = ""
        lines.append(f"/{verb:<10} {help_} {avail}".rstrip())
    return lines or ["(no matching commands)"]


def parse(line: str) -> Tuple[str, List[str]]:
    s = line.strip()
    if not s.startswith("/"):
        return "", []
    parts = s[1:].split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]
