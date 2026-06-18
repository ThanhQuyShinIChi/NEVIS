from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from unittest.mock import patch

from modules.elevation_anchor import AnchorDiscoveryResult
from modules.elevation_candidate import evaluate_elevation_candidates
from modules.elevation_wavefront import (
    CandidatePropagationPath,
    ElevationWavefrontResult,
    build_elevation_wavefront,
)


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


class ElevationCandidateEvaluationTest(unittest.TestCase):
    def test_reads_b2_data_and_creates_evaluation_result(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[DummyEdge(1, 2, end_z=100.0), DummyEdge(2, 3)],
        )

        result = evaluate_elevation_candidates(model)

        self.assertIsInstance(result.b2_result, ElevationWavefrontResult)
        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(len(result.usable_candidates), 1)
        self.assertEqual(result.blocked_candidates, [])
        self.assertEqual(result.conflict_reports, [])

    def test_b3_consumes_b2_output(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[DummyEdge(1, 2), DummyEdge(2, 3)],
        )
        fake_b2 = ElevationWavefrontResult(
            b1_result=AnchorDiscoveryResult(),
            candidate_paths=[_candidate()],
        )

        with patch("modules.elevation_candidate.build_elevation_wavefront", return_value=fake_b2) as build:
            result = evaluate_elevation_candidates(model)

        build.assert_called_once_with(model)
        self.assertIs(result.b2_result, fake_b2)
        self.assertEqual(result.usable_candidates, [_candidate()])

    def test_conflict_is_report_only_without_mutation(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[DummyEdge(1, 2), DummyEdge(2, 3)],
        )
        before = copy.deepcopy(model)
        fake_b2 = ElevationWavefrontResult(
            b1_result=AnchorDiscoveryResult(),
            candidate_paths=[
                _candidate(source_edge_index=0, source_z=100.0),
                _candidate(source_edge_index=0, source_z=120.0),
            ],
        )

        with patch("modules.elevation_candidate.build_elevation_wavefront", return_value=fake_b2):
            result = evaluate_elevation_candidates(model)

        self.assertEqual(model, before)
        self.assertEqual(len(result.conflict_reports), 1)
        self.assertEqual(result.conflict_reports[0].reason, "multiple_candidates_for_target")
        self.assertEqual(len(result.blocked_candidates), 2)
        self.assertEqual(result.usable_candidates, [])

    def test_lock_is_report_only_without_mutation(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, elevation_locked=True),
                DummyEdge(2, 3, elevation_locked=True),
            ],
        )
        before = copy.deepcopy(model)
        fake_b2 = ElevationWavefrontResult(
            b1_result=AnchorDiscoveryResult(),
            candidate_paths=[_candidate(source_edge_index=0, target_edge_index=1)],
        )

        with patch("modules.elevation_candidate.build_elevation_wavefront", return_value=fake_b2):
            result = evaluate_elevation_candidates(model)

        self.assertEqual(model, before)
        self.assertEqual(len(result.lock_reports), 2)
        self.assertEqual({report.role for report in result.lock_reports}, {"source", "target"})
        self.assertEqual(len(result.usable_candidates), 1)

    def test_does_not_mutate_model_or_create_elevation_values(self):
        model = DummyPipeModel(
            nodes={
                1: DummyNode(1, z=999.0),
                2: DummyNode(2),
                3: DummyNode(3),
            },
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )
        before = copy.deepcopy(model)

        result = evaluate_elevation_candidates(model)

        self.assertEqual(model, before)
        self.assertEqual(len(result.usable_candidates), 1)
        candidate = result.usable_candidates[0]
        self.assertFalse(hasattr(candidate, "target_z"))
        self.assertFalse(hasattr(candidate, "proposed_z"))
        self.assertIsNone(model.edges[1].start_z)
        self.assertIsNone(model.edges[1].end_z)

    def test_does_not_overwrite_known_endpoint_values(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3, start_z=200.0),
            ],
        )

        b2_result = build_elevation_wavefront(model)
        result = evaluate_elevation_candidates(model)

        self.assertEqual(result.known_endpoint_z, b2_result.known_endpoint_z)
        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(result.known_endpoint_z[(1, "start")], 200.0)
        self.assertEqual(model.edges[0].end_z, 100.0)
        self.assertEqual(model.edges[1].start_z, 200.0)


if __name__ == "__main__":
    unittest.main()
