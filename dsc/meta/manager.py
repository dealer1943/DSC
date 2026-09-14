"""R001 light — external assay logger (not in-loop cell).

Appends one JSONL row per bench/dev_run. Does not mutate population utility.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LOG = Path("BENCHMARKS/meta/r001_assay_log.jsonl")

_ABS_PATH = re.compile(
    r"(?:/Users/|/home/|/workspace/|/var/|/opt/|/tmp/|/private/|[A-Za-z]:\\|\\\\)"
)
_HOSTISH = re.compile(r"\b[\w-]+\.(?:local|lan|internal)\b", re.I)


def append_row(
    kind: str,
    payload: dict[str, Any],
    log_path: Path | None = None,
) -> Path:
    path = Path(log_path or DEFAULT_LOG)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kind": kind,
        **payload,
    }
    scrubbed = _scrub(row)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(scrubbed, default=_json_default) + "\n")
    return path


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Path):
        return obj.name
    return str(type(obj).__name__)


def _scrub_str(s: str) -> str:
    s = _HOSTISH.sub("[host]", s)
    if _ABS_PATH.search(s) or ("/" in s and s.startswith("/")) or "\\" in s:
        # keep basename-ish last segment
        try:
            return Path(s.replace("\\", "/")).name or "[path]"
        except Exception:
            return "[path]"
    return s


def _scrub(obj: Any) -> Any:
    if isinstance(obj, Path):
        return obj.name
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_scrub(x) for x in obj]
    if isinstance(obj, str):
        return _scrub_str(obj)
    return obj
