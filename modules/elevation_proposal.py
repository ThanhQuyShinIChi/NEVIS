from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .elevation_conflict_lock import ConflictLockResult, build_conflict_lock_report
from .elevation_wavefront import CandidatePropagationPath


EndpointKey = Tuple[int, str]


@dataclass(frozen=True)
class PropagationProposalStep:
    source_kind: str
    source_node_id: int
    target_node_id: int
    target_edge_index: int
    target_endpoint: str
    proposed_z: float | None
    reason: str
    source_edge_index: int | None = None
    source_endpoint: str = ""
    source_z: float | None = None
    source_label: str = ""
    topology_degree: int = 0


@dataclass(frozen=True)
class BlockedPropagationProposal:
    target_edge_index: int
    target_endpoint: str
    reason: str
    source_edge_index: int | None = None
    source_endpoint: str = ""
    candidate: CandidatePropagationPath | None = None


@dataclass(frozen=True)
class PropagationProposalResult:
    conflict_lock_result: ConflictLockResult
    known_endpoint_z: Dict[EndpointKey, float] = field(default_factory=dict)
    proposal_steps: List[PropagationProposalStep] = field(default_factory=list)
    blocked_steps: List[BlockedPropagationProposal] = field(default_factory=list)


def _conflict_nodes(conflict_lock_result: ConflictLockResult) -> set[int]:
    return {report.node_id for report in conflict_lock_result.anchor_conflicts}


def _conflict_targets(conflict_lock_result: ConflictLockResult) -> set[EndpointKey]:
    return {
        (report.target_edge_index, report.target_endpoint)
        for report in conflict_lock_result.candidate_conflicts
    }


def _locked_edges(conflict_lock_result: ConflictLockResult) -> set[int]:
    return {report.edge_index for report in conflict_lock_result.lock_conditions}


def _candidate_block_reasons(
    candidate: CandidatePropagationPath,
    conflict_lock_result: ConflictLockResult,
) -> List[str]:
    reasons: List[str] = []
    target_key = (candidate.target_edge_index, candidate.target_endpoint)

    if target_key in conflict_lock_result.known_endpoint_z:
        reasons.append("target_already_known")
    if target_key in _conflict_targets(conflict_lock_result):
        reasons.append("candidate_conflict")
    if candidate.source_node_id in _conflict_nodes(conflict_lock_result):
        reasons.append("anchor_conflict_at_source_node")
    if candidate.target_node_id in _conflict_nodes(conflict_lock_result):
        reasons.append("anchor_conflict_at_target_node")

    locked_edges = _locked_edges(conflict_lock_result)
    if candidate.source_edge_index in locked_edges:
        reasons.append("source_edge_locked")
    if candidate.target_edge_index in locked_edges:
        reasons.append("target_edge_locked")

    return reasons


def _proposal_from_candidate(candidate: CandidatePropagationPath) -> PropagationProposalStep:
    return PropagationProposalStep(
        source_kind=candidate.source_kind,
        source_node_id=candidate.source_node_id,
        source_edge_index=candidate.source_edge_index,
        source_endpoint=candidate.source_endpoint,
        source_z=candidate.source_z,
        source_label=candidate.source,
        target_node_id=candidate.target_node_id,
        target_edge_index=candidate.target_edge_index,
        target_endpoint=candidate.target_endpoint,
        topology_degree=candidate.degree,
        proposed_z=candidate.source_z,
        reason="copy_source_z_for_dry_run_proposal",
    )


def build_elevation_proposals(model: Any) -> PropagationProposalResult:
    """Build read-only propagation proposals without applying them to the model."""
    conflict_lock_result = build_conflict_lock_report(model)
    proposal_steps: List[PropagationProposalStep] = []
    blocked_steps: List[BlockedPropagationProposal] = []

    for candidate in conflict_lock_result.evaluation_result.usable_candidates:
        reasons = _candidate_block_reasons(candidate, conflict_lock_result)
        if reasons:
            for reason in reasons:
                blocked_steps.append(
                    BlockedPropagationProposal(
                        target_edge_index=candidate.target_edge_index,
                        target_endpoint=candidate.target_endpoint,
                        source_edge_index=candidate.source_edge_index,
                        source_endpoint=candidate.source_endpoint,
                        reason=reason,
                        candidate=candidate,
                    )
                )
            continue
        proposal_steps.append(_proposal_from_candidate(candidate))

    for issue in conflict_lock_result.evaluation_result.blocked_candidates:
        blocked_steps.append(
            BlockedPropagationProposal(
                target_edge_index=issue.target_edge_index,
                target_endpoint=issue.target_endpoint,
                source_edge_index=issue.source_edge_index,
                source_endpoint=issue.source_endpoint,
                reason=issue.reason,
            )
        )

    conflict_nodes = _conflict_nodes(conflict_lock_result)
    for candidate in conflict_lock_result.evaluation_result.b2_result.candidate_paths:
        if candidate.source_node_id in conflict_nodes:
            blocked_steps.append(
                BlockedPropagationProposal(
                    target_edge_index=candidate.target_edge_index,
                    target_endpoint=candidate.target_endpoint,
                    source_edge_index=candidate.source_edge_index,
                    source_endpoint=candidate.source_endpoint,
                    reason="anchor_conflict_at_source_node",
                    candidate=candidate,
                )
            )
        if candidate.target_node_id in conflict_nodes:
            blocked_steps.append(
                BlockedPropagationProposal(
                    target_edge_index=candidate.target_edge_index,
                    target_endpoint=candidate.target_endpoint,
                    source_edge_index=candidate.source_edge_index,
                    source_endpoint=candidate.source_endpoint,
                    reason="anchor_conflict_at_target_node",
                    candidate=candidate,
                )
            )

    return PropagationProposalResult(
        conflict_lock_result=conflict_lock_result,
        known_endpoint_z=dict(conflict_lock_result.known_endpoint_z),
        proposal_steps=proposal_steps,
        blocked_steps=blocked_steps,
    )
