from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .elevation_anchor import AnchorDiscoveryResult, discover_elevation_anchors


EndpointKey = Tuple[int, str]


@dataclass(frozen=True)
class TopologyEndpoint:
    edge_index: int
    endpoint: str
    node_id: int
    edge_key: str = ""


@dataclass(frozen=True)
class WavefrontNode:
    seed_kind: str
    seed_node_id: int
    degree: int
    source: str
    seed_edge_index: Optional[int] = None
    seed_endpoint: str = ""
    source_z: Optional[float] = None


@dataclass(frozen=True)
class CandidatePropagationPath:
    source_kind: str
    source_node_id: int
    target_edge_index: int
    target_endpoint: str
    target_node_id: int
    degree: int
    reason: str
    source: str
    source_edge_index: Optional[int] = None
    source_endpoint: str = ""
    source_z: Optional[float] = None


@dataclass(frozen=True)
class SkippedWavefrontItem:
    seed_kind: str
    seed_node_id: Optional[int]
    reason: str
    degree: Optional[int] = None
    seed_edge_index: Optional[int] = None
    seed_endpoint: str = ""


@dataclass(frozen=True)
class ElevationWavefrontResult:
    b1_result: AnchorDiscoveryResult
    known_endpoint_z: Dict[EndpointKey, float] = field(default_factory=dict)
    wavefront_nodes: List[WavefrontNode] = field(default_factory=list)
    candidate_paths: List[CandidatePropagationPath] = field(default_factory=list)
    skipped: List[SkippedWavefrontItem] = field(default_factory=list)


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


def _endpoint_node(edge: Any, endpoint: str) -> Optional[int]:
    attr = "a" if endpoint == "start" else "b"
    value = getattr(edge, attr, None)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _topology_by_node(model: Any) -> Dict[int, List[TopologyEndpoint]]:
    topology: Dict[int, List[TopologyEndpoint]] = {}
    edges = list(getattr(model, "edges", []) or [])
    for edge_index, edge in enumerate(edges):
        edge_key = _edge_key(edge)
        for endpoint in ("start", "end"):
            node_id = _endpoint_node(edge, endpoint)
            if node_id is None:
                continue
            topology.setdefault(node_id, []).append(
                TopologyEndpoint(
                    edge_index=edge_index,
                    endpoint=endpoint,
                    node_id=node_id,
                    edge_key=edge_key,
                )
            )
    return topology


def build_elevation_wavefront(model: Any) -> ElevationWavefrontResult:
    """Build B2 read-only topology candidates from B1 anchors.

    This function intentionally does not mutate the model, assign endpoint
    elevations, resolve conflicts, or calculate new elevation values.
    """
    b1_result = discover_elevation_anchors(model)
    known_endpoint_z = dict(b1_result.known_endpoint_z)
    topology = _topology_by_node(model)
    wavefront_nodes: List[WavefrontNode] = []
    candidate_paths: List[CandidatePropagationPath] = []
    skipped: List[SkippedWavefrontItem] = []

    for seed in b1_result.initial_frontier:
        seed_node_id = seed.node_id
        if seed_node_id is None:
            skipped.append(
                SkippedWavefrontItem(
                    seed_kind=seed.kind,
                    seed_node_id=None,
                    reason="missing_seed_node",
                    seed_edge_index=seed.edge_index,
                    seed_endpoint=seed.endpoint,
                )
            )
            continue

        endpoints = topology.get(int(seed_node_id), [])
        degree = len(endpoints)
        if degree == 0:
            skipped.append(
                SkippedWavefrontItem(
                    seed_kind=seed.kind,
                    seed_node_id=int(seed_node_id),
                    reason="degree_0",
                    degree=degree,
                    seed_edge_index=seed.edge_index,
                    seed_endpoint=seed.endpoint,
                )
            )
            continue

        wavefront_nodes.append(
            WavefrontNode(
                seed_kind=seed.kind,
                seed_node_id=int(seed_node_id),
                degree=degree,
                source=seed.source,
                seed_edge_index=seed.edge_index,
                seed_endpoint=seed.endpoint,
                source_z=seed.z,
            )
        )

        if degree > 2:
            skipped.append(
                SkippedWavefrontItem(
                    seed_kind=seed.kind,
                    seed_node_id=int(seed_node_id),
                    reason="degree_gt_2",
                    degree=degree,
                    seed_edge_index=seed.edge_index,
                    seed_endpoint=seed.endpoint,
                )
            )
            continue

        for target in endpoints:
            target_key = (target.edge_index, target.endpoint)
            is_source_endpoint = (
                seed.kind == "edge_endpoint"
                and seed.edge_index == target.edge_index
                and seed.endpoint == target.endpoint
            )
            if is_source_endpoint:
                continue
            if target_key in known_endpoint_z:
                skipped.append(
                    SkippedWavefrontItem(
                        seed_kind=seed.kind,
                        seed_node_id=int(seed_node_id),
                        reason="target_already_known",
                        degree=degree,
                        seed_edge_index=seed.edge_index,
                        seed_endpoint=seed.endpoint,
                    )
                )
                continue

            candidate_paths.append(
                CandidatePropagationPath(
                    source_kind=seed.kind,
                    source_node_id=int(seed_node_id),
                    source_edge_index=seed.edge_index,
                    source_endpoint=seed.endpoint,
                    source_z=seed.z,
                    target_edge_index=target.edge_index,
                    target_endpoint=target.endpoint,
                    target_node_id=target.node_id,
                    degree=degree,
                    reason="degree_le_2_adjacent_unknown_endpoint",
                    source=seed.source,
                )
            )

    return ElevationWavefrontResult(
        b1_result=b1_result,
        known_endpoint_z=known_endpoint_z,
        wavefront_nodes=wavefront_nodes,
        candidate_paths=candidate_paths,
        skipped=skipped,
    )
