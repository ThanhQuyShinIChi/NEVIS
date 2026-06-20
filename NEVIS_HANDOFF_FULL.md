# NEVIS — Tài liệu Bàn Giao Toàn Diện
**Cập nhật: 2026-06-20 | Phiên: Wall System W1–W6 hoàn chỉnh**

---

## 1. TỔNG QUAN DỰ ÁN

**NEVIS** là phần mềm MEP (cơ điện lạnh) chuyên ngành Việt–Nhật.

| Thông tin | Giá trị |
|-----------|---------|
| Ngôn ngữ | Python 3.11+ |
| UI Framework | PySide6 / Qt |
| File chính | `D:\Nevis2.03\Nevis_no_ui.py` (32 619 dòng) |
| Branch | `feature/building-space-model` |
| Remote | `https://github.com/ThanhQuyShinIChi/NEVIS.git` |
| Commit mới nhất **chưa push** | `fd63ef0` |
| Test suite | `274 passed, 38 warnings` (baseline không được phá vỡ) |
| Git user | Le Thanh Quy |

---

## 2. KIẾN TRÚC KỸ THUẬT

### 2.1 Pattern chính
- **Monkey-patching**: NEVIS thêm chức năng bằng cách patch vào `MainWindow` và `PreviewView` ở cuối file `Nevis_no_ui.py`. Không sửa class definition trực tiếp.
- **Task numbering**: mỗi block chức năng mới đặt tên `# TASK XX — tên`.
- **Coordinate system**: canvas dùng pixel; real-world dùng mm. Hàm `_nevis_real_to_canvas_point()` / `_nevis_canvas_to_real_point()` chuyển đổi.
- **GEOMETRY_SCALE = 0.1** (scene unit / mm) trong section view.
- **Section view**: xây dựng riêng tại `_nevis_t15_show_section_dialog()`, không phải section view chính `_nevis_t29_render_section`.

### 2.2 Workspace modes
- `"mep"` — mặc định, vẽ đường ống
- `"structural"` — vẽ kết cấu (slab, beam, column, wall)

### 2.3 Elevations
- **SL = ±0** — mặt sàn bê tông (Slab Level)
- **FL** = SL + finish_thickness_mm (Floor Level = mặt sàn hoàn thiện)
- **GL** = SL − 150mm (Ground Level, datum bổ sung tầng 1)
- **置き床 (oki-yuka)**: SL → +168mm 支持脚 → +20mm 置床パネル → +12mm フローリング = FL tại SL+200mm

---

## 3. CÁC FILE QUAN TRỌNG

| File | Mô tả |
|------|-------|
| `Nevis_no_ui.py` | File chính 32 619 dòng, TOÀN BỘ logic UI + rendering |
| `modules/structural_element.py` | Data model: `StructuralElement` dataclass + serialize/deserialize |
| `modules/clash_detection.py` | Clash detection MEP vs kết cấu |
| `modules/structural_transform.py` | Resize/handle logic |
| `modules/stepped_slab.py` | Sàn giật cấp (polygon merge với Shapely) |
| `tests/` | ~274 tests, chạy với pytest |
| `PIPE_CODE_LOCKED.md` | **ĐỌC TRƯỚC** khi đụng pipe rendering |
| `WALL_SYSTEM.md` | Chi tiết hệ thống tường |
| `CURRENT_HANDOFF.md` | Handoff summary ngắn (cập nhật thường xuyên) |
| `nevis_library_index.json` | 577 pipe fitting entries |

---

## 4. DATA MODEL — StructuralElement

File: `D:\Nevis2.03\modules\structural_element.py`

```python
@dataclass
class StructuralElement:
    id: int
    element_type: str  # "slab"|"beam"|"column"|"wall_rc"|"wall_lgs"|"ceiling"
    label: str = ""
    points: list          # [(x,y)...] canvas mm coords, rectangle = 4 điểm
    width: float = 0.0    # mm
    length: float = 0.0   # mm
    height: float = 0.0   # mm (thickness cho slab/wall)
    arc_radius: float = 0.0

    # Elevation (mm, relative to SL=0)
    top_elevation: float = 0.0
    bottom_elevation: float = 0.0

    # LGS-specific
    stud_spacing: float = 303.0   # mm (1尺=303 hoặc 1.5尺=455)
    stud_width: float = 65.0      # mm (45/65/90)
    board_thickness: float = 12.5
    board_layers: int = 1

    # Stepped slab
    is_stepped: bool = False
    parent_slab_id: int = -1
    overlap_width: float = 0.0

    # Floor finish (sàn)
    finish_layers: list = []      # [{"name":str, "thickness":float}]
    finish_thickness_mm: float = 0.0

    # Wall/Column/Beam finish layers (THÊM MỚI — Wall System W1)
    wall_finish_inner: list = []  # lớp kết cấu → phía trong phòng
    wall_finish_outer: list = []  # lớp kết cấu → phía ngoài/hành lang
    wall_finish_type_code: str = ""   # "W-01"..."W-13", "H-01", "H-12", "" = custom
    wall_rc_thickness: float = 180.0  # RC body (mm)
    lgs_is_staggered: bool = False    # True = 千鳥配置
```

**Layer dict format:**
```python
{"name": str, "thickness": float, "material_type": str}
# material_type: "insulation_ur"|"insulation_gw"|"gl"|"gypsum"|"gypsum_fire"
#                "gypsum_hard"|"gypsum_wet"|"air_gap"|"lgs_frame"
```

**Helper functions:**
```python
get_wall_frame_width(e) -> float
# LGS: stud_width + 2 (single) hoặc stud_width + 12 (千鳥)

get_wall_total_width(e) -> float
# LGS: frame + inner_sum + outer_sum
# RC:  wall_rc_thickness + inner_sum + outer_sum

get_finish_thickness(e) -> float
# Sàn: sum(finish_layers) hoặc fallback finish_thickness_mm
```

---

## 5. WALL SYSTEM — ĐÃ IMPLEMENT (W1–W6)

### 5.1 Presets (trong `Nevis_no_ui.py` ~line 28368)

Biến `_NEVIS_WALL_PRESETS` — list of dict:

| Code | Loại | Cấu tạo | Tổng dày |
|------|------|---------|----------|
| **H-01** | Cột/Dầm ngoại thất | ウレタン25+GL17.5+石膏12.5 (inner) | +55mm |
| **H-12** | Cột/Dầm ngoại thất | GL17.5+石膏12.5 (inner) | +30mm |
| **W-12** | RC外壁 | ウレタン(UR)25+GL17.5+石膏12.5 (inner) | RC180+55=235mm |
| **W-13** | RC内壁 | GL17.5+石膏12.5 (inner) | RC180+30=210mm |
| **W-04** | RC外壁ELV | GW35+中空+LGS47+石膏12.5 (inner) | RC180+96.5=276.5mm |
| **W-01** | LGS65 千鳥 界壁 | 強化石膏21+硬質9.5 (両面) | 77+61=138mm |
| **W-02** | LGS45 一般間仕切 | 石膏12.5 (両面) | 47+25=72mm |
| **W-03** | LGS45 水廻り | 耐水石膏12.5 (両面) | 47+25=72mm |

Hàm lookup: `_nevis_wall_preset_by_code(code: str) -> dict`

### 5.2 Dialog (W2) — `_nevis_t21_edit_dialog()`

Dialog hiện thị `仕上げ構成` panel khi type = `wall_rc`, `wall_lgs`, `column`, `beam`:
- Preset dropdown (H-01, H-12, W-01~W-13)
- RC厚 field (chỉ wall_rc)
- Stud size + 千鳥 checkbox (chỉ wall_lgs)
- Auto-calc total width + layer summary

**Return tuple**: 9 giá trị (non-wall) hoặc **15 giá trị** (wall/column/beam):
```python
# 15-tuple for walls:
(etype, width, length, height, arc_radius,
 top_elev, bot_elev, 0.0, [],
 wall_type_code, wall_inner, wall_outer,
 wall_rc_thick, stud_w, lgs_stagger)
```

**3 callers** đều xử lý 15-tuple:
- `_nevis_t21_create_from_drag()` (~line 29033)
- `_nevis_t21_edit_existing()` (~line 29079)
- `_nevis_t23a_create_from_drag()` (~line 29246)

### 5.3 Plan View (W3a/W3b/W6) — `_nevis_w3_draw_walls()`

Vị trí: ~line 26669, gọi từ `_nevis_structural_draw_items()`.

**Junction auto-merge logic:**
```python
# Merge key rules:
wall_rc + column + beam  →  key=("rc_solid","")  → QPainterPath.united() → 1 viền liền
wall_lgs                 →  key=("wall_lgs", type_code)  → merge trong cùng preset
```

- RC solid group: `QPen(dark, 2.0)` + `QBrush(FDiagPattern)` cho toàn merged path
- LGS: `QPen(dark, 1.5)` + light fill + finish layer bands (inner/outer strips màu riêng)
- Column/Beam trong RC group: merge luôn vào viền RC, không seam kép tại góc
- Hit-test item (transparent) cho từng element → selection/handles vẫn riêng biệt

**Finish layer bands** (LGS plan view):
- Horizontal wall: outer = dải trên, inner = dải dưới (theo Y direction)
- Vertical wall: outer = dải trái, inner = dải phải (theo X direction)
- Tỷ lệ theo `total_outer/total_w` và `total_inner/total_w`

### 5.4 Section View (W4/W5) — trong `_nevis_t15_show_section_dialog()`

**Slab (W4)**: FL finish layers hiển thị như dải màu nằm TRÊN slab rect, ordered bottom→top.

**Wall_lgs (W5)**: chia rect theo width thành: `outer layers | LGS frame | inner layers`, mỗi layer màu riêng theo `material_type`.

**Wall_rc (W5)**: `RC body (FDiagPattern) | inner layers`.

**Wall annotation (W4)**:
- W-01 → `[FL全カット]`
- W-02/W-03 → `[フロ カット]`

### 5.5 Tường-Sàn Rules (chỉ implement annotation, chưa implement geometry cut)

```
W-01 (界壁): CẮT TOÀN BỘ FL finish → sàn RC trần tại zone đó
W-02/W-03 (一般間仕切): chỉ cắt フローリング (top layer)
RC外壁: sàn dừng tại mép trong RC tự nhiên
```

---

## 6. PIPE CODE — KHÓA (KHÔNG SỬA)

**Đọc `PIPE_CODE_LOCKED.md` trước khi đụng pipe code.**

| Section | Vị trí | Ghi chú |
|---------|--------|---------|
| Pipe styles (5/7 nét) | ~line 210–252 | `NEVIS_PIPE_STYLE_LOCKED_VERSION` |
| `paintEvent` | ~line 2123 | `cosmetic=True` bắt buộc |
| `_add_pipe_line` | ~line 3107 | z=5, cosmetic=True |
| Fitting lookup | `nevis_library_index.json` | 577 entries |

**VP/DV**: 5 nét | **TMP**: 7 nét | Tim dùng `[4,3,12,3]` pattern.

---

## 7. QUY TẮC LẬP TRÌNH

### 7.1 Bắt buộc
- **KHÔNG commit/push** khi chưa hỏi người dùng
- **KHÔNG ghi đè `CODEX_TASKS.md`** mà không đọc trước
- **KHÔNG xóa `section_debug.log`** khi debug GUI
- Trước mỗi thay đổi lớn: chạy syntax check + test suite
- Monkey-patch ở cuối file, đặt tên `_nevis_tXX_` theo task number

### 7.2 Test commands
```powershell
# Syntax check
python -B -c "import ast; ast.parse(open('Nevis_no_ui.py', encoding='utf-8').read()); print('OK')"

# Full test suite (KHÔNG bao giờ được ít hơn 274 passed)
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py

# Chạy app
python -B D:\Nevis2.03\Nevis_no_ui.py
```

### 7.3 Coding patterns hay dùng
```python
# Canvas ↔ Real conversion
canvas_pt = _nevis_real_to_canvas_point(mainwin, (real_x, real_y))
real_pt   = _nevis_canvas_to_real_point(mainwin, (canvas_x, canvas_y))

# Find element by id
elem = _nevis_structural_find_element(self, element_id)

# Scene polygon
polygon = QPolygonF([QPointF(x, y) for x, y in canvas_points])
item = view.scene.addPolygon(polygon, pen, brush)
item.setZValue(z)
item.setData(0, ("structural_element", int(element.id)))

# QPainterPath union (junction merge)
path = QPainterPath()
path.addPolygon(polygon)
path.closeSubpath()
merged = merged.united(path)
```

---

## 8. TRẠNG THÁI HIỆN TẠI

### 8.1 Đã commit (pushed đến `fd63ef0`)
- Clash Detection (Task 22)
- GL datum + Section auto-refresh (Task 22c)
- Z-order fix + snap-to-slab-edge
- FL datum trong section
- Slab finish layers (multi-layer dialog + section rendering)

### 8.2 Đã implement nhưng **CHƯA COMMIT/PUSH** (phiên này)
- `modules/structural_element.py`: 5 field mới + 2 helper functions + serialize/deserialize
- `Nevis_no_ui.py`: Wall System W1–W6 toàn bộ
  - `_NEVIS_WALL_PRESETS` (H-01, H-12, W-01~W-13)
  - `_nevis_wall_preset_by_code()`
  - `_nevis_w3_draw_walls()` — junction merge rendering
  - Wall panel trong `_nevis_t21_edit_dialog()`
  - Section view wall/column layer rendering
  - FL finish bands trên slab trong section
- `PIPE_CODE_LOCKED.md` (file mới)
- `WALL_SYSTEM.md` (file mới)
- `CURRENT_HANDOFF.md` (cập nhật)

### 8.3 Chưa implement
| Phase | Mô tả |
|-------|-------|
| W7 | Trần LGS (天井下地 LGS) — chờ spec chi tiết |
| W4-geometry | Actual geometry cut của FL finish tại wall intersection (hiện chỉ có annotation) |
| Cửa/Cửa sổ | Door/Window openings trong tường |
| JWW export | Export tường/cột ra file JWW |

---

## 9. CONTEXT KỸ THUẬT CỤ THỂ

### 9.1 Structural dialog return tuple
```python
# Non-wall types → 9-tuple:
(etype, width, length, height, arc_radius,
 top_elevation, bottom_elevation, finish_mm, finish_layers)

# wall_rc / wall_lgs / column / beam → 15-tuple:
(etype, width, length, height, arc_radius,
 top_elevation, bottom_elevation, 0.0, [],
 wall_type_code, wall_inner, wall_outer,
 wall_rc_thick, stud_w, lgs_stagger)
```

### 9.2 Plan view z-order
```
z=10 : slab
z=11 : wall_lgs, ceiling
z=12 : wall_rc, column, beam  (RC solid group)
z=13 : labels, elevation text
z=15 : elevation labels overlay (_nevis_t21_draw_model)
z=1001: preview polygon khi drag
```

### 9.3 Section view structure
Section là simple elevation view — không có spatial X coordinates. Elements được xếp theo index. Mỗi element chiếm `elem_w = (W-20) / count` pixels theo chiều ngang.

Floor finish bands: vẽ TRÊN `rect_y` (top of slab), mỗi layer `layer_h = thickness_mm * px_per_mm`.

### 9.4 Key lines trong Nevis_no_ui.py
| Nội dung | Khoảng line |
|---------|-------------|
| PIPE_COLORS + style constants | ~210–260 |
| paintEvent (pipe rendering) | ~2123 |
| `_add_pipe_line` | ~3107 |
| `_nevis_structural_draw_items` | ~26845 |
| `_nevis_w3_draw_walls` | ~26669 |
| `_nevis_t15_show_section_dialog` (simple section) | ~27952 |
| `_NEVIS_FINISH_TYPES` (sàn presets) | ~28593 |
| `_NEVIS_WALL_PRESETS` | ~28368 |
| `_nevis_wall_preset_by_code` | ~28483 |
| `_nevis_t21_edit_dialog` | ~28487 |
| `_nevis_t21_create_from_drag` | ~29033 |
| `_nevis_t21_edit_existing` | ~29079 |
| `_nevis_t23a_create_from_drag` | ~29246 |

---

## 10. CÁC VẤN ĐỀ ĐÃ BIẾT

### 10.1 Section view (simple) vs Section view (full)
Có 2 loại section:
1. **Simple** (`_nevis_t15_show_section_dialog`): popup dialog, elevation only, không có spatial X
2. **Full** (`_nevis_t29_render_section`): split view bên phải, có scale thực, dùng `GEOMETRY_SCALE=0.1`

Wall layer rendering hiện chỉ có ở **simple** section. Full section chưa có wall layers.

### 10.2 Junction merge giới hạn
- RC elements (wall_rc + column + beam) merge với nhau ✅
- LGS merge với cùng type_code ✅
- LGS KHÔNG merge với RC (đúng về mặt kỹ thuật — LGS đứng trước/sau RC)
- Finish layer bands ở plan view chỉ đúng với tường THẲNG (horizontal/vertical), không xử lý tường chéo

### 10.3 Wall direction
Wall "inner" vs "outer" trong plan view được suy luận từ bounding box:
- `dx > dy` → horizontal wall → outer = top strip (min Y), inner = bottom strip (max Y)
- `dx <= dy` → vertical wall → outer = left strip (min X), inner = right strip (max X)
- **Giới hạn**: không biết chiều "phía trong nhà" là trái hay phải — cần user input hoặc room detection

### 10.4 Pipe fitting (LOCKED)
Fitting key format: `{size}{mat}-{type}` hoặc `{main}x{branch}{mat}-{type}`.
Debug: `nevis_preview_fitting_debug.txt` ghi `missing=<key>` khi không tìm thấy.

---

## 11. HƯỚNG DẪN BẮT ĐẦU PHIÊN MỚI

**Bước 1 — Đọc context:**
```powershell
cd D:\Nevis2.03
git status --short --branch
git log -10 --oneline
```

**Bước 2 — Verify baseline:**
```powershell
python -B -c "import ast; ast.parse(open('Nevis_no_ui.py', encoding='utf-8').read()); print('OK')"
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py
# Kết quả mong đợi: 274 passed
```

**Bước 3 — Đọc handoff files:**
- `NEVIS_HANDOFF_FULL.md` (file này)
- `PIPE_CODE_LOCKED.md` nếu liên quan đến pipe
- `WALL_SYSTEM.md` nếu tiếp tục wall system
- `CURRENT_HANDOFF.md` cho summary ngắn

**Bước 4 — Hỏi người dùng** những gì cần làm tiếp theo.

---

## 12. CÂU HỎI ĐÃ GIẢI QUYẾT (KHÔNG CẦN HỎI LẠI)

| Câu hỏi | Quyết định |
|---------|-----------|
| RC thickness mặc định? | 180mm (standard Nhật) |
| LGS reference point? | Tim khung (centerline) |
| RC reference point? | Mép ngoài (outer face = mép sàn) |
| 千鳥 adds how much? | +12mm (vs +2mm cho single-row tracks) |
| W-01 total width? | 138mm (77 frame + 30.5×2 finish) |
| W-02/W-03 total width? | 72mm (47 frame + 12.5×2 finish) |
| Column/Beam RC merge with wall_rc? | ✅ YES — tất cả gom vào rc_solid group |
| LGS merges with RC? | ❌ NO — vật lý không đúng |
| H-01 preset? | ウレタン25+GL17.5+石膏12.5 trên mặt trong |
| Commit/push khi nào? | Chỉ khi người dùng confirm |

---

## 13. LỆNH COMMIT KHI NGƯỜI DÙNG XÁC NHẬN

```powershell
cd D:\Nevis2.03

# Stage files
git add Nevis_no_ui.py
git add modules/structural_element.py
git add CURRENT_HANDOFF.md
git add PIPE_CODE_LOCKED.md
git add WALL_SYSTEM.md
git add NEVIS_HANDOFF_FULL.md

# Commit
git commit -m "$(cat <<'EOF'
Wall System W1-W6: data model, dialog, plan/section rendering, junction merge

- W1: StructuralElement +5 fields (wall_finish_inner/outer, type_code, rc_thickness, lgs_is_staggered)
      + get_wall_frame_width / get_wall_total_width helpers
- W2: Edit dialog wall panel — presets H-01/H-12/W-01~W-13, RC厚, stud+千鳥, total width display
- W3a/b: Plan view — _nevis_w3_draw_walls() with QPainterPath.united() junction merge
         RC+column+beam → single merged border; LGS → same-type merge
- W4: Section view — FL finish layer bands above slab; wall FL-cut annotations
- W5: Section view — wall layer structure with per-material-type colors (LGS frame|gypsum|insulation)
- W6: H-01/H-12 presets for exterior column/beam ウレタン finish
      Column+beam included in RC solid merge group (no seam at column-wall junction)
- PIPE_CODE_LOCKED.md: pipe rendering protection documentation
- WALL_SYSTEM.md: wall system specification and progress tracking

Tests: 274 passed, 38 warnings (no regressions)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"

# Push
git push origin feature/building-space-model
```

---

*File này được tạo tự động bởi Claude Sonnet 4.6 ngày 2026-06-20.*
*Để tiếp tục: đọc mục 11 (Hướng dẫn bắt đầu phiên mới).*
