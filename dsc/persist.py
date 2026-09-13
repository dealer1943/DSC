"""Save / load MODEL/active checkpoint (display names only in manifests)."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

from dsc import defaults
from dsc.cells import Population
from dsc.harness import TemporalHarness
from dsc.progress import ProgressCb, emit
from dsc.substrate import Substrate


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_active(
    root: Path,
    sub: Substrate,
    pop: Population,
    harness: TemporalHarness,
    extra: Optional[Dict[str, Any]] = None,
    progress: Optional[ProgressCb] = None,
) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    emit(progress, 0.2, "persist: writing checkpoint.npz")
    path = root / defaults.CHECKPOINT_NAME
    np.savez_compressed(
        path,
        adj=sub.adj,
        gate_logits=pop.gate_logits,
        type_weights=pop.type_weights,
        bias=pop.bias,
        readout=pop.readout,
        utility=pop.utility,
        age=pop.age,
        differentiation=pop.differentiation,
        activity=pop.activity,
        hidden=pop.hidden,
    )
    emit(progress, 0.7, "persist: writing manifest")
    harness_path = root / "harness.json"
    harness_path.write_text(json.dumps(harness.state_dict(), indent=2) + "\n")
    meta = {
        "schema": defaults.SCHEMA_VERSION,
        "kind": "dsc_active",
        "revision": f"r{defaults.SCHEMA_VERSION}-n{sub.n}-e{sub.n_edges}",
        "updated_utc": _utc(),
        "created_utc": _utc(),
        "note": "MVP+evolve: F001–F006/F009 light + F010/F013/F014",
        "pairs_with_features": ["F001", "F002", "F003", "F004", "F005", "F006", "F009", "F010", "F013", "F014"],
        "ui_default": True,
        "substrate": sub.meta,
        "checkpoint": defaults.CHECKPOINT_NAME,
        "harness": "harness.json",
        "display_name": "active",
    }
    if extra:
        meta.update(extra)
    # preserve created_utc if prior manifest exists
    man = root / "manifest.json"
    if man.exists():
        try:
            old = json.loads(man.read_text())
            if "created_utc" in old:
                meta["created_utc"] = old["created_utc"]
        except Exception:
            pass
    man.write_text(json.dumps(meta, indent=2) + "\n")
    emit(progress, 1.0, "persist: saved active")
    return path


def load_active(
    root: Path,
    progress: Optional[ProgressCb] = None,
) -> Tuple[Substrate, Population, TemporalHarness, Dict[str, Any]]:
    root = Path(root)
    emit(progress, 0.05, "load: reading manifest")
    man = json.loads((root / "manifest.json").read_text())
    emit(progress, 0.25, "load: reading checkpoint")
    data = np.load(root / defaults.CHECKPOINT_NAME, allow_pickle=False)
    adj = data["adj"]
    sub = Substrate(adj=adj, meta=dict(man.get("substrate") or {}))
    if "n" not in sub.meta:
        sub.meta.update({"n": int(adj.shape[0]), "n_edges": int(adj.sum()), "density": float(adj.sum() / (adj.shape[0]*(adj.shape[0]-1)))})
    emit(progress, 0.55, "load: restoring population")
    pop = Population(
        gate_logits=data["gate_logits"],
        type_weights=data["type_weights"],
        bias=data["bias"],
        readout=data["readout"],
        utility=data["utility"],
        age=data["age"],
        differentiation=data["differentiation"],
        activity=data["activity"],
        hidden=data["hidden"],
    )
    emit(progress, 0.8, "load: restoring harness")
    harness = TemporalHarness()
    hpath = root / "harness.json"
    if hpath.exists():
        harness.load_state(json.loads(hpath.read_text()))
    emit(progress, 1.0, f"load: ready · {man.get('revision', 'active')}")
    return sub, pop, harness, man



SAVES_DIRNAME = "saves"


def sanitize_model_name(name: Optional[str] = None) -> str:
    """Return a safe basename ending in .model (no paths)."""
    if name is None or not str(name).strip():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"dsc_{stamp}.model"
    raw = str(name).strip()
    # strip any accidental path components — basename only
    raw = Path(raw).name
    stem = raw[:-6] if raw.lower().endswith(".model") else raw
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", stem)
    cleaned = cleaned.strip("._-") or "dsc"
    return f"{cleaned}.model"


def default_model_name() -> str:
    return sanitize_model_name(None)


def save_model_bundle(
    saves_root: Path,
    sub: Substrate,
    pop: Population,
    harness: TemporalHarness,
    name: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    progress: Optional[ProgressCb] = None,
    also_active: Optional[Path] = None,
) -> Path:
    """
    Write a .model zip under saves_root and optionally mirror into also_active/.
    Returns the .model path. Public strings use display basename only.
    """
    saves_root = Path(saves_root)
    saves_root.mkdir(parents=True, exist_ok=True)
    basename = sanitize_model_name(name)
    out = saves_root / basename
    emit(progress, 0.1, f"save: preparing {basename}")

    with tempfile.TemporaryDirectory(prefix="dsc_save_") as tmp:
        tmp_path = Path(tmp)
        save_active(tmp_path, sub, pop, harness, extra=extra, progress=None)
        # stamp display name into manifest
        man_path = tmp_path / "manifest.json"
        man = json.loads(man_path.read_text())
        man["display_name"] = basename
        man["saved_utc"] = _utc()
        man["kind"] = "dsc_model_bundle"
        if extra:
            man.update(extra)
        man_path.write_text(json.dumps(man, indent=2) + "\n")

        emit(progress, 0.55, f"save: packing {basename}")
        if out.exists():
            out.unlink()
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname in (defaults.CHECKPOINT_NAME, "harness.json", "manifest.json"):
                zf.write(tmp_path / fname, arcname=fname)

        if also_active is not None:
            emit(progress, 0.8, "save: updating active tip")
            # copy unpacked tip into active
            also_active = Path(also_active)
            also_active.mkdir(parents=True, exist_ok=True)
            for fname in (defaults.CHECKPOINT_NAME, "harness.json", "manifest.json"):
                shutil.copy2(tmp_path / fname, also_active / fname)

    emit(progress, 1.0, f"save: wrote {basename}")
    return out
