from __future__ import annotations

import os
import unittest
from dataclasses import dataclass

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import Nevis_no_ui as nevis


@dataclass
class DummyModel:
    start_z: float | None = None
    end_z: float | None = None


class UndoHarness:
    def __init__(self):
        self.model = DummyModel()
        self.selected_node = 10
        self.selected_edge = "1-2"
        self.selected_bushing_id = 20
        self.pending_reducer = None
        self._nevis_undo_stack = []
        self._nevis_undo_limit = 3
        self.undo_snapshot = None


def _begin(owner: UndoHarness, reason: str = "apply_elevation_proposals"):
    return nevis.MainWindow.begin_model_transaction(owner, reason)


def _commit(owner: UndoHarness, token) -> bool:
    return nevis.MainWindow.commit_model_transaction(owner, token)


def _rollback(owner: UndoHarness, token) -> bool:
    return nevis.MainWindow.rollback_model_transaction(owner, token)


def _snapshot(action: str, value: float) -> dict:
    return {
        "action": action,
        "model": DummyModel(start_z=value),
        "selected_node": None,
        "selected_edge": None,
        "selected_bushing_id": None,
    }


class UndoTransactionTest(unittest.TestCase):
    def test_begin_captures_pre_state_without_pushing_stack(self):
        owner = UndoHarness()

        token = _begin(owner)

        self.assertIsNotNone(token)
        self.assertEqual(owner._nevis_undo_stack, [])
        self.assertIsNone(owner.undo_snapshot)
        self.assertIsNone(token.snapshot["model"].start_z)

    def test_commit_pushes_exactly_one_snapshot(self):
        owner = UndoHarness()
        token = _begin(owner)
        owner.model.start_z = 100.0

        committed = _commit(owner, token)

        self.assertTrue(committed)
        self.assertEqual(len(owner._nevis_undo_stack), 1)
        self.assertIs(owner.undo_snapshot, owner._nevis_undo_stack[0])
        self.assertEqual(owner.undo_snapshot["action"], "apply_elevation_proposals")
        self.assertIsNone(owner.undo_snapshot["model"].start_z)
        self.assertEqual(owner.model.start_z, 100.0)

    def test_rollback_restores_model_and_creates_no_ghost_snapshot(self):
        owner = UndoHarness()
        existing = _snapshot("existing", 5.0)
        owner._nevis_undo_stack = [existing]
        owner.undo_snapshot = existing
        token = _begin(owner)
        owner.model.start_z = 100.0
        owner.model.end_z = 200.0
        owner.selected_node = 99

        rolled_back = _rollback(owner, token)

        self.assertTrue(rolled_back)
        self.assertIsNone(owner.model.start_z)
        self.assertIsNone(owner.model.end_z)
        self.assertEqual(owner.selected_node, 10)
        self.assertEqual(owner._nevis_undo_stack, [existing])
        self.assertIs(owner.undo_snapshot, existing)

    def test_commit_with_full_stack_trims_to_latest_three(self):
        owner = UndoHarness()
        first = _snapshot("first", 1.0)
        second = _snapshot("second", 2.0)
        third = _snapshot("third", 3.0)
        owner._nevis_undo_stack = [first, second, third]
        owner.undo_snapshot = third
        token = _begin(owner)
        owner.model.start_z = 100.0

        committed = _commit(owner, token)

        self.assertTrue(committed)
        self.assertEqual(len(owner._nevis_undo_stack), 3)
        self.assertEqual(
            [item["action"] for item in owner._nevis_undo_stack],
            ["second", "third", "apply_elevation_proposals"],
        )

    def test_nested_transaction_is_blocked(self):
        owner = UndoHarness()
        first = _begin(owner, "first")

        second = _begin(owner, "second")

        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertTrue(_rollback(owner, first))

    def test_token_from_another_owner_is_blocked(self):
        first_owner = UndoHarness()
        second_owner = UndoHarness()
        token = _begin(first_owner)

        self.assertFalse(_commit(second_owner, token))
        self.assertFalse(_rollback(second_owner, token))
        self.assertEqual(second_owner._nevis_undo_stack, [])
        self.assertTrue(_rollback(first_owner, token))


if __name__ == "__main__":
    unittest.main()
