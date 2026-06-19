import os
import math
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("NEVIS_SKIP_LICENSE", "1")

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

import Nevis_no_ui as nevis


class PdfUnderlayWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = nevis.MainWindow()
        self.window.resize(1400, 850)
        self.window.show()
        QApplication.processEvents()

    def tearDown(self):
        self.window.close()
        QApplication.processEvents()

    def test_underlay_ignores_repeated_mouse_clicks(self):
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("white"))
        self.window._reference_background_pixmap = pixmap
        self.window.ensure_reference_background()
        self.window.preview.fit_view()
        QApplication.processEvents()

        item = nevis._nevis_reference_background_item(self.window)
        self.assertIsNotNone(item)
        self.assertEqual(item.acceptedMouseButtons(), Qt.NoButton)
        self.assertIsNone(self.window.preview._interactive_item_data(item))

        errors = []
        old_hook = sys.excepthook
        sys.excepthook = lambda *args: errors.append(args)
        try:
            pos = self.window.preview.mapFromScene(item.sceneBoundingRect().center())
            for _ in range(4):
                QTest.mouseClick(self.window.preview.viewport(), Qt.LeftButton, pos=pos)
                QTest.mouseClick(self.window.preview.viewport(), Qt.RightButton, pos=pos)
                QApplication.processEvents()
        finally:
            sys.excepthook = old_hook
        self.assertEqual(errors, [])

    def test_empty_main_size_does_not_lock_workflow(self):
        self.window.cmb_main_size.setCurrentText("")
        self.window.update_workflow_state(False)

        for name in ("g_sel", "g_jww", "center_panel", "right_panel"):
            self.assertTrue(getattr(self.window, name).isEnabled(), name)

        self.window.apply_common()
        self.assertEqual(
            self.window.statusBar().currentMessage(),
            "Vui lòng nhập kích thước ống chính",
        )
        self.assertTrue(self.window.center_panel.isEnabled())

    def test_pipe_connect_command_starts_after_size_is_entered(self):
        self.window.cmb_main_size.setCurrentText("65")
        self.assertTrue(nevis._nevis_conn_v2_start_command(self.window.preview))
        self.assertEqual(self.window.orphan_connect_mode, "start")

    def test_pdf_toolbar_keeps_primary_controls_and_moves_transforms_to_menu(self):
        toolbar = self.window.preview_toolbar_layout
        for name in (
            "btn_detail_preview",
            "btn_center_undo",
            "btn_fit",
            "btn_open_reference_background",
            "chk_reference_background_visible",
            "lbl_reference_background_opacity",
        ):
            self.assertGreaterEqual(toolbar.indexOf(getattr(self.window, name)), 0, name)

        for name in ("btn_rot", "btn_fx", "btn_fy", "btn_clear_reference_background"):
            self.assertEqual(toolbar.indexOf(getattr(self.window, name)), -1, name)

        self.assertTrue(self.window.btn_align_reference_background.isEnabled())
        self.assertFalse(self.window.btn_scale_reference_background.isEnabled())
        self.assertEqual(
            [action.text() for action in self.window.menu_pdf_underlay.actions() if not action.isSeparator()],
            ["Nạp PDF/Ảnh...", "Xóa nền", "Xoay 180°", "Lật ngang", "Lật dọc"],
        )

    def test_align_underlay_snaps_two_degree_line_without_changing_model(self):
        pixmap = QPixmap(800, 600)
        pixmap.fill(QColor("white"))
        self.window._reference_background_pixmap = pixmap
        self.window.model.nodes = {1: nevis.Node(1, 400.0, 300.0)}
        self.window.model.edges = []
        for index, angle in enumerate(range(0, 360, 45), start=2):
            radians = math.radians(angle)
            self.window.model.nodes[index] = nevis.Node(
                index,
                400.0 + math.cos(radians) * 180.0,
                300.0 + math.sin(radians) * 180.0,
            )
            self.window.model.edges.append(nevis.Edge(1, index, "65"))
        model_snapshot = (
            {nid: (node.x, node.y) for nid, node in self.window.model.nodes.items()},
            [(edge.a, edge.b, edge.size) for edge in self.window.model.edges],
        )
        self.window.preview.draw_model()
        preview_transform = (
            nevis.PREVIEW_ROTATE_180,
            nevis.PREVIEW_FLIP_X,
            nevis.PREVIEW_FLIP_Y,
        )

        self.window.btn_align_reference_background.click()
        point_a = QPointF(100.0, 100.0)
        point_b = QPointF(600.0, 100.0 + math.tan(math.radians(2.0)) * 500.0)
        self.window.preview.fit_view()
        QApplication.processEvents()
        QTest.mouseClick(
            self.window.preview.viewport(),
            Qt.LeftButton,
            pos=self.window.preview.mapFromScene(point_a),
        )
        QTest.mouseClick(
            self.window.preview.viewport(),
            Qt.LeftButton,
            pos=self.window.preview.mapFromScene(point_b),
        )
        QApplication.processEvents()

        self.assertAlmostEqual(self.window._reference_background_rotation, -2.0, delta=0.2)
        self.assertTrue(self.window.lbl_reference_background_angle.text().startswith("Góc hiện tại: "))
        self.assertTrue(self.window.lbl_reference_background_angle.text().endswith("°"))
        self.assertEqual(
            (
                {nid: (node.x, node.y) for nid, node in self.window.model.nodes.items()},
                [(edge.a, edge.b, edge.size) for edge in self.window.model.edges],
            ),
            model_snapshot,
        )
        self.assertEqual(
            (nevis.PREVIEW_ROTATE_180, nevis.PREVIEW_FLIP_X, nevis.PREVIEW_FLIP_Y),
            preview_transform,
        )

        self.window.preview.draw_model()
        item = nevis._nevis_reference_background_item(self.window)
        self.assertIsNotNone(item)
        self.assertAlmostEqual(item.rotation(), -2.0, delta=0.2)

    def test_align_underlay_snaps_near_vertical_line_to_ninety_degrees(self):
        pixmap = QPixmap(800, 600)
        pixmap.fill(QColor("white"))
        self.window._reference_background_pixmap = pixmap
        self.window.ensure_reference_background()
        self.window.btn_align_reference_background.click()

        point_a = QPointF(300.0, 50.0)
        length = 500.0
        point_b = QPointF(
            point_a.x() + math.cos(math.radians(88.0)) * length,
            point_a.y() + math.sin(math.radians(88.0)) * length,
        )
        self.window.handle_reference_background_alignment_click(point_a)
        self.window.handle_reference_background_alignment_click(point_b)
        self.assertAlmostEqual(self.window._reference_background_rotation, 2.0, places=2)


if __name__ == "__main__":
    unittest.main()
