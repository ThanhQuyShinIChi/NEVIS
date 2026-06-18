from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .elevation_anchor import EndpointAnchor, NodeAnchor
from .elevation_candidate import CandidateEvaluationResult, evaluate_elevation_candidates
from .elevation_wavefront import CandidatePropagationPath


EndpointKey = Tuple[int, str]


@dataclass(frozen=True)
class AnchorConflictItem:
    kind: str
    node_id: int
    z: float
    source: str
    edge_index: int | None = None
    endpoint: str = ""
    level_id: str = ""


@dataclass(frozen=True)
class AnchorConflictReport:
    node_id: int
    reason: str
    items: List[AnchorConflictItem] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateConflictReport:
    target_edge_index: int
    target_endpoint: str
    reason: str
    candidates: List[CandidatePropagationPath] = field(default_factory=list)


@dataclass(frozen=True)
class LockConditionReport:
    edge_index: int
    role: str
    reason: str
    candidate: CandidatePropagationPath | None = None


@dataclass(frozen=True)
class ConflictLockResult:
    evaluation_result: CandidateEvaluationResult
    known_endpoint_z: Dict[EndpointKey, float] = field(default_factory=dict)
    anchor_conflicts: List[AnchorConflictReport] = field(default_factory=list)
    candidate_conflicts: List[CandidateConflictReport] = field(default_factory=list)
    lock_conditions: List[LockConditionReport] = field(default_factory=list)


def _edge_at(model: Any, edge_index: int | None) -> Any | None:
    if edge_index is None:
        return None
    edges = list(getattr(model, "edges", []) or [])
    if edge_index < 0 or edge_index >= len(edges):
        return None
    return edges[edge_index]


def _is_locked(model: Any, edge_index: int | None) -> bool:
    edge = _edge_at(model, edge_index)
    return bool(getattr(edge, "elevation_locked", False)) if edge is not None else False


def _anchor_conflict_item_from_endpoint(anchor: EndpointAnchor) -> AnchorConflictItem:
    return AnchorConflictItem(
        kind="edge_endpoint",
        node_id=anchor.node_id,
        z=anchor.z,
        source=anchor.source,
        edge_index=anchor.edge_index,
        endpoint=anchor.endpoint,
        level_id=anchor.level_id,
    )


def _anchor_conflict_item_from_node(anchor: NodeAnchor) -> AnchorConflictItem:
    return AnchorConflictItem(
        kind="node",
        node_id=anchor.node_id,
        z=anchor.z,
        source=anchor.source,
        level_id=anchor.level_id,
    )


def _detect_anchor_conflicts(
    evaluation_result: CandidateEvaluationResult,
) -> List[AnchorConflictReport]:
    b1_result = evaluation_result.b2_result.b1_result
    anchors_by_node: Dict[int, List[AnchorConflictItem]] = {}

    for anchor in b1_result.endpoint_anchors.values():
        anchors_by_node.setdefault(anchor.node_id, []).append(
            _anchor_conflict_item_from_endpoint(anchor)
        )
    for anchor in b1_result.node_anchors.values():
        anchors_by_node.setdefault(anchor.node_id, []).append(
            _anchor_conflict_item_from_node(anchor)
        )

    reports: List[AnchorConflictReport] = []
    for node_id, items in anchors_by_node.items():
        z_values = {item.z for item in items}
        if len(z_values) <= 1:
            continue
        reports.append(
            AnchorConflictReport(
                node_id=node_id,
                reason="multiple_anchor_z_at_node",
                items=list(items),
            )
        )
    return reports


def _copy_candidate_conflicts(
    evaluation_result: CandidateEvaluationResult,
) -> List[CandidateConflictReport]:
    return [
        CandidateConflictReport(
            target_edge_index=report.target_edge_index,
            target_endpoint=report.target_endpoint,
            reason=report.reason,
            candidates=list(report.candidates),
        )
        for report in evaluation_result.conflict_reports
    ]


def _detect_lock_conditions(
    model: Any,
    evaluation_result: CandidateEvaluationResult,
) -> List[LockConditionReport]:
    reports: List[LockConditionReport] = []

    for report in evaluation_result.lock_reports:
        reports.append(
            LockConditionReport(
                edge_index=report.edge_index,
                role=report.role,
                reason=report.reason,
                candidate=report.candidate,
            )
        )

    known_edges = {
        edge_index for edge_index, _endpoint in evaluation_result.known_endpoint_z
    }
    for edge_index in sorted(known_edges):
        if _is_locked(model, edge_index):
            reports.append(
                LockConditionReport(
                    edge_index=edge_index,
                    role="known_endpoint",
                    reason="known_endpoint_edge_locked",
                )
            )

    return reports


def build_conflict_lock_report(model: Any) -> ConflictLockResult:
    """Build B4 conflict and lock report data without resolving or mutating."""
    evaluation_result = evaluate_elevation_candidates(model)
    return ConflictLockResult(
        evaluation_result=evaluation_result,
        known_endpoint_z=dict(evaluation_result.known_endpoint_z),
        anchor_conflicts=_detect_anchor_conflicts(evaluation_result),
        candidate_conflicts=_copy_candidate_conflicts(evaluation_result),
        lock_conditions=_detect_lock_conditions(model, evaluation_result),
    )
