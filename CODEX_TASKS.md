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

## TASK 6 — Data model cho StructuralElement `[x]`

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

## TASK 7 — Vẽ Rectangle trên canvas (công cụ vẽ kết cấu) `[x]`

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

## TASK 8 — Nhập kích thước trực tiếp (W, L, H, C) `[x]`

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

## TASK 9 — Di chuyển và resize phần tử kết cấu `[x]`

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

## TASK 10 — Sàn giật cấp (stepped slab) `[x]`

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

## TASK 11 — Mode switch MEP / Kết cấu `[x]`

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

## TASK 12 — Grid snap + hiển thị lưới `[x]`

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
