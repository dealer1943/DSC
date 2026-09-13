"""Shared view model + adapter protocol for the operator console."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class NodeView:
    id: str
    label: str
    kind: str = "node"
    activity: float = 0.0
    utility: Optional[float] = None


@dataclass
class EdgeView:
    src: str
    dst: str
    weight: float = 1.0
    meta: str = ""


@dataclass
class ViewModel:
    mode: str
    revision: str
    caption: str
    nodes: List[NodeView] = field(default_factory=list)
    edges: List[EdgeView] = field(default_factory=list)
    signals: Dict[str, List[float]] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    status: Dict[str, Any] = field(default_factory=dict)


class SubstrateAdapter(Protocol):
    name: str
    revision: str

    def capabilities(self) -> Dict[str, bool]:
        ...

    def status(self) -> Dict[str, Any]:
        ...

    def snapshot(self) -> ViewModel:
        ...

    def focus(self, query: str) -> List[str]:
        ...

    def request(self, verb: str, args: List[str]) -> List[str]:
        ...
