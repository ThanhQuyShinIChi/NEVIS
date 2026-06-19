from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import Nevis_no_ui as nevis


class NodeZEdgeSlopeTest(unittest.TestCase):
    def test_new_model_objects_default_to_floor_zero_and_flat_slope(self):
        self.assertEqual(nevis.Node(1, 100.0, 200.0).z, 0.0)
        self.assertEqual(nevis.Edge(1, 2).slope, 0.0)

    def test_existing_positional_values_remain_supported(self):
        node = nevis.Node(1, 100.0, 200.0, 350.0, "1F_FL")
        edge = nevis.Edge(1, 2, "65", "DV", 0.02)

        self.assertEqual(node.z, 350.0)
        self.assertEqual(node.level_id, "1F_FL")
        self.assertEqual(edge.slope, 0.02)

    def test_legacy_project_data_without_fields_uses_zero_defaults(self):
        node = nevis.node_from_project_data(1, {"x": 100, "y": 200})
        edge = nevis.edge_from_project_data({"a": 1, "b": 2})

        self.assertEqual(node.z, 0.0)
        self.assertEqual(edge.slope, 0.0)

    def test_null_or_blank_project_values_use_zero_defaults(self):
        null_node = nevis.node_from_project_data(1, {"x": 0, "y": 0, "z": None})
        blank_edge = nevis.edge_from_project_data({"a": 1, "b": 2, "slope": ""})

        self.assertEqual(null_node.z, 0.0)
        self.assertEqual(blank_edge.slope, 0.0)

    def test_project_payload_persists_zero_defaults(self):
        model = nevis.PipeModel(
            nodes={1: nevis.Node(1, 0.0, 0.0), 2: nevis.Node(2, 100.0, 0.0)},
            edges=[nevis.Edge(1, 2)],
        )
        owner = type("PayloadHarness", (), {
            "model": model,
            "lang": "vi",
            "selected_node": None,
            "selected_edge": None,
            "selected_bushing_id": None,
            "current_project_path": None,
        })()

        payload = nevis.MainWindow._project_payload(owner)

        self.assertEqual(payload["nodes"]["1"]["z"], 0.0)
        self.assertEqual(payload["edges"][0]["slope"], 0.0)


if __name__ == "__main__":
    unittest.main()
