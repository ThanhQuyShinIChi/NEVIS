from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from modules.elevation_proposal import build_elevation_proposals


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


class ElevationProposalTest(unittest.TestCase):
    def test_creates_proposal_from_b1_b2_b3_b4_pipeline(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )

        result = build_elevation_proposals(model)

        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(len(result.proposal_steps), 1)
        self.assertEqual(result.blocked_steps, [])
        step = result.proposal_steps[0]
        self.assertEqual(step.source_edge_index, 0)
        self.assertEqual(step.source_endpoint, "end")
        self.assertEqual(step.target_edge_index, 1)
        self.assertEqual(step.target_endpoint, "start")
        self.assertEqual(step.proposed_z, 100.0)
        self.assertEqual(step.reason, "copy_source_z_for_dry_run_proposal")

    def test_conflict_blocks_proposal(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2, level_id="L2"), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
            level_datums={"L2": DummyLevelDatum("L2", 120.0)},
        )

        result = build_elevation_proposals(model)

        self.assertEqual(result.proposal_steps, [])
        reasons = {step.reason for step in result.blocked_steps}
        self.assertIn("anchor_conflict_at_source_node", reasons)
        self.assertTrue(result.conflict_lock_result.anchor_conflicts)
        self.assertEqual(model.edges[1].start_z, None)
        self.assertEqual(model.edges[1].end_z, None)

    def test_locked_value_blocks_proposal_report_only(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0, elevation_locked=True),
                DummyEdge(2, 3),
            ],
        )
        before = copy.deepcopy(model)

        result = build_elevation_proposals(model)

        self.assertEqual(model, before)
        self.assertEqual(result.proposal_steps, [])
        reasons = {step.reason for step in result.blocked_steps}
        self.assertIn("source_edge_locked", reasons)
        self.assertTrue(result.conflict_lock_result.lock_conditions)

    def test_does_not_mutate_model_or_write_z_back(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1, z=999.0), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )
        before = copy.deepcopy(model)

        result = build_elevation_proposals(model)

        self.assertEqual(model, before)
        self.assertEqual(len(result.proposal_steps), 1)
        self.assertIsNone(model.edges[1].start_z)
        self.assertIsNone(model.edges[1].end_z)
        self.assertEqual(model.nodes[1].z, 999.0)
        self.assertIsNone(model.nodes[2].z)
        self.assertIsNone(model.nodes[3].z)

    def test_does_not_create_apply_action_or_overwrite_known_values(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3, start_z=200.0),
            ],
        )

        result = build_elevation_proposals(model)

        self.assertFalse(hasattr(result, "apply_actions"))
        self.assertFalse(hasattr(result, "applied_steps"))
        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(result.known_endpoint_z[(1, "start")], 200.0)
        self.assertEqual(model.edges[0].end_z, 100.0)
        self.assertEqual(model.edges[1].start_z, 200.0)


if __name__ == "__main__":
    unittest.main()
