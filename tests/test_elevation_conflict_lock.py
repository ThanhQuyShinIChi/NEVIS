from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from unittest.mock import patch

from modules.elevation_anchor import AnchorDiscoveryResult
from modules.elevation_candidate import CandidateEvaluationResult
from modules.elevation_conflict_lock import build_conflict_lock_report
from modules.elevation_wavefront import CandidatePropagationPath, ElevationWavefrontResult


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
class DummyLevelDatum:
    id: str
    elevation_mm: float


@dataclass
class DummyPipeModel:
    nodes: Dict[int, DummyNode] = field(default_factory=dict)
    edges: List[DummyEdge] = field(default_factory=list)
    level_datums: Dict[str, DummyLevelDatum] = field(default_factory=dict)


def _candidate(
    target_edge_index: int = 1,
    target_endpoint: str = "start",
    source_edge_index: int = 0,
    source_z: float = 100.0,
) -> CandidatePropagationPath:
    return CandidatePropagationPath(
        source_kind="edge_endpoint",
        source_node_id=2,
        source_edge_index=source_edge_index,
        source_endpoint="end",
        source_z=source_z,
        target_edge_index=target_edge_index,
        target_endpoint=target_endpoint,
        target_node_id=2,
        degree=2,
        reason="degree_le_2_adjacent_unknown_endpoint",
        source="edge.end_z",
    )


class ElevationConflictLockTest(unittest.TestCase):
    def test_detects_conflict_between_multiple_anchor_z_at_same_topological_node(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3, start_z=120.0),
            ],
        )

        result = build_conflict_lock_report(model)

        self.assertEqual(len(result.anchor_conflicts), 1)
        conflict = result.anchor_conflicts[0]
        self.assertEqual(conflict.node_id, 2)
        self.assertEqual(conflict.reason, "multiple_anchor_z_at_node")
        self.assertEqual({item.z for item in conflict.items}, {100.0, 120.0})
        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(result.known_endpoint_z[(1, "start")], 120.0)

    def test_lock_condition_is_report_only(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0, elevation_locked=True),
                DummyEdge(2, 3, elevation_locked=True),
            ],
        )
        before = copy.deepcopy(model)

        result = build_conflict_lock_report(model)

        self.assertEqual(model, before)
        self.assertGreaterEqual(len(result.lock_conditions), 2)
        reasons = {report.reason for report in result.lock_conditions}
        self.assertIn("source_edge_locked", reasons)
        self.assertIn("target_edge_locked", reasons)
        self.assertIn("known_endpoint_edge_locked", reasons)

    def test_conflict_is_not_resolved_or_winner_selected(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[DummyEdge(1, 2), DummyEdge(2, 3)],
        )
        fake_evaluation = CandidateEvaluationResult(
            b2_result=ElevationWavefrontResult(b1_result=AnchorDiscoveryResult()),
            conflict_reports=[],
        )
        fake_candidates = [_candidate(source_z=100.0), _candidate(source_z=120.0)]
        fake_evaluation = CandidateEvaluationResult(
            b2_result=ElevationWavefrontResult(
                b1_result=AnchorDiscoveryResult(),
                candidate_paths=fake_candidates,
            ),
            conflict_reports=[],
        )

        # B4 should not invent a winner even when B3 has no resolved result.
        with patch("modules.elevation_conflict_lock.evaluate_elevation_candidates", return_value=fake_evaluation):
            result = build_conflict_lock_report(model)

        self.assertFalse(hasattr(result, "resolved_conflicts"))
        self.assertFalse(hasattr(result, "winning_candidates"))
        self.assertEqual(model.edges[1].start_z, None)

    def test_does_not_mutate_model_or_create_elevation_values(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1, z=999.0), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )
        before = copy.deepcopy(model)

        result = build_conflict_lock_report(model)

        self.assertEqual(model, before)
        self.assertEqual(result.anchor_conflicts, [])
        self.assertIsNone(model.edges[1].start_z)
        self.assertIsNone(model.edges[1].end_z)
        candidate = result.evaluation_result.usable_candidates[0]
        self.assertFalse(hasattr(candidate, "target_z"))
        self.assertFalse(hasattr(candidate, "proposed_z"))

    def test_does_not_overwrite_known_endpoint_values(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3, start_z=200.0),
            ],
        )

        result = build_conflict_lock_report(model)

        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(result.known_endpoint_z[(1, "start")], 200.0)
        self.assertEqual(model.edges[0].end_z, 100.0)
        self.assertEqual(model.edges[1].start_z, 200.0)


if __name__ == "__main__":
    unittest.main()
