from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from unittest.mock import patch

from modules.elevation_conflict_lock import ConflictLockResult
from modules.elevation_candidate import CandidateEvaluationResult
from modules.elevation_proposal import (
    BlockedPropagationProposal,
    PropagationProposalResult,
    PropagationProposalStep,
)
from modules.elevation_review import (
    STATUS_BLOCKED_CONFLICT,
    STATUS_BLOCKED_LOCK,
    STATUS_PROPOSED,
    STATUS_SKIPPED_KNOWN_TARGET,
    build_proposal_review,
)
from modules.elevation_wavefront import ElevationWavefrontResult
from modules.elevation_anchor import AnchorDiscoveryResult


@dataclass
class DummyNode:
    id: int
    z: Optional[float] = None
    level_id: str = ""


@dataclass
class DummyEdge:
    a: int
    b: int
    start_z: Optional[float] = None
    end_z: Optional[float] = None
    start_level_id: str = ""
    end_level_id: str = ""
    elevation_locked: bool = False

    @property
    def key(self) -> str:
        return f"{min(self.a, self.b)}-{max(self.a, self.b)}"


@dataclass
class DummyPipeModel:
    nodes: Dict[int, DummyNode] = field(default_factory=dict)
    edges: List[DummyEdge] = field(default_factory=list)


def _empty_conflict_lock_result() -> ConflictLockResult:
    return ConflictLockResult(
        evaluation_result=CandidateEvaluationResult(
            b2_result=ElevationWavefrontResult(
                b1_result=AnchorDiscoveryResult(),
            )
        )
    )


def _proposal_result_with_block(reason: str) -> PropagationProposalResult:
    return PropagationProposalResult(
        conflict_lock_result=_empty_conflict_lock_result(),
        blocked_steps=[
            BlockedPropagationProposal(
                target_edge_index=1,
                target_endpoint="start",
                source_edge_index=0,
                source_endpoint="end",
                reason=reason,
            )
        ],
    )


class ElevationReviewTest(unittest.TestCase):
    def test_report_created_from_real_proposal_pipeline(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )

        report = build_proposal_review(model)

        self.assertEqual(len(report.rows), 1)
        self.assertEqual(report.rows[0].status, STATUS_PROPOSED)
        self.assertEqual(report.rows[0].target_edge_index, 1)
        self.assertEqual(report.rows[0].target_endpoint, "start")
        self.assertEqual(report.rows[0].proposed_z, 100.0)
        self.assertEqual(report.summary.proposed_count, 1)

    def test_proposed_classified_correctly(self):
        model = DummyPipeModel()
        fake_result = PropagationProposalResult(
            conflict_lock_result=_empty_conflict_lock_result(),
            proposal_steps=[
                PropagationProposalStep(
                    source_kind="edge_endpoint",
                    source_node_id=2,
                    source_edge_index=0,
                    source_endpoint="end",
                    source_z=100.0,
                    target_node_id=2,
                    target_edge_index=1,
                    target_endpoint="start",
                    proposed_z=100.0,
                    reason="copy_source_z_for_dry_run_proposal",
                )
            ],
        )

        with patch("modules.elevation_review.build_elevation_proposals", return_value=fake_result):
            report = build_proposal_review(model)

        self.assertEqual(report.rows[0].status, STATUS_PROPOSED)
        self.assertEqual(report.summary.proposed_count, 1)

    def test_conflict_classified_correctly(self):
        model = DummyPipeModel()
        fake_result = _proposal_result_with_block("anchor_conflict_at_source_node")

        with patch("modules.elevation_review.build_elevation_proposals", return_value=fake_result):
            report = build_proposal_review(model)

        self.assertEqual(report.rows[0].status, STATUS_BLOCKED_CONFLICT)
        self.assertEqual(report.summary.blocked_by_conflict_count, 1)

    def test_lock_classified_correctly(self):
        model = DummyPipeModel()
        fake_result = _proposal_result_with_block("source_edge_locked")

        with patch("modules.elevation_review.build_elevation_proposals", return_value=fake_result):
            report = build_proposal_review(model)

        self.assertEqual(report.rows[0].status, STATUS_BLOCKED_LOCK)
        self.assertEqual(report.summary.blocked_by_lock_count, 1)

    def test_known_target_classified_correctly(self):
        model = DummyPipeModel()
        fake_result = _proposal_result_with_block("target_already_known")

        with patch("modules.elevation_review.build_elevation_proposals", return_value=fake_result):
            report = build_proposal_review(model)

        self.assertEqual(report.rows[0].status, STATUS_SKIPPED_KNOWN_TARGET)
        self.assertEqual(report.summary.skipped_known_target_count, 1)

    def test_does_not_mutate_model(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1, z=999.0), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )
        before = copy.deepcopy(model)

        report = build_proposal_review(model)

        self.assertEqual(model, before)
        self.assertFalse(hasattr(report, "apply_actions"))
        self.assertFalse(hasattr(report, "applied_steps"))


if __name__ == "__main__":
    unittest.main()
