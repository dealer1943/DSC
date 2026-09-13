"""Headless FlyWire load test for CI / agent shells."""
from __future__ import annotations

import sys
from pathlib import Path

# allow `python -m console.smoke_flywire` from UI/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.flywire_pack import FlyWirePackAdapter


def main() -> int:
    ad = FlyWirePackAdapter()
    lines = ad.load()
    print("LOAD:")
    for ln in lines:
        print(" ", ln)
    if ad._df is None:
        return 1
    print("STATUS:")
    for k, v in ad.status().items():
        print(f"  {k}: {v}")
    print("FOCUS AL:")
    for ln in ad.focus("AL"):
        print(" ", ln)
    vm = ad.snapshot()
    print("SNAPSHOT:")
    print(" ", vm.mode, vm.revision)
    print(" ", vm.caption)
    print(" ", f"nodes={len(vm.nodes)} edges={len(vm.edges)} signals={list(vm.signals)}")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
