from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


EndpointKey = Tuple[int, str]


@dataclass(frozen=True)
class EndpointAnchor:
    edge_index: int
    endpoint: str
    node_id: int
    z: float
    source: str
    edge_key: str = ""
    level_id: str = ""


@dataclass(frozen=True)
class NodeAnchor:
    node_id: int
    z: float
    source: str
    level_id: str = ""


@dataclass(frozen=True)
class FrontierItem:
    kind: str
    z: float
    source: str
    edge_index: Optional[int] = None
    endpoint: str = ""
    node_id: Optional[int] = None
    edge_key: str = ""
    level_id: str = ""


@dataclass(frozen=True)
class AnchorDiscoveryResult:
    known_endpoint_z: Dict[EndpointKey, float] = field(default_factory=dict)
    endpoint_anchors: Dict[EndpointKey, EndpointAnchor] = field(default_factory=dict)
    node_anchors: Dict[int, NodeAnchor] = field(default_factory=dict)
    initial_frontier: List[FrontierItem] = field(default_factory=list)


def _optional_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _level_elevation(model: Any, level_id: Any) -> Optional[float]:
    level_key = str(level_id or "").strip()
    if not level_key:
        return None
    datum = getattr(model, "level_datums", {}).get(level_key)
    if datum is None:
        return None
    return _optional_float(getattr(datum, "elevation_mm", None))


def _edge_key(edge: Any) -> str:
    key = getattr(edge, "key", None)
    if key:
        return str(key)
    a = getattr(edge, "a", None)
    b = getattr(edge, "b", None)
    if a is None or b is None:
        return ""
    try:
        return f"{min(int(a), int(b))}-{max(int(a), int(b))}"
    except Exception:
        return f"{a}-{b}"


def _resolve_edge_endpoint_z(model: Any, edge: Any, endpoint: str) -> Tuple[Optional[float], str, str]:
    if endpoint == "start":
        level_id = str(getattr(edge, "start_level_id", "") or "").strip()
        explicit_z = _optional_float(getattr(edge, "start_z", None))
        if explicit_z is not None:
            return explicit_z, "edge.start_z", level_id
        level_z = _level_elevation(model, level_id)
        if level_z is not None:
            return level_z, "edge.start_level_id", level_id
        return None, "", level_id

    level_id = str(getattr(edge, "end_level_id", "") or "").strip()
    explicit_z = _optional_float(getattr(edge, "end_z", None))
    if explicit_z is not None:
        return explicit_z, "edge.end_z", level_id
    level_z = _level_elevation(model, level_id)
    if level_z is not None:
        return level_z, "edge.end_level_id", level_id
    return None, "", level_id


def discover_elevation_anchors(model: Any) -> AnchorDiscoveryResult:
    """Discover Milestone B elevation anchors without mutating the model.

    Edge start/end elevation metadata is the source of truth. Node.z is
    intentionally ignored; node anchors are derived only from Node.level_id.
    """
    known_endpoint_z: Dict[EndpointKey, float] = {}
    endpoint_anchors: Dict[EndpointKey, EndpointAnchor] = {}
    node_anchors: Dict[int, NodeAnchor] = {}
    initial_frontier: List[FrontierItem] = []

    edges = list(getattr(model, "edges", []) or [])
    for edge_index, edge in enumerate(edges):
        edge_key = _edge_key(edge)
        for endpoint, node_attr in (("start", "a"), ("end", "b")):
            z_value, source, level_id = _resolve_edge_endpoint_z(model, edge, endpoint)
            if z_value is None:
                continue
            node_id = int(getattr(edge, node_attr))
            key = (edge_index, endpoint)
            anchor = EndpointAnchor(
                edge_index=edge_index,
                endpoint=endpoint,
                node_id=node_id,
                z=z_value,
                source=source,
                edge_key=edge_key,
                level_id=level_id,
            )
            known_endpoint_z[key] = z_value
            endpoint_anchors[key] = anchor
            initial_frontier.append(
                FrontierItem(
                    kind="edge_endpoint",
                    edge_index=edge_index,
                    endpoint=endpoint,
                    node_id=node_id,
                    z=z_value,
                    source=source,
                    edge_key=edge_key,
                    level_id=level_id,
                )
            )

    nodes = getattr(model, "nodes", {}) or {}
    for node_id, node in nodes.items():
        level_id = str(getattr(node, "level_id", "") or "").strip()
        z_value = _level_elevation(model, level_id)
        if z_value is None:
            continue
        nid = int(node_id)
        anchor = NodeAnchor(
            node_id=nid,
            z=z_value,
            source="node.level_id",
            level_id=level_id,
        )
        node_anchors[nid] = anchor
        initial_frontier.append(
            FrontierItem(
                kind="node",
                node_id=nid,
                z=z_value,
                source="node.level_id",
                level_id=level_id,
            )
        )

    return AnchorDiscoveryResult(
        known_endpoint_z=known_endpoint_z,
        endpoint_anchors=endpoint_anchors,
        node_anchors=node_anchors,
        initial_frontier=initial_frontier,
    )
