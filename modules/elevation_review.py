from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .elevation_proposal import (
    BlockedPropagationProposal,
    PropagationProposalResult,
    PropagationProposalStep,
    build_elevation_proposals,
)


STATUS_PROPOSED = "Proposed"
STATUS_BLOCKED_CONFLICT = "Blocked by Conflict"
STATUS_BLOCKED_LOCK = "Blocked by Lock"
STATUS_SKIPPED_KNOWN_TARGET = "Skipped (Known Target)"


@dataclass(frozen=True)
class ProposalReviewRow:
    status: str
    target_edge_index: int
    target_endpoint: str
    reason: str
    source_edge_index: int | None = None
    source_endpoint: str = ""
    target_node_id: int | None = None
    source_z: float | None = None
    proposed_z: float | None = None
    source_label: str = ""
    target_edge_pair: Tuple[int, int] | None = None
    target_edge_orientation: Tuple[int, int] | None = None


@dataclass(frozen=True)
class ProposalReviewSummary:
    proposed_count: int = 0
    blocked_by_conflict_count: int = 0
    blocked_by_lock_count: int = 0
    skipped_known_target_count: int = 0
    warning_count: int = 0


@dataclass(frozen=True)
class ProposalReviewReport:
    proposal_result: PropagationProposalResult
    rows: List[ProposalReviewRow] = field(default_factory=list)
    summary: ProposalReviewSummary = field(default_factory=ProposalReviewSummary)
    warnings: List[str] = field(default_factory=list)


CONFLICT_REASONS = {
    "anchor_conflict_at_source_node",
    "anchor_conflict_at_target_node",
    "candidate_conflict",
    "multiple_candidates_for_target",
}

LOCK_REASONS = {
    "source_edge_locked",
    "target_edge_locked",
    "known_endpoint_edge_locked",
}

KNOWN_TARGET_REASONS = {
    "target_already_known",
}


def _status_for_reason(reason: str) -> str | None:
    if reason in CONFLICT_REASONS:
        return STATUS_BLOCKED_CONFLICT
    if reason in LOCK_REASONS:
        return STATUS_BLOCKED_LOCK
    if reason in KNOWN_TARGET_REASONS:
        return STATUS_SKIPPED_KNOWN_TARGET
    return None


def _target_edge_identity(
    model: Any,
    edge_index: int,
) -> tuple[Tuple[int, int] | None, Tuple[int, int] | None]:
    edges = getattr(model, "edges", None)
    try:
        edge = edges[edge_index]
        a = int(getattr(edge, "a"))
        b = int(getattr(edge, "b"))
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return None, None
    return (min(a, b), max(a, b)), (a, b)


def _row_from_proposal(model: Any, step: PropagationProposalStep) -> ProposalReviewRow:
    target_pair, target_orientation = _target_edge_identity(
        model, step.target_edge_index
    )
    return ProposalReviewRow(
        status=STATUS_PROPOSED,
        source_edge_index=step.source_edge_index,
        source_endpoint=step.source_endpoint,
        target_edge_index=step.target_edge_index,
        target_endpoint=step.target_endpoint,
        target_node_id=step.target_node_id,
        source_z=step.source_z,
        proposed_z=step.proposed_z,
        reason=step.reason,
        source_label=step.source_label,
        target_edge_pair=target_pair,
        target_edge_orientation=target_orientation,
    )


def _row_from_blocked(
    model: Any,
    step: BlockedPropagationProposal,
    status: str,
) -> ProposalReviewRow:
    candidate = step.candidate
    target_pair, target_orientation = _target_edge_identity(
        model, step.target_edge_index
    )
    return ProposalReviewRow(
        status=status,
        source_edge_index=step.source_edge_index,
        source_endpoint=step.source_endpoint,
        target_edge_index=step.target_edge_index,
        target_endpoint=step.target_endpoint,
        target_node_id=None if candidate is None else candidate.target_node_id,
        source_z=None if candidate is None else candidate.source_z,
        proposed_z=None,
        reason=step.reason,
        source_label="" if candidate is None else candidate.source,
        target_edge_pair=target_pair,
        target_edge_orientation=target_orientation,
    )


def _summary(rows: List[ProposalReviewRow], warning_count: int) -> ProposalReviewSummary:
    counts: Dict[str, int] = {}
    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
    return ProposalReviewSummary(
        proposed_count=counts.get(STATUS_PROPOSED, 0),
        blocked_by_conflict_count=counts.get(STATUS_BLOCKED_CONFLICT, 0),
        blocked_by_lock_count=counts.get(STATUS_BLOCKED_LOCK, 0),
        skipped_known_target_count=counts.get(STATUS_SKIPPED_KNOWN_TARGET, 0),
        warning_count=warning_count,
    )


def build_proposal_review(model: Any) -> ProposalReviewReport:
    """Build a read-only B6 proposal review report."""
    proposal_result = build_elevation_proposals(model)
    rows: List[ProposalReviewRow] = []
    warnings: List[str] = []

    for step in proposal_result.proposal_steps:
        rows.append(_row_from_proposal(model, step))

    for step in proposal_result.blocked_steps:
        status = _status_for_reason(step.reason)
        if status is None:
            warnings.append(f"unknown_blocked_reason:{step.reason}")
            continue
        rows.append(_row_from_blocked(model, step, status))

    return ProposalReviewReport(
        proposal_result=proposal_result,
        rows=rows,
        summary=_summary(rows, len(warnings)),
        warnings=warnings,
    )
