from __future__ import annotations

import copy
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QRawFont
from PySide6.QtWidgets import QApplication, QGraphicsScene, QMainWindow

import Nevis_no_ui as nevis


class PreviewHolder:
    def __init__(self):
        self.scene = QGraphicsScene()


class PreviewHost(QMainWindow):
    def __init__(self, lang: str = "jp"):
        super().__init__()
        self.lang = lang
        self.model = nevis.PipeModel(
            nodes={
                1: nevis.Node(1, 0.0, 0.0),
                2: nevis.Node(2, 100.0, 0.0),
                3: nevis.Node(3, 200.0, 0.0),
            },
            edges=[
                nevis.Edge(1, 2, end_z=100.0),
                nevis.Edge(2, 3),
            ],
        )
        self.preview = PreviewHolder()
        self.selected_edge = "1-2"

    def tr(self, key: str) -> str:
        return nevis.APP_TEXT[self.lang].get(key, key)


class ElevationPreviewUiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.host = PreviewHost()
        self.dialog = nevis.ElevationPreviewDialog(self.host)

    def tearDown(self):
        self.dialog.close()
        self.host.close()

    def test_dry_run_is_read_only_and_populates_summary_and_table(self):
        before = copy.deepcopy(self.host.model)

        self.dialog.run_dry_run()

        self.assertEqual(self.host.model, before)
        self.assertEqual(self.dialog.table.rowCount(), 1)
        self.assertEqual(self.dialog.summary_labels["proposed"].text(), "提案  1")
        self.assertEqual(self.dialog.table.item(0, 0).text(), "提案")
        self.assertEqual(self.dialog.table.item(0, 1).text(), "配管 2-3 / 開始")
        self.assertEqual(self.dialog.table.item(0, 3).text(), "100")

    def test_runtime_language_change_retranslates_without_rerunning_pipeline(self):
        self.dialog.run_dry_run()
        report = self.dialog.report
        self.host.lang = "vi"

        self.dialog.retranslate_ui()

        self.assertIs(self.dialog.report, report)
        self.assertEqual(self.dialog.lbl_title.text(), "Báo cáo tính thử cao độ")
        self.assertEqual(self.dialog.table.item(0, 0).text(), "Đề xuất")
        self.assertNotIn("Proposed", self.dialog.table.item(0, 0).text())

    def test_row_selection_draws_overlay_without_changing_normal_selection(self):
        self.dialog.run_dry_run()
        selected_before = self.host.selected_edge

        self.dialog.table.selectRow(0)
        QApplication.processEvents()

        self.assertEqual(self.host.selected_edge, selected_before)
        self.assertEqual(len(self.dialog.highlight_items), 2)
        self.assertEqual(len(self.host.preview.scene.items()), 2)

    def test_dialog_contains_no_apply_action(self):
        button_texts = [button.text() for button in self.dialog.findChildren(nevis.QPushButton)]

        self.assertEqual(button_texts, ["高低差を試算"])

    def test_selected_font_covers_japanese_and_vietnamese_glyphs(self):
        raw = QRawFont.fromFont(self.dialog.font())

        self.assertTrue(raw.isValid())
        for character in "高低差Đềộử":
            self.assertTrue(raw.supportsCharacter(ord(character)), character)


if __name__ == "__main__":
    unittest.main()
