from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .elevation_wavefront import (
    CandidatePropagationPath,
    ElevationWavefrontResult,
    build_elevation_wavefront,
)


EndpointKey = Tuple[int, str]


@dataclass(frozen=True)
class CandidateIssue:
    target_edge_index: int
    target_endpoint: str
    reason: str
    source_edge_index: int | None = None
    source_endpoint: str = ""


@dataclass(frozen=True)
class ConflictReport:
    target_edge_index: int
    target_endpoint: str
    reason: str
    candidates: List[CandidatePropagationPath] = field(default_factory=list)


@dataclass(frozen=True)
class LockReport:
    edge_index: int
    role: str
    reason: str
    candidate: CandidatePropagationPath


@dataclass(frozen=True)
class CandidateEvaluationResult:
    b2_result: ElevationWavefrontResult
    known_endpoint_z: Dict[EndpointKey, float] = field(default_factory=dict)
    usable_candidates: List[CandidatePropagationPath] = field(default_factory=list)
    blocked_candidates: List[CandidateIssue] = field(default_factory=list)
    conflict_reports: List[ConflictReport] = field(default_factory=list)
    lock_reports: List[LockReport] = field(default_factory=list)


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


def evaluate_elevation_candidates(model: Any) -> CandidateEvaluationResult:
    """Evaluate B2 candidate paths without mutating or propagating values."""
    b2_result = build_elevation_wavefront(model)
    known_endpoint_z = dict(b2_result.known_endpoint_z)
    usable_candidates: List[CandidatePropagationPath] = []
    blocked_candidates: List[CandidateIssue] = []
    conflict_reports: List[ConflictReport] = []
    lock_reports: List[LockReport] = []

    candidates_by_target: Dict[EndpointKey, List[CandidatePropagationPath]] = {}
    for candidate in b2_result.candidate_paths:
        target_key = (candidate.target_edge_index, candidate.target_endpoint)
        candidates_by_target.setdefault(target_key, []).append(candidate)

    conflicted_targets = {
        target_key: paths
        for target_key, paths in candidates_by_target.items()
        if len(paths) > 1
    }
    for (edge_index, endpoint), paths in conflicted_targets.items():
        conflict_reports.append(
            ConflictReport(
                target_edge_index=edge_index,
                target_endpoint=endpoint,
                reason="multiple_candidates_for_target",
                candidates=list(paths),
            )
        )

    for candidate in b2_result.candidate_paths:
        target_key = (candidate.target_edge_index, candidate.target_endpoint)
        reasons: List[str] = []

        if target_key in known_endpoint_z:
            reasons.append("target_already_known")
        if target_key in conflicted_targets:
            reasons.append("multiple_candidates_for_target")
        if not candidate.source:
            reasons.append("missing_source_metadata")
        if candidate.target_endpoint not in ("start", "end"):
            reasons.append("invalid_target_endpoint")
        if _edge_at(model, candidate.target_edge_index) is None:
            reasons.append("target_edge_missing")

        if _is_locked(model, candidate.source_edge_index):
            lock_reports.append(
                LockReport(
                    edge_index=int(candidate.source_edge_index),
                    role="source",
                    reason="source_edge_locked",
                    candidate=candidate,
                )
            )
        if _is_locked(model, candidate.target_edge_index):
            lock_reports.append(
                LockReport(
                    edge_index=candidate.target_edge_index,
                    role="target",
                    reason="target_edge_locked",
                    candidate=candidate,
                )
            )

        if reasons:
            for reason in reasons:
                blocked_candidates.append(
                    CandidateIssue(
                        target_edge_index=candidate.target_edge_index,
                        target_endpoint=candidate.target_endpoint,
                        reason=reason,
                        source_edge_index=candidate.source_edge_index,
                        source_endpoint=candidate.source_endpoint,
                    )
                )
            continue

        usable_candidates.append(candidate)

    return CandidateEvaluationResult(
        b2_result=b2_result,
        known_endpoint_z=known_endpoint_z,
        usable_candidates=usable_candidates,
        blocked_candidates=blocked_candidates,
        conflict_reports=conflict_reports,
        lock_reports=lock_reports,
    )
