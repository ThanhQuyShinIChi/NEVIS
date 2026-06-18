from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from unittest.mock import patch

from modules.elevation_anchor import AnchorDiscoveryResult, FrontierItem
from modules.elevation_wavefront import build_elevation_wavefront


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


class ElevationWavefrontTest(unittest.TestCase):
    def test_reads_anchor_result_from_b1(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2)},
            edges=[DummyEdge(1, 2)],
        )
        fake_b1 = AnchorDiscoveryResult(
            initial_frontier=[
                FrontierItem(
                    kind="node",
                    node_id=1,
                    z=0.0,
                    source="node.level_id",
                    level_id="1F_FL",
                )
            ]
        )

        with patch("modules.elevation_wavefront.discover_elevation_anchors", return_value=fake_b1) as discover:
            result = build_elevation_wavefront(model)

        discover.assert_called_once_with(model)
        self.assertIs(result.b1_result, fake_b1)
        self.assertEqual(len(result.wavefront_nodes), 1)
        self.assertEqual(len(result.candidate_paths), 1)
        self.assertEqual(result.candidate_paths[0].target_edge_index, 0)
        self.assertEqual(result.candidate_paths[0].target_endpoint, "start")

    def test_known_endpoint_anchor_creates_wavefront_candidate_path(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )

        result = build_elevation_wavefront(model)

        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(len(result.wavefront_nodes), 1)
        self.assertEqual(len(result.candidate_paths), 1)
        candidate = result.candidate_paths[0]
        self.assertEqual(candidate.source_kind, "edge_endpoint")
        self.assertEqual(candidate.source_edge_index, 0)
        self.assertEqual(candidate.source_endpoint, "end")
        self.assertEqual(candidate.source_z, 100.0)
        self.assertEqual(candidate.target_edge_index, 1)
        self.assertEqual(candidate.target_endpoint, "start")
        self.assertEqual(candidate.target_node_id, 2)
        self.assertEqual(candidate.degree, 2)

    def test_wavefront_does_not_mutate_model(self):
        model = DummyPipeModel(
            nodes={
                1: DummyNode(1, z=999.0, level_id="1F_FL"),
                2: DummyNode(2),
                3: DummyNode(3),
            },
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
            level_datums={"1F_FL": DummyLevelDatum("1F_FL", 0.0)},
        )
        before = copy.deepcopy(model)

        build_elevation_wavefront(model)

        self.assertEqual(model, before)

    def test_wavefront_does_not_create_new_elevation_values(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3),
            ],
        )

        result = build_elevation_wavefront(model)

        self.assertEqual(len(result.candidate_paths), 1)
        candidate = result.candidate_paths[0]
        self.assertFalse(hasattr(candidate, "target_z"))
        self.assertFalse(hasattr(candidate, "proposed_z"))
        self.assertIsNone(model.edges[1].start_z)
        self.assertIsNone(model.edges[1].end_z)

    def test_wavefront_does_not_overwrite_known_endpoint_values(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2), 3: DummyNode(3)},
            edges=[
                DummyEdge(1, 2, end_z=100.0),
                DummyEdge(2, 3, start_z=200.0),
            ],
        )

        result = build_elevation_wavefront(model)

        self.assertEqual(result.known_endpoint_z[(0, "end")], 100.0)
        self.assertEqual(result.known_endpoint_z[(1, "start")], 200.0)
        self.assertEqual(model.edges[0].end_z, 100.0)
        self.assertEqual(model.edges[1].start_z, 200.0)
        self.assertEqual(result.candidate_paths, [])


if __name__ == "__main__":
    unittest.main()
