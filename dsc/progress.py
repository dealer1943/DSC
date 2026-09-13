"""Load / build progress reporting (F013)."""
from __future__ import annotations

from typing import Callable, Optional

ProgressCb = Callable[[float, str], None]


def emit(cb: Optional[ProgressCb], frac: float, message: str) -> None:
    if cb is None:
        return
    f = 0.0 if frac < 0 else 1.0 if frac > 1 else float(frac)
    cb(f, message)


class Progress:
    """Simple staged progress helper."""

    def __init__(self, cb: Optional[ProgressCb] = None):
        self.cb = cb

    def __call__(self, frac: float, message: str) -> None:
        emit(self.cb, frac, message)
