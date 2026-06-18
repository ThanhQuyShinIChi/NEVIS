from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from modules.elevation_apply import apply_elevation_review
from modules.elevation_review import build_proposal_review


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


class FailingEdge(DummyEdge):
    def __setattr__(self, name, value):
        if name == "start_z" and getattr(self, "fail_next_start_z_write", False):
            object.__setattr__(self, "fail_next_start_z_write", False)
            object.__setattr__(self, name, value)
            raise RuntimeError("simulated write failure")
        object.__setattr__(self, name, value)


@dataclass
class DummyLevelDatum:
    id: str
    elevation_mm: float


@dataclass
class DummyPipeModel:
    nodes: Dict[int, DummyNode] = field(default_factory=dict)
    edges: List[DummyEdge] = field(default_factory=list)
    level_datums: Dict[str, DummyLevelDatum] = field(default_factory=dict)


def _linear_model(*, second_edge_locked: bool = False) -> DummyPipeModel:
    return DummyPipeModel(
        nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
        edges=[
            DummyEdge(1, 2, end_z=100.0),
            DummyEdge(2, 3, elevation_locked=second_edge_locked),
        ],
    )


def _model_with_unrelated_edge_first() -> DummyPipeModel:
    return DummyPipeModel(
        nodes={node_id: DummyNode(node_id) for node_id in (1, 2, 3, 10, 11)},
        edges=[
            DummyEdge(10, 11),
            DummyEdge(1, 2, end_z=100.0),
            DummyEdge(2, 3),
        ],
    )


class ElevationApplyTest(unittest.TestCase):
    def test_successful_apply_writes_only_target_edge_endpoint(self):
        model = _linear_model()
        report = build_proposal_review(model)

        result = apply_elevation_review(model, report)

        self.assertTrue(result.success)
        self.assertEqual(model.edges[1].start_z, 100.0)
        self.assertIsNone(model.edges[1].end_z)
        self.assertEqual(result.summary.applied_count, 1)

    def test_conflict_is_hard_blocker(self):
        model = _linear_model()
        model.nodes[2].level_id = "L2"
        model.level_datums["L2"] = DummyLevelDatum("L2", 120.0)
        report = build_proposal_review(model)

        result = apply_elevation_review(model, report)

        self.assertFalse(result.success)
        self.assertIsNone(model.edges[1].start_z)
        self.assertIn("unresolved_conflict_in_report", {item.reason for item in result.rejected_steps})

    def test_lock_is_hard_blocker(self):
        model = _linear_model(second_edge_locked=True)
        report = build_proposal_review(model)

        result = apply_elevation_review(model, report)

        self.assertFalse(result.success)
        self.assertIsNone(model.edges[1].start_z)
        self.assertIn("locked_value_in_report", {item.reason for item in result.rejected_steps})

    def test_existing_value_blocks_apply_without_overwrite(self):
        model = _linear_model()
        report = build_proposal_review(model)
        model.edges[1].start_z = 200.0

        result = apply_elevation_review(model, report)

        self.assertFalse(result.success)
        self.assertEqual(model.edges[1].start_z, 200.0)
        self.assertIn("target_already_known", {item.reason for item in result.rejected_steps})

    def test_snapshot_is_created_before_successful_write(self):
        model = _linear_model()
        report = build_proposal_review(model)

        result = apply_elevation_review(model, report)

        self.assertEqual(len(result.undo_snapshot), 1)
        item = result.undo_snapshot[0]
        self.assertEqual((item.edge_index, item.field_name), (1, "start_z"))
        self.assertIsNone(item.old_value)
        self.assertEqual(item.new_value, 100.0)
        self.assertTrue(result.rollback_available)

    def test_write_failure_rolls_back_all_prior_writes(self):
        model = DummyPipeModel(
            nodes={
                1: DummyNode(1),
                2: DummyNode(2),
                3: DummyNode(3),
                4: DummyNode(4),
                5: DummyNode(5),
                6: DummyNode(6),
            },
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
                DummyEdge(4, 5, end_z=200.0),
                FailingEdge(5, 6),
            ],
        )
        report = build_proposal_review(model)
        model.edges[3].fail_next_start_z_write = True

        result = apply_elevation_review(model, report)

        self.assertFalse(result.success)
        self.assertTrue(result.rolled_back)
        self.assertIsNone(model.edges[1].start_z)
        self.assertIsNone(model.edges[3].start_z)
        self.assertEqual(len(result.undo_snapshot), 2)
        self.assertIn("simulated write failure", result.error)

    def test_node_z_is_never_written(self):
        model = _linear_model()
        model.nodes[2].z = 999.0
        report = build_proposal_review(model)

        result = apply_elevation_review(model, report)

        self.assertTrue(result.success)
        self.assertEqual(model.nodes[2].z, 999.0)

    def test_endpoint_pair_apply_without_topology_change(self):
        model = _model_with_unrelated_edge_first()
        report = build_proposal_review(model)

        result = apply_elevation_review(model, report)

        self.assertTrue(result.success)
        self.assertEqual(model.edges[2].start_z, 100.0)
        self.assertEqual(result.undo_snapshot[0].edge_index, 2)

    def test_endpoint_pair_resolves_target_after_other_edge_deleted(self):
        model = _model_with_unrelated_edge_first()
        report = build_proposal_review(model)
        del model.edges[0]

        result = apply_elevation_review(model, report)

        self.assertTrue(result.success)
        self.assertEqual((model.edges[1].a, model.edges[1].b), (2, 3))
        self.assertEqual(model.edges[1].start_z, 100.0)
        self.assertEqual(result.undo_snapshot[0].edge_index, 1)

    def test_endpoint_pair_remains_valid_after_unrelated_edge_added(self):
        model = _model_with_unrelated_edge_first()
        report = build_proposal_review(model)
        model.nodes[20] = DummyNode(20)
        model.nodes[21] = DummyNode(21)
        model.edges.append(DummyEdge(20, 21))

        result = apply_elevation_review(model, report)

        self.assertTrue(result.success)
        self.assertEqual(model.edges[2].start_z, 100.0)
        self.assertIsNone(model.edges[-1].start_z)

    def test_multi_edge_endpoint_pair_hard_blocks_without_write(self):
        model = _model_with_unrelated_edge_first()
        report = build_proposal_review(model)
        original_target = model.edges[2]
        model.edges.append(DummyEdge(3, 2))

        result = apply_elevation_review(model, report)

        self.assertFalse(result.success)
        self.assertIn(
            "multi_edge_endpoint_pair",
            {item.reason for item in result.rejected_steps},
        )
        self.assertIsNone(original_target.start_z)
        self.assertIsNone(model.edges[-1].end_z)

    def test_reversed_target_orientation_hard_blocks_without_write(self):
        model = _linear_model()
        report = build_proposal_review(model)
        model.edges[1] = DummyEdge(3, 2)

        result = apply_elevation_review(model, report)

        self.assertFalse(result.success)
        self.assertIn(
            "target_edge_orientation_mismatch",
            {item.reason for item in result.rejected_steps},
        )
        self.assertIsNone(model.edges[1].end_z)


if __name__ == "__main__":
    unittest.main()
