from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from modules.elevation_review import STATUS_PROPOSED, ProposalReviewRow, build_proposal_review


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
    level_datums: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class PreviewTargetIdentity:
    endpoint_pair: tuple[int, int]
    expected_a: int
    expected_b: int
    target_endpoint: str
    expected_target_node_id: int
    preview_edge_index: int
    expected_old_value: Optional[float]
    expected_locked: bool


class IdentityVerificationError(RuntimeError):
    pass


def _canonical_pair(edge: DummyEdge) -> tuple[int, int]:
    return min(edge.a, edge.b), max(edge.a, edge.b)


def _capture_identity(model: DummyPipeModel, row: ProposalReviewRow) -> PreviewTargetIdentity:
    edge = model.edges[row.target_edge_index]
    field_name = "start_z" if row.target_endpoint == "start" else "end_z"
    target_node_id = edge.a if row.target_endpoint == "start" else edge.b
    return PreviewTargetIdentity(
        endpoint_pair=_canonical_pair(edge),
        expected_a=edge.a,
        expected_b=edge.b,
        target_endpoint=row.target_endpoint,
        expected_target_node_id=target_node_id,
        preview_edge_index=row.target_edge_index,
        expected_old_value=getattr(edge, field_name),
        expected_locked=edge.elevation_locked,
    )


def _verify_target_by_endpoint_pair(
    model: DummyPipeModel,
    identity: PreviewTargetIdentity,
) -> tuple[int, DummyEdge]:
    pair_index: Dict[tuple[int, int], List[tuple[int, DummyEdge]]] = {}
    for index, edge in enumerate(model.edges):
        pair_index.setdefault(_canonical_pair(edge), []).append((index, edge))

    multi_pairs = {pair: matches for pair, matches in pair_index.items() if len(matches) > 1}
    if multi_pairs:
        raise IdentityVerificationError("multi_edge_endpoint_pair")

    matches = pair_index.get(identity.endpoint_pair, [])
    if not matches:
        raise IdentityVerificationError("target_edge_missing")

    current_index, edge = matches[0]
    if (edge.a, edge.b) != (identity.expected_a, identity.expected_b):
        raise IdentityVerificationError("edge_orientation_mismatch")

    target_node_id = edge.a if identity.target_endpoint == "start" else edge.b
    if target_node_id != identity.expected_target_node_id:
        raise IdentityVerificationError("target_node_mismatch")

    field_name = "start_z" if identity.target_endpoint == "start" else "end_z"
    if getattr(edge, field_name) != identity.expected_old_value:
        raise IdentityVerificationError("target_value_mismatch")
    if edge.elevation_locked != identity.expected_locked or edge.elevation_locked:
        raise IdentityVerificationError("target_lock_mismatch")
    return current_index, edge


def _verified_reference_apply(
    model: DummyPipeModel,
    row: ProposalReviewRow,
    identity: PreviewTargetIdentity,
) -> int:
    if row.status != STATUS_PROPOSED:
        raise IdentityVerificationError("status_not_proposed")
    current_index, edge = _verify_target_by_endpoint_pair(model, identity)
    field_name = "start_z" if identity.target_endpoint == "start" else "end_z"
    setattr(edge, field_name, float(row.proposed_z))
    return current_index


def _model_with_unrelated_edge_first() -> DummyPipeModel:
    return DummyPipeModel(
        nodes={node_id: DummyNode(node_id) for node_id in (1, 2, 3, 10, 11)},
        edges=[
            DummyEdge(10, 11),
            DummyEdge(1, 2, end_z=100.0),
            DummyEdge(2, 3),
        ],
    )


def _preview(model: DummyPipeModel) -> tuple[ProposalReviewRow, PreviewTargetIdentity]:
    report = build_proposal_review(model)
    proposed_rows = [row for row in report.rows if row.status == STATUS_PROPOSED]
    if len(proposed_rows) != 1:
        raise AssertionError(f"expected one Proposed row, got {len(proposed_rows)}")
    row = proposed_rows[0]
    return row, _capture_identity(model, row)


class EndpointPairIdentityInvestigationTest(unittest.TestCase):
    def test_preview_then_apply_without_topology_change(self):
        model = _model_with_unrelated_edge_first()
        row, identity = _preview(model)

        current_index = _verified_reference_apply(model, row, identity)

        self.assertEqual(current_index, identity.preview_edge_index)
        self.assertEqual(model.edges[current_index].start_z, 100.0)
        self.assertIsNone(model.nodes[2].z)

    def test_preview_delete_other_edge_then_apply_resolves_shifted_index(self):
        model = _model_with_unrelated_edge_first()
        row, identity = _preview(model)
        del model.edges[0]

        current_index = _verified_reference_apply(model, row, identity)

        self.assertNotEqual(current_index, identity.preview_edge_index)
        self.assertEqual((model.edges[current_index].a, model.edges[current_index].b), (2, 3))
        self.assertEqual(model.edges[current_index].start_z, 100.0)

    def test_preview_add_new_edge_then_apply_keeps_unique_target_identity(self):
        model = _model_with_unrelated_edge_first()
        row, identity = _preview(model)
        model.nodes[20] = DummyNode(20)
        model.nodes[21] = DummyNode(21)
        model.edges.append(DummyEdge(20, 21))

        current_index = _verified_reference_apply(model, row, identity)

        self.assertEqual((model.edges[current_index].a, model.edges[current_index].b), (2, 3))
        self.assertEqual(model.edges[current_index].start_z, 100.0)
        self.assertIsNone(model.edges[-1].start_z)

    def test_multi_edge_with_same_endpoint_pair_hard_blocks_before_write(self):
        model = _model_with_unrelated_edge_first()
        row, identity = _preview(model)
        original_target = model.edges[identity.preview_edge_index]
        model.edges.append(DummyEdge(3, 2))

        with self.assertRaisesRegex(IdentityVerificationError, "multi_edge_endpoint_pair"):
            _verified_reference_apply(model, row, identity)

        self.assertIsNone(original_target.start_z)
        self.assertIsNone(model.edges[-1].end_z)


if __name__ == "__main__":
    unittest.main()
