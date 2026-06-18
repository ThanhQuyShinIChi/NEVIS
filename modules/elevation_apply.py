from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real
from typing import Any, Dict, List, Tuple

from .elevation_conflict_lock import build_conflict_lock_report

from .elevation_review import (
    STATUS_BLOCKED_CONFLICT,
    STATUS_BLOCKED_LOCK,
    STATUS_PROPOSED,
    ProposalReviewReport,
    ProposalReviewRow,
)


@dataclass(frozen=True)
class ApplySnapshotItem:
    edge_index: int
    endpoint: str
    field_name: str
    old_value: Any
    new_value: float
    source_edge_index: int | None = None
    source_endpoint: str = ""


@dataclass(frozen=True)
class AppliedStep:
    row: ProposalReviewRow
    snapshot: ApplySnapshotItem


@dataclass(frozen=True)
class SkippedStep:
    row: ProposalReviewRow
    reason: str


@dataclass(frozen=True)
class RejectedStep:
    row: ProposalReviewRow | None
    reason: str


@dataclass(frozen=True)
class ApplySummary:
    applied_count: int = 0
    skipped_count: int = 0
    rejected_count: int = 0


@dataclass(frozen=True)
class ApplyResult:
    success: bool
    applied_steps: List[AppliedStep] = field(default_factory=list)
    skipped_steps: List[SkippedStep] = field(default_factory=list)
    rejected_steps: List[RejectedStep] = field(default_factory=list)
    undo_snapshot: List[ApplySnapshotItem] = field(default_factory=list)
    rollback_available: bool = False
    rolled_back: bool = False
    error: str = ""
    summary: ApplySummary = field(default_factory=ApplySummary)


def _summary(
    applied: List[AppliedStep],
    skipped: List[SkippedStep],
    rejected: List[RejectedStep],
) -> ApplySummary:
    return ApplySummary(
        applied_count=len(applied),
        skipped_count=len(skipped),
        rejected_count=len(rejected),
    )


def _edge_at(model: Any, edge_index: int) -> Any | None:
    edges = getattr(model, "edges", None)
    if edges is None or edge_index < 0:
        return None
    try:
        return edges[edge_index]
    except (IndexError, KeyError, TypeError):
        return None


def _field_name(endpoint: str) -> str:
    return "start_z" if endpoint == "start" else "end_z"


def _is_numeric_z(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and isfinite(float(value))


EndpointPair = Tuple[int, int]
PairIndex = Dict[EndpointPair, List[tuple[int, Any]]]


def _edge_pair(edge: Any) -> EndpointPair | None:
    try:
        a = int(getattr(edge, "a"))
        b = int(getattr(edge, "b"))
    except (AttributeError, TypeError, ValueError):
        return None
    return min(a, b), max(a, b)


def _edge_orientation(edge: Any) -> Tuple[int, int] | None:
    try:
        return int(getattr(edge, "a")), int(getattr(edge, "b"))
    except (AttributeError, TypeError, ValueError):
        return None


def _build_pair_index(model: Any) -> tuple[PairIndex, str]:
    edges = getattr(model, "edges", None)
    if edges is None:
        return {}, "missing_model_edges"
    pair_index: PairIndex = {}
    try:
        for edge_index, edge in enumerate(edges):
            pair = _edge_pair(edge)
            if pair is None:
                return {}, "invalid_edge_endpoint_pair"
            pair_index.setdefault(pair, []).append((edge_index, edge))
    except TypeError:
        return {}, "invalid_model_edges"
    if any(len(matches) > 1 for matches in pair_index.values()):
        return pair_index, "multi_edge_endpoint_pair"
    return pair_index, ""


def _target_is_known(model: Any, edge: Any, endpoint: str) -> bool:
    field_name = _field_name(endpoint)
    explicit_z = getattr(edge, field_name, None)
    if explicit_z not in (None, ""):
        return True
    level_id = str(getattr(edge, f"{endpoint}_level_id", "") or "").strip()
    if not level_id:
        return False
    datum = (getattr(model, "level_datums", {}) or {}).get(level_id)
    return datum is not None and _is_numeric_z(getattr(datum, "elevation_mm", None))


def _validate_proposed_row(
    model: Any,
    row: ProposalReviewRow,
    pair_index: PairIndex,
    strict: bool,
) -> tuple[int | None, Any | None, str]:
    if row.target_edge_pair is None or row.target_edge_orientation is None:
        return None, None, "missing_target_edge_identity"
    try:
        target_pair = tuple(int(value) for value in row.target_edge_pair)
        target_orientation = tuple(int(value) for value in row.target_edge_orientation)
    except (TypeError, ValueError):
        return None, None, "invalid_target_edge_identity"
    if len(target_pair) != 2 or len(target_orientation) != 2:
        return None, None, "invalid_target_edge_identity"
    if target_pair != tuple(sorted(target_pair)):
        return None, None, "invalid_target_edge_pair"
    if tuple(sorted(target_orientation)) != target_pair:
        return None, None, "target_edge_pair_mismatch"

    matches = pair_index.get(target_pair, [])
    if not matches:
        return None, None, "target_edge_not_found"
    if len(matches) != 1:
        return None, None, "multi_edge_endpoint_pair"
    current_edge_index, edge = matches[0]
    if _edge_orientation(edge) != target_orientation:
        return None, None, "target_edge_orientation_mismatch"
    if row.target_endpoint not in {"start", "end"}:
        return None, None, "invalid_target_endpoint"
    target_node_id = getattr(edge, "a" if row.target_endpoint == "start" else "b", None)
    if row.target_node_id is None or int(target_node_id) != int(row.target_node_id):
        return None, None, "target_node_mismatch"
    if not _is_numeric_z(row.proposed_z):
        return None, None, "invalid_proposed_z"
    if bool(getattr(edge, "elevation_locked", False)):
        return None, None, "target_edge_locked"
    if strict and _target_is_known(model, edge, row.target_endpoint):
        return None, None, "target_already_known"
    return current_edge_index, edge, ""


def apply_elevation_review(
    model: Any,
    report: ProposalReviewReport,
    *,
    strict: bool = True,
) -> ApplyResult:
    """Validate and atomically apply safe B6 Proposed rows to edge endpoint Z fields."""
    skipped = [
        SkippedStep(row=row, reason="status_not_proposed")
        for row in report.rows
        if row.status != STATUS_PROPOSED
    ]
    proposed_rows = [row for row in report.rows if row.status == STATUS_PROPOSED]
    rejected: List[RejectedStep] = []

    if any(row.status == STATUS_BLOCKED_CONFLICT for row in report.rows):
        rejected.append(RejectedStep(row=None, reason="unresolved_conflict_in_report"))
    if any(row.status == STATUS_BLOCKED_LOCK for row in report.rows):
        rejected.append(RejectedStep(row=None, reason="locked_value_in_report"))
    if strict and report.warnings:
        rejected.append(RejectedStep(row=None, reason="blocking_report_warnings"))

    pair_index, pair_index_error = _build_pair_index(model)
    if pair_index_error:
        rejected.append(RejectedStep(row=None, reason=pair_index_error))

    try:
        current_conflicts = build_conflict_lock_report(model)
        if current_conflicts.anchor_conflicts or current_conflicts.candidate_conflicts:
            rejected.append(RejectedStep(row=None, reason="current_model_conflict"))
    except Exception:
        rejected.append(RejectedStep(row=None, reason="current_conflict_validation_failed"))

    targets: set[tuple[EndpointPair, str]] = set()
    plan: List[tuple[ProposalReviewRow, int, Any]] = []
    for row in proposed_rows:
        pair = row.target_edge_pair
        key = (pair, row.target_endpoint)
        if key in targets:
            rejected.append(RejectedStep(row=row, reason="duplicate_target_proposal"))
            continue
        targets.add(key)
        current_edge_index, edge, reason = _validate_proposed_row(
            model, row, pair_index, strict
        )
        if reason:
            rejected.append(RejectedStep(row=row, reason=reason))
        else:
            plan.append((row, current_edge_index, edge))

    if rejected:
        result_summary = _summary([], skipped, rejected)
        return ApplyResult(
            success=False,
            skipped_steps=skipped,
            rejected_steps=rejected,
            summary=result_summary,
            error="validation_failed",
        )

    snapshot = [
        ApplySnapshotItem(
            edge_index=current_edge_index,
            endpoint=row.target_endpoint,
            field_name=_field_name(row.target_endpoint),
            old_value=getattr(edge, _field_name(row.target_endpoint), None),
            new_value=float(row.proposed_z),
            source_edge_index=row.source_edge_index,
            source_endpoint=row.source_endpoint,
        )
        for row, current_edge_index, edge in plan
    ]

    applied: List[AppliedStep] = []
    try:
        for (row, current_edge_index, edge), item in zip(plan, snapshot):
            if _edge_at(model, current_edge_index) is not edge:
                raise RuntimeError("target_edge_changed_during_write")
            if _edge_pair(edge) != row.target_edge_pair:
                raise RuntimeError("target_edge_pair_changed_during_write")
            if _edge_orientation(edge) != row.target_edge_orientation:
                raise RuntimeError("target_edge_orientation_changed_during_write")
            if bool(getattr(edge, "elevation_locked", False)):
                raise RuntimeError("target_edge_locked_during_write")
            if strict and _target_is_known(model, edge, row.target_endpoint):
                raise RuntimeError("target_already_known_during_write")
            setattr(edge, item.field_name, item.new_value)
            applied.append(AppliedStep(row=row, snapshot=item))
    except Exception as exc:
        rollback_errors: List[str] = []
        for item in reversed(snapshot):
            edge = _edge_at(model, item.edge_index)
            try:
                if edge is None:
                    raise RuntimeError("target_edge_missing_during_rollback")
                setattr(edge, item.field_name, item.old_value)
            except Exception as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        error = f"write_failed:{exc}"
        if rollback_errors:
            error += ";rollback_failed:" + "|".join(rollback_errors)
        failed_rejection = RejectedStep(
            row=plan[len(applied)][0] if len(applied) < len(plan) else None,
            reason="write_failed",
        )
        rejected = [failed_rejection]
        return ApplyResult(
            success=False,
            skipped_steps=skipped,
            rejected_steps=rejected,
            undo_snapshot=snapshot,
            rolled_back=not rollback_errors,
            error=error,
            summary=_summary([], skipped, rejected),
        )

    return ApplyResult(
        success=True,
        applied_steps=applied,
        skipped_steps=skipped,
        undo_snapshot=snapshot,
        rollback_available=bool(snapshot),
        summary=_summary(applied, skipped, []),
    )


def undo_elevation_apply(model: Any, result: ApplyResult) -> bool:
    """Restore the exact pre-apply endpoint values from a successful result."""
    if not result.success or not result.rollback_available:
        return False
    restored: List[tuple[Any, ApplySnapshotItem]] = []
    try:
        for item in reversed(result.undo_snapshot):
            edge = _edge_at(model, item.edge_index)
            if edge is None:
                raise RuntimeError("target_edge_missing_during_undo")
            setattr(edge, item.field_name, item.old_value)
            restored.append((edge, item))
    except Exception:
        for edge, item in reversed(restored):
            setattr(edge, item.field_name, item.new_value)
        return False
    return True
