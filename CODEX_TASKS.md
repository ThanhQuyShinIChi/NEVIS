# CODEX TASKS — NEVIS Building Space Model

Danh sách nhiệm vụ theo thứ tự ưu tiên. Mỗi task độc lập, commit riêng.
Khi hoàn thành: đánh dấu `[x]`, commit, push lên `feature/building-space-model`.

---

## Quy tắc chung

- Branch: `feature/building-space-model`
- Mỗi task phải có ít nhất 1 file test mới (pure logic, không cần Qt)
- Chạy `python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py` trước khi commit
- Hiện tại: **104 tests PASS** — không được làm regression
- Python 3.11: không dùng f-string lồng nháy đôi

---

## ✅ TASK 1–5 — Elevation Feature (DONE)

Task 1–5 đã hoàn thành. 104 tests pass. Không sửa các file elevation.

---

## ✅ TASK 6–29 — Building Space Model + Section View (DONE)

Task 6–29 đã hoàn thành. 245 tests pass. Commit cuối: `b9b6b81`.
- Task 6–21: data model, vẽ kết cấu, trục tọa độ, cao độ SL
- Task 22: xem Task 22 bên dưới (chưa làm)
- Task 23–29: sidebar compact, responsive toolbar, section view, stepped slab, unified render, scale thật, SL datum, marker, zoom/pan
- GUI xác nhận: section ổn định, sàn giật cấp đúng, sidebar/toolbar ok

---

## TASK 6 — Data model cho StructuralElement `[x]` (DONE)

**Mục tiêu:** Định nghĩa dataclass cho các phần tử kết cấu, lưu/load được trong file project.

**Các loại phần tử (element_type):**
| type | Tiếng Việt | Tiếng Nhật | Ghi chú |
|------|-----------|-----------|---------|
| `slab` | Sàn BT | スラブ | Có mặt trên, độ dày |
| `beam` | Dầm | 梁 | W × H, cao độ đáy dầm |
| `column` | Cột | 柱 | W × D, có thể hình tròn |
| `wall_rc` | Tường BT | RC壁 | Dày, cao |
| `wall_lgs` | Vách thạch cao | 軽量鉄骨壁 | Khung LGS + tấm thạch cao |
| `ceiling` | Trần | 天井 | Trần treo kiểu Nhật (軽天) |

**Yêu cầu:**

1. Tạo `modules/structural_element.py`:

```python
@dataclass
class StructuralElement:
    id: int
    element_type: str          # "slab", "beam", "column", "wall_rc", "wall_lgs", "ceiling"
    label: str = ""

    # Geometry (mm) — polygon hoặc rectangle
    points: list[tuple[float, float]] = field(default_factory=list)
    # Với rectangle: points = [(x0,y0), (x1,y0), (x1,y1), (x0,y1)]
    # Với arc: dùng arc_cx, arc_cy, arc_r thêm vào

    # Dimensions (mm)
    width: float = 0.0         # W — chiều ngang
    length: float = 0.0        # L — chiều dài
    height: float = 0.0        # H — chiều cao / độ dày
    arc_radius: float = 0.0    # C — bán kính cung (0 = không có)

    # Elevation (mm, relative to SL = ±0)
    top_elevation: float = 0.0     # mặt trên so với SL
    bottom_elevation: float = 0.0  # mặt dưới so với SL (= top - height)

    # Wall LGS specific
    stud_spacing: float = 303.0    # khoảng cách khung (303 hoặc 455 mm — chuẩn Nhật)
    stud_width: float = 65.0       # chiều rộng thanh LGS (65 hoặc 100 mm)
    board_thickness: float = 12.5  # độ dày tấm thạch cao (mm)
    board_layers: int = 1          # số lớp tấm (1 hoặc 2)

    # Slab stepped (sàn giật cấp)
    is_stepped: bool = False
    parent_slab_id: int = -1       # id sàn chính (-1 = không có)
    overlap_width: float = 0.0     # độ rộng vùng chồng lấn với sàn chính (mm)
```

2. Hàm `structural_element_to_dict(e: StructuralElement) -> dict` và `structural_element_from_dict(d: dict) -> StructuralElement`
3. File cũ không có `structural_elements` → load thành list rỗng, không crash
4. Thêm `structural_elements: list[StructuralElement]` vào `ProjectModel` (hoặc tương đương trong `Nevis_no_ui.py`)

**Test file:** `tests/test_structural_element.py`
- Round-trip serialize/deserialize cho từng element_type
- Load dict thiếu field → default an toàn
- `bottom_elevation` tự tính = `top_elevation - height`

---

## TASK 7 — Vẽ Rectangle trên canvas (công cụ vẽ kết cấu) `[  ]`

**Mục tiêu:** Người dùng click-drag trên canvas để vẽ hình chữ nhật đại diện cho phần tử kết cấu.

**Yêu cầu:**

1. Thêm nút **"Vẽ kết cấu"** (構造要素) vào toolbar canvas
2. Khi bật mode này:
   - Click điểm 1 → kéo → thả điểm 2 → tạo `StructuralElement` với `points` là 4 góc
   - Hiện rubber-band rectangle khi kéo (preview)
   - Bắt điểm (snap) theo grid hoặc theo điểm node MEP gần nhất (tolerance 10px)
3. Sau khi thả:
   - Mở dialog nhỏ hỏi: **Loại phần tử** (dropdown: Sàn/Dầm/Cột/Tường RC/Vách LGS/Trần)
   - **W, L** tự điền từ kích thước vừa kéo (mm, làm tròn)
   - Người dùng có thể sửa W, L trực tiếp trong dialog
   - Bấm OK → lưu vào model
4. Phần tử được vẽ trên canvas bằng nét đứt màu xám, label ở tâm

**Snap theo nền (underlay):**
- Nếu có PDF/JWW/DXF underlay đang hiển thị → snap theo grid của underlay
- Nếu không có nền → snap tự do (free-point)

**Test file:** `tests/test_structural_geometry.py`
- Hàm `rect_from_two_points(p1, p2) -> list[tuple]` trả về 4 góc đúng thứ tự
- Hàm `snap_to_grid(x, y, grid_mm) -> tuple` làm tròn đúng
- Hàm `nearest_snap_point(x, y, candidates, tolerance) -> tuple | None`

---

## TASK 8 — Nhập kích thước trực tiếp (W, L, H, C) `[  ]`

**Mục tiêu:** Ngoài kéo chuột, người dùng có thể nhập số liệu chính xác.

**Yêu cầu:**

1. Trong dialog sau khi vẽ (Task 7) hoặc khi click vào phần tử đã vẽ:
   - Field **W** (mm) — chiều rộng
   - Field **L** (mm) — chiều dài
   - Field **H** (mm) — chiều cao / độ dày
   - Field **C** (mm) — bán kính cung (ẩn mặc định, hiện khi tick "Có cung tròn")
2. Khi thay đổi W hoặc L → canvas cập nhật hình dạng phần tử ngay (live preview)
3. Validation: W, L, H > 0; C ≥ 0; tất cả ≤ 99999 mm

**Test file:** `tests/test_structural_input.py` (pure, không Qt)
- `validate_dimension(value, name) -> tuple[float, str]` — test các case lỗi
- `rect_from_center_wl(cx, cy, w, l) -> list[tuple]` — test geometry

---

## TASK 9 — Di chuyển và resize phần tử kết cấu `[  ]`

**Mục tiêu:** Sau khi vẽ, người dùng có thể kéo để di chuyển hoặc kéo góc để resize.

**Yêu cầu:**

1. Click vào phần tử → hiện 8 handle (4 góc + 4 cạnh giữa) màu xanh
2. Kéo handle góc → resize (giữ tỷ lệ nếu giữ Shift)
3. Kéo vào bên trong (không trúng handle) → di chuyển toàn bộ
4. Undo/redo hỗ trợ (lưu snapshot trước khi thay đổi)
5. Snap vẫn hoạt động khi kéo

**Test file:** `tests/test_structural_transform.py`
- `move_element(elem, dx, dy) -> StructuralElement` — test points dịch chuyển đúng
- `resize_element(elem, handle, new_pos) -> StructuralElement` — test W, L cập nhật đúng

---

## TASK 10 — Sàn giật cấp (stepped slab) `[  ]`

**Mục tiêu:** Tạo sàn giật cấp bên trong vùng sàn chính.

**Workflow:**

1. Chọn một `StructuralElement` loại `slab` đã vẽ
2. Bấm nút **"Tạo sàn giật cấp"**
3. Dialog hiện ra hỏi:
   - **Mặt sàn giật cấp** = SL - ? mm (ví dụ: -200mm, tức thấp hơn SL 200mm)
   - **Độ dày BT** (mm)
   - **Độ rộng chồng lấn** với sàn chính (mm) — vùng overlap để đổ BT liên tục
4. Người dùng vẽ vùng con bên trong sàn chính → tạo `StructuralElement` mới với:
   - `is_stepped = True`
   - `parent_slab_id = id sàn chính`
   - `overlap_width` = giá trị nhập
   - `top_elevation` = SL - giá trị nhập
5. Canvas hiển thị vùng giật cấp bằng hatch pattern khác với sàn chính

**Constraint:**
- Vùng giật cấp phải nằm trong bounds của sàn chính (validate)
- Một sàn chính có thể có nhiều sàn giật cấp

**Test file:** `tests/test_stepped_slab.py`
- `validate_stepped_slab_bounds(parent, child) -> bool` — child phải trong parent
- `compute_stepped_slab_elevation(sl_elevation, offset_mm) -> float`
- Round-trip serialize sàn giật cấp → load lại đúng `parent_slab_id`

---

## Ghi chú kỹ thuật

| File | Vai trò |
|------|---------|
| `Nevis_no_ui.py` | File chính ~25k dòng. Dùng grep tìm symbol, không đọc toàn bộ |
| `modules/structural_element.py` | NEW — dataclass + serialize/deserialize |
| `modules/elevation_display.py` | Đã có — pure helpers elevation, không sửa |
| `modules/elevation_apply.py` | Đã có — Apply Engine, không sửa |
| `tests/test_elevation_*.py` | 104 tests PASS — không được regression |

**Chuẩn Nhật cần biết:**
- LGS stud spacing: 303mm (1尺) hoặc 455mm (1.5尺)
- LGS stud width: 65mm (standard) hoặc 100mm (sound insulation)
- Gypsum board: 12.5mm hoặc 15mm, thường 2 lớp ở vách chống cháy
- 軽天 (keiten) ceiling: thanh C-channel treo từ slab, khoảng cách 303mm hoặc 455mm
- SL = Structural Level = mặt trên sàn BT hoàn thiện = cốt ±0 của tầng

---

## TASK 11 — Mode switch MEP / Kết cấu `[  ]`

**Mục tiêu:** Chuyển đổi giữa 2 workspace rõ ràng, panel và toolbar thay đổi theo mode.

**Yêu cầu:**
1. Thêm 2 nút lớn ở đầu panel trái: **"MEP / Đường ống"** và **"Kết cấu"**
2. Khi bật mode Kết cấu:
   - Panel trái ẩn toàn bộ section MEP (thiết lập chung, vật liệu, cụm ống)
   - Hiện section kết cấu: danh sách loại phần tử (Sàn/Dầm/Cột/Tường RC/Vách LGS/Trần), nút "Vẽ", nút "Xóa"
   - JWW/Thao tác section ở dưới canvas ẩn đi
3. Khi bật mode MEP: trở về giao diện hiện tại, ẩn section kết cấu
4. Mode mặc định: MEP
5. Lưu mode hiện tại vào project file, restore khi mở lại

**Test file:** `tests/test_workspace_mode.py` (pure logic)
- `get_default_mode()` → `"mep"`
- Mode serialize/deserialize trong project payload

---

## TASK 12 — Grid snap + hiển thị lưới `[  ]`

**Mục tiêu:** Vẽ kết cấu bắt điểm vào lưới cố định, không giật, chuẩn xác.

**Yêu cầu:**
1. Lưới mặc định: 303mm (1尺 Nhật). Cho phép chọn: 303 / 455 / 910 / tùy chỉnh mm
2. Hiện lưới mờ trên canvas khi ở mode Kết cấu (chấm xám nhạt, không che bản nền)
3. Khi vẽ hoặc kéo phần tử: snap tọa độ vào điểm lưới gần nhất
4. Checkbox "Bật lưới" để tắt/bật
5. Lưới tự scale theo zoom

**Test file:** `tests/test_structural_geometry.py` (bổ sung)
- `snap_to_grid(x, y, grid_mm) -> tuple` đã có — bổ sung test thêm
- `grid_points_in_view(x0, y0, x1, y1, grid_mm, max_points=2000) -> list` — không vượt quá max_points

---

## TASK 13 — Căn tỷ lệ bản nền `[  ]`

**Mục tiêu:** Người dùng click 2 điểm trên bản nền PDF/JWW, nhập khoảng cách thực → tự tính scale.

**Yêu cầu:**
1. Nút **"Căn tỷ lệ"** trên toolbar canvas (hiện ở cả 2 mode)
2. Khi bấm: hướng dẫn "Click điểm 1..." → "Click điểm 2..." → dialog nhập khoảng cách thực (mm)
3. Tính `scale = distance_real / distance_canvas` → lưu vào model
4. Hiện tỷ lệ hiện tại ở góc canvas (ví dụ "1:50")
5. Scale áp dụng cho tất cả tọa độ khi vẽ kết cấu

**Test file:** `tests/test_scale_calibration.py`
- `compute_scale(p1, p2, real_distance_mm) -> float`
- `canvas_to_real(x, y, scale, origin) -> tuple`
- `real_to_canvas(x, y, scale, origin) -> tuple`

---

## TASK 14 — Trục tọa độ 通り芯 (Toori-shin) `[  ]`

**Mục tiêu:** Hệ lưới trục chuẩn Nhật hiển thị trên canvas, snap kết cấu vào giao điểm trục.

**Yêu cầu:**

1. Tạo `modules/grid_axis.py`:
```python
@dataclass
class GridAxis:
    name: str          # "X1", "X2", "Y1", "Y2"...
    direction: str     # "X" (dọc) hoặc "Y" (ngang)
    position: float    # tọa độ canvas (mm)
```

2. UI nhập trục (trong panel Kết cấu):
   - Danh sách trục X: tên + khoảng cách (mm). Ví dụ: X1=0, X2=3640, X3=7280
   - Danh sách trục Y: tương tự
   - Nút "Thêm trục", "Xóa trục"

3. Hiển thị trên canvas:
   - Đường trục màu đỏ mờ (opacity 40%), nét đứt
   - Nhãn tên trục (X1, X2...) ở đầu đường, font nhỏ màu đỏ
   - Hiện khi ở mode Kết cấu, ẩn khi mode MEP

4. Snap vào giao điểm trục khi vẽ/kéo phần tử kết cấu (tolerance 15px)

5. Lưu/load trục trong file project

**Test file:** `tests/test_grid_axis.py`
- Round-trip serialize/deserialize GridAxis
- `find_nearest_axis_intersection(x, y, axes, tolerance) -> tuple | None`
- `build_axis_intersections(x_axes, y_axes) -> list[tuple]`

---

## TASK 15 — Mặt cắt với cao trình GL/SL/FL/CH `[  ]`

**Mục tiêu:** Cửa sổ mặt cắt nổi hiển thị kết cấu và cao trình chuẩn Nhật.

**Hệ ký hiệu cao trình:**
| Ký hiệu | Ý nghĩa |
|---------|---------|
| GL | Ground Level — mặt đất tự nhiên |
| SL | Structural Level — mặt sàn BT thô = ±0 |
| FL | Finish Level — mặt sàn hoàn thiện = SL + lớp hoàn thiện |
| CH | Clear Height — từ FL lên đến đáy trần thạch cao |

**Yêu cầu:**

1. Nút **"Mặt cắt"** trên toolbar canvas (cả 2 mode)
2. Khi bấm: vẽ đường cắt trên mặt bằng (click 2 điểm)
3. Cửa sổ mặt cắt nổi hiện ra:
   - Trục đứng bên trái hiện ký hiệu: `GL`, `SL ±0`, `SL+xxx`, `SL-xxx`, `FL`, `CH↕`
   - Phần tử kết cấu (sàn/dầm/tường) hiện đúng vị trí cao độ
   - Đường ống MEP nếu cắt qua cũng hiện (màu khác)
4. Tự động tính và hiện:
   - FL = SL + finish_thickness (mặc định 30mm, chỉnh được)
   - CH = đáy trần (ceiling bottom_elevation) - FL
   - Hiện số CH bằng mũi tên 2 đầu ↕ kèm giá trị mm

**Test file:** `tests/test_section_view.py`
- `compute_fl(sl, finish_thickness) -> float`
- `compute_ch(ceiling_bottom, fl) -> float`
- `elements_intersect_cut_line(elements, p1, p2) -> list`
- `sort_elements_by_elevation(elements) -> list`

---

## TASK 16 — Vẽ kết cấu mượt (bỏ auto-snap khi kéo) `[  ]`

**Mục tiêu:** Khi kéo chuột vẽ sàn/dầm/cột không bị giật. Hiện tại snap vào lưới mỗi pixel → giật.

**Yêu cầu:**

1. Trong `mouseMoveEvent` của canvas khi đang vẽ kết cấu (draw mode):
   - **KHÔNG** snap tọa độ khi đang kéo → cứ để chuột chạy tự do mượt mà
   - Chỉ dùng tọa độ canvas thô (không qua `snap_to_grid`)

2. Trong `mouseReleaseEvent` (khi thả chuột):
   - **Lúc này mới** snap điểm cuối vào lưới gần nhất
   - Gọi `snap_to_grid(x, y, grid_mm)` từ `modules.structural_geometry`

3. Điểm đầu (click lần đầu / `mousePressEvent`):
   - Snap ngay vào lưới khi click

4. Preview rubber-band (hình chữ nhật tạm khi kéo):
   - Vẫn vẽ theo tọa độ chuột thực, không snap → nhìn mượt

**Tìm trong Nevis_no_ui.py:**
- Grep `mouseMoveEvent` gần từ khóa `structural` hoặc `draw_rect`
- Grep `snap_to_grid` để tìm chỗ đang gọi — comment out hoặc chuyển sang `mouseReleaseEvent`

**Test file:** Không cần test mới (logic snap đã có test ở `test_structural_geometry.py`)

---

## TASK 17 — Snap thủ công bằng chuột phải `[  ]`

**Mục tiêu:** Khi đang vẽ kết cấu, click chuột phải vào góc/cạnh của phần tử kết cấu khác hoặc đường nền → bắt điểm chính xác.

**Workflow:**

1. Đang trong draw mode (đang kéo vẽ)
2. User click chuột phải (**không phải trái**)
3. Hệ thống tìm điểm snap gần nhất trong bán kính 20px:
   - Góc của các `StructuralElement` đã vẽ (lấy từ `element.points`)
   - Giao điểm trục tọa độ X/Y (nếu có `grid_axes`)
4. Nếu tìm thấy → **gán điểm đó** làm điểm hiện tại (thay tọa độ chuột)
5. Hiện dấu chấm tròn xanh nhỏ để báo "đã bắt điểm"

**Tìm trong Nevis_no_ui.py:**
- Grep `contextMenuEvent` hoặc `RightButton` trong canvas
- Thêm logic snap vào đó, gọi `nearest_snap_point(x, y, candidates, tolerance=20)` từ `modules.structural_geometry`
- `candidates` = tất cả `points` của mọi `StructuralElement` trong `self.model.structural_elements`

**Test file:** Không cần test mới (logic đã có ở `test_structural_geometry.py`)

---

## TASK 18 — Hiển thị trục tọa độ 通り芯 trên canvas `[  ]`

**Mục tiêu:** Vẽ đường trục X1/X2/Y1/Y2 lên canvas như bản vẽ Nhật.

**Yêu cầu:**

1. Trong `paintEvent` hoặc hàm vẽ canvas của mode Kết cấu:
   - Lấy danh sách trục từ `getattr(self.model, "grid_axes", [])`
   - Mỗi `GridAxis` có: `name`, `direction` ("X" hoặc "Y"), `position` (tọa độ canvas mm)

2. Vẽ từng trục:
   - **Trục X** (direction="X"): đường thẳng đứng từ trên xuống dưới toàn canvas
   - **Trục Y** (direction="Y"): đường nằm ngang toàn canvas
   - Màu: đỏ mờ, opacity 40% — `QColor(220, 50, 50, 100)`
   - Nét đứt: `Qt.DashLine`
   - Độ dày: 1px

3. Nhãn tên trục (X1, X2, Y1...):
   - Vị trí: đầu trên của trục X, đầu trái của trục Y
   - Font nhỏ, màu đỏ đậm `QColor(180, 0, 0)`
   - Kích thước chữ: 10pt

4. Ẩn khi mode MEP, hiện khi mode Kết cấu

5. Lưu/load `grid_axes` vào project:
   - `_project_payload()`: thêm `"grid_axes": [grid_axis_to_dict(a) for a in getattr(self.model, "grid_axes", [])]`
   - `open_project()`: `self.model.grid_axes = [grid_axis_from_dict(d) for d in data.get("grid_axes", [])]`
   - Import: `from modules.grid_axis import GridAxis, grid_axis_to_dict, grid_axis_from_dict`

6. UI nhập trục đơn giản (trong panel Kết cấu):
   - Nút **"+ Thêm trục X"** → dialog hỏi tên (X1) và vị trí (mm)
   - Nút **"+ Thêm trục Y"** → tương tự
   - List hiện các trục đã có, click để xóa

**Tọa độ:** `position` là tọa độ canvas (mm). Khi vẽ cần convert sang pixel theo scale hiện tại của canvas.

**Test file:** Không cần test mới (logic đã có ở `test_grid_axis.py`)

---

## TASK 19 — Sửa UX vẽ kết cấu: icon, thoát lệnh, lưới `[ ]`

**Mục tiêu:** Workflow vẽ kết cấu phải chuẩn như phần mềm CAD chuyên nghiệp.

### 19a — Nút vẽ có icon riêng từng loại

Xóa dropdown chọn loại phần tử. Thay bằng **6 nút icon** nằm ngang:

| Nút | Icon gợi ý | Loại |
|-----|-----------|------|
| Sàn | hình chữ nhật ngang dày | `slab` |
| Dầm | hình chữ nhật ngang mỏng có gạch chéo | `beam` |
| Cột | hình vuông đặc | `column` |
| Tường RC | hình chữ nhật đứng có gạch chéo | `wall_rc` |
| Vách LGS | hình chữ nhật đứng có đường đứt | `wall_lgs` |
| Trần | hình chữ nhật ngang có chấm | `ceiling` |

- Click nút → bật draw mode cho loại đó, nút sáng lên (checked)
- Click lại hoặc nhấn **Escape** → thoát draw mode
- Chỉ 1 nút active cùng lúc

### 19b — Thoát lệnh vẽ

- Nhấn **Escape**: hủy hình đang vẽ, thoát draw mode
- **Click phải** khi đang kéo: hủy hình hiện tại (giữ draw mode để vẽ tiếp)
- Status bar hiện: `"Đang vẽ [Sàn] — Escape để thoát"` khi đang trong draw mode

### 19c — Checkbox "Bật lưới" phải hoạt động

- Khi tick → hiện lưới chấm mờ trên canvas + snap vào lưới khi click/thả
- Khi bỏ tick → ẩn lưới, vẽ tự do không snap
- Lưu trạng thái vào project

**Test file:** Không cần test mới

---

## TASK 20 — Sửa dialog trục tọa độ 通り芯 `[ ]`

**Mục tiêu:** Dialog "Thêm trục" phải đúng thứ tự thao tác, tên tự sinh, hỗ trợ đổi tên hàng loạt.

### 20a — Thứ tự dialog đúng

Dialog "Thêm trục" hiện tại sai thứ tự. Sửa lại:

```
[Chiều]  ○ X (dọc)   ○ Y (ngang)    ← chọn trước
[Tên]    X1                          ← tự sinh, user có thể sửa
[Vị trí (mm)]  0
[OK]  [Hủy]
```

- Khi chọn chiều X → tự điền tên = "X" + (số trục X hiện có + 1). VD: đã có X1, X2 → gợi ý "X3"
- Khi chọn chiều Y → tương tự "Y1", "Y2"...
- Tên luôn **chữ HOA** (X không phải x)

### 20b — Thứ tự hiển thị danh sách trục

Trong list trục đã có: hiện **X trước, Y sau**, mỗi nhóm sort theo position tăng dần.

Hiện tại bị đảo (Y1 hiện trước X2). Sửa lại.

### 20c — Đổi tên prefix hàng loạt

Thêm nút **"Đổi prefix"** bên cạnh list trục:
- Dialog hỏi: `Prefix cũ: [X]  →  Prefix mới: [Xr]`
- Nhấn OK → tất cả trục có tên bắt đầu bằng "X" đổi thành "Xr1", "Xr2"... (giữ số thứ tự)
- Ví dụ: X1, X2, X3 → Xr1, Xr2, Xr3

**Test file:** `tests/test_grid_axis.py` — thêm:
- `rename_axes_prefix(axes, old_prefix, new_prefix) -> list[GridAxis]`
- `auto_axis_name(axes, direction) -> str` — trả về tên gợi ý tiếp theo

---

## TASK 21 — Cao độ SL cho từng loại phần tử kết cấu `[ ]`

**Mục tiêu:** Mỗi phần tử kết cấu phải có cao độ so với SL. Đây là thông tin bắt buộc trong bản vẽ Nhật.

### Khái niệm cần hiểu

```
SL = 0 (cốt mặt sàn BT thô = ±0 của tầng)
FL = SL + lớp hoàn thiện (thường 30~50mm)
CH = đáy trần - FL (chiều cao thông thủy)
```

### Dialog sau khi vẽ: input khác nhau theo loại

**Sàn (slab):**
```
Mặt sàn so với SL:  [±0] mm   ← VD: 0 (bình thường), -200 (sàn WC)
Độ dày BT:          [150] mm
→ Hiện: "Mặt sàn = SL±0,  Đáy sàn = SL-150"
```

**Dầm (beam):**
```
Đáy dầm so với SL:  [-500] mm  ← âm = thấp hơn SL
Cao dầm H:          [600] mm
Rộng dầm W:         [300] mm
→ Hiện: "Đáy dầm = SL-500,  Đỉnh dầm = SL+100"
```

**Cột (column):**
```
Chân cột so với SL: [0] mm
Cao cột:            [2800] mm
Rộng W × Dài D:     [500] × [500] mm
```

**Tường RC / Vách LGS:**
```
Chân tường so với SL: [0] mm
Cao tường H:          [2800] mm
Dày tường:            [200] mm  (RC) / tự tính từ LGS (LGS)
```

**Trần (ceiling):**
```
Đáy trần so với SL:  [-2400] mm  ← âm = dưới SL của tầng trên
→ Tự tính CH = Đáy trần - FL
→ Hiện: "CH = 2360mm" (nếu FL = SL+40)
```

### Hiển thị trên canvas

Mỗi phần tử kết cấu đã vẽ → hiện nhãn nhỏ ở tâm:
- Sàn: `SL±0 / t150`
- Dầm: `GL-500 / 300×600`
- Cột: `500×500`
- Tường: `W200 / H2800`
- Trần: `CH=2360`

### Lưu vào model

Các field đã có trong `StructuralElement`:
- `top_elevation`, `bottom_elevation` → dùng để lưu so với SL
- `height`, `width`, `length` → kích thước

Chỉ cần cập nhật dialog để điền đúng các field này.

**Test file:** `tests/test_section_view.py` — thêm:
- `format_slab_label(top_elev, height) -> str`  → `"SL±0 / t150"`
- `format_beam_label(bottom_elev, h, w) -> str` → `"GL-500 / 300×600"`
- `format_ceiling_ch(ceiling_bottom, fl) -> str` → `"CH=2360"`

---

## TASK 22 — Clash Detection 2.5D: Ống xuyên kết cấu `[ ]`

**Mục tiêu:** Đây là tính năng cốt lõi của NEVIS — phát hiện xung đột giữa đường ống MEP và phần tử kết cấu (sàn, dầm, trần). Highlight đỏ các đoạn ống bị xung đột.

---

### Khái niệm 2.5D Clash

NEVIS không dùng mô hình 3D đầy đủ. Thay vào đó:

- **Đường ống MEP**: có tọa độ XY trên mặt bằng + cao độ Z (mm so với SL)
- **Phần tử kết cấu**: có outline XY (đa giác/hình chữ nhật) + dải cao độ [bottom_elevation, top_elevation]
- **Clash**: đoạn ống nằm trong vùng XY của phần tử kết cấu VÀ Z của ống nằm trong [bottom, top] của phần tử

Ví dụ thực tế:
```
Sàn BT: top_elevation=0, bottom_elevation=-150 (SL±0, dày 150mm)
Ống cấp nước: z=-80 → ống đang nằm TRONG sàn → CLASH ĐỎ
Ống thoát: z=-300 → ống dưới đáy sàn → bình thường
Dầm: top=0, bottom=-600 (đáy dầm SL-600, cao 600mm)
Ống: z=-400 → ống trong vùng dầm → CLASH ĐỎ
```

---

### 22a — Module pure logic: `modules/clash_detection.py`

Tạo file mới `modules/clash_detection.py`:

```python
"""2.5D clash detection — no Qt dependency."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ClashResult:
    pipe_id: int          # ID của đường ống
    element_id: int       # ID của phần tử kết cấu
    element_type: str     # "slab", "beam", "column", "wall_rc", "wall_lgs", "ceiling"
    clash_type: str       # "penetrate" | "too_close"
    overlap_mm: float     # Khoảng chồng lấn (mm) — dương = clash nặng


def point_in_polygon(px: float, py: float, polygon: list) -> bool:
    """Ray casting algorithm — kiểm tra điểm có trong đa giác không."""
    ...


def segment_intersects_polygon(p1: tuple, p2: tuple, polygon: list) -> bool:
    """True nếu đoạn thẳng p1→p2 có bất kỳ điểm nào nằm trong polygon."""
    ...


def check_elevation_clash(pipe_z: float, elem_bottom: float, elem_top: float,
                           clearance_mm: float = 50.0) -> tuple[bool, float]:
    """
    Kiểm tra Z ống có xung đột với dải cao độ phần tử không.
    Returns: (is_clash, overlap_mm)
    overlap_mm > 0: ống xuyên vào phần tử
    overlap_mm < 0: ống gần phần tử nhưng chưa chạm (< clearance_mm)
    """
    ...


def find_clashes(pipes: list, elements: list, clearance_mm: float = 50.0) -> list[ClashResult]:
    """
    Main function: kiểm tra tất cả pipe segments vs tất cả structural elements.
    pipes: list of objects với attrs: id, z_elevation, points (list of (x,y) tuples)
    elements: list of StructuralElement với attrs: id, element_type, points, top_elevation, bottom_elevation
    Returns: list[ClashResult]
    """
    ...
```

**Triển khai chi tiết:**

```python
def point_in_polygon(px, py, polygon):
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def segment_intersects_polygon(p1, p2, polygon):
    # Kiểm tra từng điểm mẫu trên đoạn thẳng
    steps = max(2, int(((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5 // 100) + 2)
    for k in range(steps + 1):
        t = k / steps
        px = p1[0] + t * (p2[0] - p1[0])
        py = p1[1] + t * (p2[1] - p1[1])
        if point_in_polygon(px, py, polygon):
            return True
    return False


def check_elevation_clash(pipe_z, elem_bottom, elem_top, clearance_mm=50.0):
    if elem_bottom <= pipe_z <= elem_top:
        # Ống nằm trong phần tử — clash nặng
        overlap = min(pipe_z - elem_bottom, elem_top - pipe_z)
        return True, overlap
    # Kiểm tra khoảng cách gần (< clearance_mm)
    if pipe_z < elem_bottom:
        gap = elem_bottom - pipe_z
    else:
        gap = pipe_z - elem_top
    if gap < clearance_mm:
        return True, -gap  # âm = chưa chạm nhưng quá gần
    return False, gap


def find_clashes(pipes, elements, clearance_mm=50.0):
    results = []
    for pipe in pipes:
        if not getattr(pipe, "points", None) or len(pipe.points) < 2:
            continue
        pipe_z = getattr(pipe, "z_elevation", 0.0)
        for elem in elements:
            if not getattr(elem, "points", None) or len(elem.points) < 3:
                continue
            elem_top = getattr(elem, "top_elevation", 0.0)
            elem_bottom = getattr(elem, "bottom_elevation", 0.0)
            # Bước 1: kiểm tra XY — có đoạn ống nào đi qua vùng kết cấu?
            xy_clash = False
            pts = pipe.points
            for i in range(len(pts) - 1):
                if segment_intersects_polygon(pts[i], pts[i+1], elem.points):
                    xy_clash = True
                    break
            if not xy_clash:
                continue
            # Bước 2: kiểm tra Z
            is_clash, overlap = check_elevation_clash(pipe_z, elem_bottom, elem_top, clearance_mm)
            if is_clash:
                clash_type = "penetrate" if overlap >= 0 else "too_close"
                results.append(ClashResult(
                    pipe_id=pipe.id,
                    element_id=elem.id,
                    element_type=elem.element_type,
                    clash_type=clash_type,
                    overlap_mm=overlap,
                ))
    return results
```

---

### 22b — Test file: `tests/test_clash_detection.py`

Tạo file mới `tests/test_clash_detection.py`:

```python
"""Tests for modules/clash_detection.py — no Qt dependency."""
import pytest
from modules.clash_detection import (
    point_in_polygon, segment_intersects_polygon,
    check_elevation_clash, find_clashes, ClashResult,
)


# --- point_in_polygon ---

def test_point_inside_square():
    poly = [(0,0),(100,0),(100,100),(0,100)]
    assert point_in_polygon(50, 50, poly) is True

def test_point_outside_square():
    poly = [(0,0),(100,0),(100,100),(0,100)]
    assert point_in_polygon(200, 200, poly) is False

def test_point_on_edge_treated_as_outside():
    # Ray casting không đảm bảo điểm trên cạnh, chỉ test trong/ngoài rõ ràng
    poly = [(0,0),(100,0),(100,100),(0,100)]
    assert point_in_polygon(-1, 50, poly) is False


# --- check_elevation_clash ---

def test_pipe_inside_slab():
    # Sàn: top=0, bottom=-150 — ống z=-80 → clash
    is_clash, overlap = check_elevation_clash(-80, -150, 0)
    assert is_clash is True
    assert overlap >= 0

def test_pipe_below_slab():
    # Ống z=-300 — dưới đáy sàn SL-150 → không clash
    is_clash, overlap = check_elevation_clash(-300, -150, 0)
    assert is_clash is False

def test_pipe_too_close_below():
    # Ống z=-170, clearance=50 → cách đáy sàn 20mm < 50 → too_close
    is_clash, overlap = check_elevation_clash(-170, -150, 0, clearance_mm=50)
    assert is_clash is True
    assert overlap < 0  # âm = chưa chạm nhưng quá gần

def test_pipe_above_element_ok():
    is_clash, _ = check_elevation_clash(100, -150, 0)
    assert is_clash is False

def test_pipe_exactly_on_top():
    # Đúng bằng top_elevation → nằm trong → clash
    is_clash, overlap = check_elevation_clash(0, -150, 0)
    assert is_clash is True


# --- segment_intersects_polygon ---

def test_segment_crosses_square():
    poly = [(0,0),(1000,0),(1000,1000),(0,1000)]
    # Đoạn từ (-100,500) đến (1100,500) cắt ngang qua hình vuông
    assert segment_intersects_polygon((-100,500), (1100,500), poly) is True

def test_segment_outside_square():
    poly = [(0,0),(100,0),(100,100),(0,100)]
    assert segment_intersects_polygon((200,0), (200,100), poly) is False


# --- find_clashes ---

class _MockPipe:
    def __init__(self, id, z, points):
        self.id = id
        self.z_elevation = z
        self.points = points

class _MockElem:
    def __init__(self, id, etype, points, top, bottom):
        self.id = id
        self.element_type = etype
        self.points = points
        self.top_elevation = top
        self.bottom_elevation = bottom


def test_find_clashes_one_clash():
    # Sàn 1000×1000, top=0, bottom=-150
    slab = _MockElem(1, "slab", [(0,0),(1000,0),(1000,1000),(0,1000)], 0, -150)
    # Ống đi xuyên qua giữa sàn, z=-80 (trong sàn)
    pipe = _MockPipe(1, -80, [(500,-100),(500,1100)])
    results = find_clashes([pipe], [slab])
    assert len(results) == 1
    assert results[0].clash_type == "penetrate"
    assert results[0].element_type == "slab"

def test_find_clashes_no_clash_z_ok():
    slab = _MockElem(1, "slab", [(0,0),(1000,0),(1000,1000),(0,1000)], 0, -150)
    # Ống đi qua vùng sàn nhưng z=-300 → dưới đáy, OK
    pipe = _MockPipe(1, -300, [(500,-100),(500,1100)])
    results = find_clashes([pipe], [slab])
    assert len(results) == 0

def test_find_clashes_no_clash_xy_miss():
    slab = _MockElem(1, "slab", [(0,0),(1000,0),(1000,1000),(0,1000)], 0, -150)
    # Ống không đi qua vùng sàn dù z phù hợp
    pipe = _MockPipe(1, -80, [(2000,0),(2000,1000)])
    results = find_clashes([pipe], [slab])
    assert len(results) == 0

def test_find_clashes_too_close():
    slab = _MockElem(1, "slab", [(0,0),(1000,0),(1000,1000),(0,1000)], 0, -150)
    # Ống z=-170 → cách đáy sàn 20mm < clearance 50mm → too_close
    pipe = _MockPipe(1, -170, [(500,-100),(500,1100)])
    results = find_clashes([pipe], [slab], clearance_mm=50)
    assert len(results) == 1
    assert results[0].clash_type == "too_close"

def test_find_clashes_multiple_pipes():
    slab = _MockElem(1, "slab", [(0,0),(1000,0),(1000,1000),(0,1000)], 0, -150)
    p1 = _MockPipe(1, -80, [(500,-100),(500,1100)])   # clash
    p2 = _MockPipe(2, -300, [(500,-100),(500,1100)])  # ok
    p3 = _MockPipe(3, -80, [(2000,0),(2000,1000)])    # xy miss
    results = find_clashes([p1, p2, p3], [slab])
    assert len(results) == 1
    assert results[0].pipe_id == 1
```

---

### 22c — UI: Highlight đỏ đoạn ống bị clash (trong `Nevis_no_ui.py`)

**Không cần thay đổi data model.** Chỉ cần:

1. **Import:**
   ```python
   from modules.clash_detection import find_clashes, ClashResult
   ```

2. **Thêm method `_run_clash_check(self)`** vào class `NEVISApp`:
   ```python
   def _run_clash_check(self):
       """Chạy clash detection và lưu kết quả vào self._clash_results."""
       pipes = getattr(self.model, "pipe_network", {}).get("pipes", [])
       elements = getattr(self.model, "structural_elements", [])
       self._clash_results = find_clashes(pipes, elements)
       clash_pipe_ids = {r.pipe_id for r in self._clash_results}
       self._clash_pipe_ids = clash_pipe_ids
       count = len(self._clash_results)
       if count:
           self.status_bar.showMessage("⚠ {} xung đột phát hiện — xem màu đỏ trên bản vẽ".format(count))
       else:
           self.status_bar.showMessage("✓ Không có xung đột")
   ```

3. **Nút "Kiểm tra clash"** trong panel MEP hoặc toolbar:
   - Label: `"🔍 Kiểm tra clash"`
   - Click → gọi `self._run_clash_check()` rồi `self.canvas.update()`

4. **Trong hàm vẽ pipe trên canvas** (hàm `paintEvent` hoặc tương đương):
   - Khi vẽ một pipe segment, kiểm tra `pipe.id in getattr(self, "_clash_pipe_ids", set())`
   - Nếu có → vẽ màu đỏ đậm (`QColor(220, 30, 30)`) thay màu bình thường
   - Có thể vẽ thêm icon ⚠ nhỏ tại điểm giữa đoạn ống bị clash

5. **Tự động chạy clash check** khi:
   - User thêm/xóa phần tử kết cấu
   - User thay đổi cao độ Z của ống

**Lưu ý quan trọng:**
- `_clash_pipe_ids` khởi tạo là `set()` trong `__init__`
- Clash check chạy **bất đồng bộ không cần thiết** — số lượng phần tử nhỏ, chạy đồng bộ OK
- Không lưu `_clash_results` vào file project (tính lại khi mở)

---

### Định nghĩa "pipe object" cần có

Module `find_clashes` cần pipe object có:
- `id: int`
- `z_elevation: float` — cao độ Z của ống so với SL (mm)
- `points: list[tuple[float, float]]` — danh sách điểm XY trên mặt bằng

Nếu trong `Nevis_no_ui.py` pipe object dùng tên khác (ví dụ `elevation` thay vì `z_elevation`), cần tạo **adapter** trong method `_run_clash_check`:

```python
class _PipeAdapter:
    def __init__(self, pipe):
        self.id = pipe.id
        self.z_elevation = getattr(pipe, "z_elevation", getattr(pipe, "elevation", 0.0))
        self.points = getattr(pipe, "points", [])

adapted_pipes = [_PipeAdapter(p) for p in pipes]
self._clash_results = find_clashes(adapted_pipes, elements)
```

---

**Test file:** `tests/test_clash_detection.py` (tạo mới — xem trên)

**Số test sau khi xong Task 22:** 240 tests

---

## TASK 23 — Sửa vẽ kết cấu: vẽ được tất cả loại, handle resize, panel gọn `[ ]`

**Mục tiêu:** Vẽ được đầy đủ 6 loại phần tử. Resize bằng handle. Panel bên trái gọn hơn.

---

### 23a — Vẽ được tất cả 6 loại phần tử

Hiện tại chỉ cột vẽ được, sàn vẽ ra đường, dầm/tường/trần chưa vẽ được. Nguyên nhân có thể là logic vẽ hình chữ nhật (drag từ góc đến góc) không được gán đúng cho từng loại.

Yêu cầu: **tất cả 6 loại đều vẽ bằng cách kéo drag** (click → kéo → thả):
- `slab`, `beam`, `column`, `wall_rc`, `wall_lgs`, `ceiling` → đều dùng chung cơ chế vẽ hình chữ nhật
- Preview hình chữ nhật mờ khi đang kéo
- Thả chuột → hiện dialog nhập kích thước/cao độ (đã có ở Task 21)

Kiểm tra lại code hiện tại — nếu `mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent` không xử lý đúng element_type → sửa lại.

---

### 23b — Resize handle (tay cầm kéo)

Khi click chọn 1 phần tử kết cấu → hiện **8 tay cầm** (handle) ở 4 góc + 4 cạnh:

```
◆ ─── ◆ ─── ◆
│               │
◆             ◆
│               │
◆ ─── ◆ ─── ◆
```

- Handle màu xanh dương, kích thước 8×8 px
- **Kéo góc**: resize cả chiều rộng lẫn chiều cao
- **Kéo cạnh**: resize một chiều
- Khi kéo handle → cập nhật `points` của phần tử realtime
- Sau khi thả → cập nhật lại dialog hoặc label trên canvas

**Trong code:**
- Thêm method `_get_element_handles(elem)` → trả về 8 điểm handle (pixel)
- Trong `mousePressEvent`: nếu click trúng handle → set `self._resize_handle_idx` và `self._resizing_elem`
- Trong `mouseMoveEvent`: nếu đang resize → tính toán lại `points` theo vị trí chuột
- Trong `mouseReleaseEvent`: kết thúc resize, lưu lại

---

### 23c — Panel tác vụ kết cấu gọn hơn

Panel bên trái hiện tại quá rộng. Yêu cầu:
- Chiều rộng panel kết cấu: **tối đa 180px** (bằng ~1/4 màn hình 720px)
- Ẩn tab **"Vật liệu"** và **"Kiểm tra ống"** khi đang ở mode Kết cấu
- Chỉ giữ lại: 6 nút vẽ icon + danh sách trục + nút Mặt cắt

---

### 23d — Nút active sáng rõ, cơ chế dừng rõ ràng

Hiện tại nút đang active không rõ màu. Yêu cầu:
- Nút đang active (draw mode bật): background `#1976D2` (xanh đậm), chữ trắng
- Các nút còn lại: background mặc định
- Nhấn **Escape**: thoát draw mode, tắt sáng tất cả nút, trở về mode select
- Nếu chưa có keyPressEvent xử lý Escape → thêm vào

---

### 23e — Scroll zoom bằng con lăn chuột

Hiện tại chưa có zoom bằng con lăn. Thêm vào `wheelEvent` của canvas:

```python
def wheelEvent(self, event):
    delta = event.angleDelta().y()
    factor = 1.15 if delta > 0 else (1 / 1.15)
    # Zoom tâm tại vị trí chuột
    mouse_pos = event.position()  # QPointF
    self._zoom_at(mouse_pos.x(), mouse_pos.y(), factor)
    event.accept()

def _zoom_at(self, cx, cy, factor):
    # Điều chỉnh offset để zoom tập trung vào điểm chuột
    self.scale *= factor
    self.offset_x = cx - (cx - self.offset_x) * factor
    self.offset_y = cy - (cy - self.offset_y) * factor
    self.update()
```

**Test file:** Không cần test mới (logic UI)

---

## TASK 24 — Panel thuộc tính đối tượng đang chọn `[ ]`

**Mục tiêu:** Khi chọn 1 phần tử → panel bên phải hiện thông tin + cho phép sửa trực tiếp.

---

### 24a — Panel thuộc tính (Properties Panel)

Thêm panel bên **phải** canvas, rộng 220px:

```
┌─────────────────────┐
│ ĐỐI TƯỢNG ĐANG CHỌN│
├─────────────────────┤
│ Loại:  Sàn (slab)   │
│ Nhãn: [Sàn S1    ]  │
│ ─────────────────── │
│ Mặt sàn SL: [  0] mm│
│ Độ dày:    [150] mm  │
│ ─────────────────── │
│ Rộng:     [3640] mm  │
│ Dài:      [2730] mm  │
│ ─────────────────── │
│ [Cập nhật]  [Xóa]   │
└─────────────────────┘
```

- Khi click chọn phần tử → điền thông tin vào panel
- Khi không chọn gì → hiện "Chưa chọn đối tượng"
- Nhấn **"Cập nhật"** → áp dụng thay đổi vào phần tử, redraw canvas
- Nhấn **"Xóa"** → xóa phần tử đang chọn (thay vì nút Xóa trên toolbar)

---

### 24b — Hiển thị kích thước realtime khi kéo

Khi đang drag vẽ hoặc resize → hiện tooltip nhỏ cạnh chuột:

```
W: 3640mm
H: 2730mm
```

- Dùng `QToolTip.showText(QCursor.pos(), text, self)` trong `mouseMoveEvent`
- Tắt tooltip khi thả chuột

---

### 24c — Lưới tọa độ mờ luôn hiện

Hiện tại checkbox "Bật lưới" không hoạt động. Sửa lại:

1. Trong `paintEvent`, luôn vẽ **lưới chấm mờ** (nếu `self.show_grid` là True):
   ```python
   if getattr(self, "show_grid", False):
       pen = QPen(QColor(180, 180, 180, 80))
       pen.setStyle(Qt.PenStyle.DotLine)
       painter.setPen(pen)
       spacing = self.grid_spacing_mm * self.scale  # px
       # Vẽ đường dọc và ngang mờ
       x = self.offset_x % spacing
       while x < self.width():
           painter.drawLine(int(x), 0, int(x), self.height())
           x += spacing
       y = self.offset_y % spacing
       while y < self.height():
           painter.drawLine(0, int(y), self.width(), int(y))
           y += spacing
   ```
2. Checkbox "Bật lưới" → toggle `self.canvas.show_grid` → `self.canvas.update()`
3. `grid_spacing_mm` mặc định = 303 (bước LGS)

**Test file:** Không cần test mới

---

## TASK 25 — Mặt cắt 2.5D: vẽ đường cắt, hiển thị song song `[ ]`

**Mục tiêu:** Vẽ đường cắt trên mặt bằng → hiện cửa sổ mặt cắt bên cạnh. Đây là tính năng quan trọng nhất của NEVIS.

---

### 25a — Cơ chế vẽ đường cắt

Thêm nút **"✂ Mặt cắt"** trong panel kết cấu.

Khi bấm:
1. Canvas vào mode `"cut_line"` — cursor đổi thành ✛
2. User **click → kéo → thả** để vẽ đường cắt ngang hoặc dọc:
   - Nếu drag gần ngang (|dy| < |dx|) → đường cắt **nằm ngang** (cắt theo trục Y)
   - Nếu drag gần dọc (|dy| > |dx|) → đường cắt **đứng** (cắt theo trục X)
3. Đường cắt hiện trên mặt bằng: nét đứt màu đỏ + mũi tên 2 đầu + ký hiệu "A-A"
4. **Click phải** sau khi vẽ đường cắt → menu nhỏ:
   - "Nhìn từ trên" / "Nhìn từ dưới" (cho đường nằm ngang)
   - "Nhìn từ trái" / "Nhìn từ phải" (cho đường đứng)
5. Chọn hướng nhìn → mở cửa sổ mặt cắt (Task 25b)

---

### 25b — Cửa sổ mặt cắt (Section View Window)

Khi user chọn hướng nhìn → mở `QDialog` hoặc `QSplitter` chia đôi màn hình:

```
┌─────────────────┬─────────────────┐
│  MẶT BẰNG      │  MẶT CẮT A-A   │
│                 │                 │
│  [bản vẽ MB]   │  GL ─────────── │
│                 │  SL±0 ───────── │
│  ══ A ═══════ A │  FL ─────────── │
│                 │                 │
│                 │  [sàn, dầm, ống]│
└─────────────────┴─────────────────┘
```

**Bên trái:** Mặt bằng hiện tại (thu nhỏ), đường cắt A-A được tô đỏ  
**Bên phải:** Mặt cắt — hiển thị:

- **Đường kẻ cao độ:** GL, SL±0, FL (dùng `build_standard_markers()` từ `section_view.py`)
- **Phần tử kết cấu** cắt qua đường cắt: vẽ mặt cắt ngang (hình chữ nhật) với vật liệu (hatch)
  - Sàn BT: hatch chéo đậm
  - Dầm BT: hatch chéo đậm
  - Vách LGS: đường đứt dọc
  - Trần: đường gạch ngang
- **Ống MEP** nằm trong vùng cắt: vẽ hình tròn (ống tròn) hoặc hình chữ nhật (ống vuông), màu theo loại (nước/điện/HVAC)
- **Nhãn cao độ** bên phải: "SL±0 / t150", "CH=2360"

**Dùng lại:** `elements_intersect_cut_line()` và `sort_elements_by_elevation()` từ `modules/section_view.py`

---

### 25c — Lưu đường cắt vào project

```python
# _project_payload():
"cut_lines": [{"x": cl.x, "direction": cl.direction, "label": cl.label} 
              for cl in getattr(self.model, "cut_lines", [])]

# open_project():
self.model.cut_lines = [CutLine(**d) for d in data.get("cut_lines", [])]
```

`CutLine` dataclass:
```python
@dataclass
class CutLine:
    x: float        # vị trí cắt (mm, tọa độ canvas)
    direction: str  # "horizontal" | "vertical"
    label: str = "A-A"
    view_side: str = "right"  # "left"|"right"|"top"|"bottom"
```

**Test file:** Không cần test mới (logic UI)

---

## TASK 26 — Sàn giật cấp: logic đúng `[ ]`

**Mục tiêu:** Sàn giật cấp (stepped slab) hiện đang bị hiểu nhầm là 2 sàn đè lên nhau. Sửa lại đúng khái niệm.

---

### Khái niệm đúng

Sàn giật cấp = **1 sàn có 2 phần ở 2 cao độ khác nhau**, ví dụ:
```
SL±0 ─────────────┐
                   │ ← vách đứng (step height)
SL-200 ────────────┘
```

Phòng WC thường thấp hơn SL±0 là 200mm (để thoát nước).

### Cách vẽ đúng

1. Vẽ sàn bình thường trước (SL±0)
2. Chọn sàn → click **"Giật cấp"** trong panel thuộc tính
3. Dialog hỏi:
   - `Vùng giật cấp`: vẽ bằng cách drag trên canvas (phải nằm trong sàn gốc)
   - `Cao độ vùng giật`: VD -200mm (so với SL)
4. Kết quả: sàn gốc vẫn còn, nhưng vùng được chọn có `stepped_region` với cao độ khác
5. Khi vẽ mặt cắt → thấy rõ 2 mức cao độ

### Lưu vào model

Dùng field đã có trong `StructuralElement`:
```python
is_stepped: bool = False
step_elevation: float = 0.0   # cao độ vùng giật so với SL
step_region: list = field(default_factory=list)  # polygon của vùng giật (nằm trong sàn)
```

Nếu field `step_region` chưa có → thêm vào `StructuralElement` dataclass và `structural_element_to_dict/from_dict`.

### Hiển thị

- Vùng giật cấp: vẽ hatch chéo mờ khác màu
- Nhãn: "SL±0 / t150" cho vùng bình thường, "SL-200 / t150" cho vùng giật
- Khi hover chuột vào vùng giật → tooltip hiện "Vùng giật cấp: SL-200"

**Test file:** Không cần test mới
