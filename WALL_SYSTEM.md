# WALL SYSTEM — NEVIS (Tiêu chuẩn Nhật)

Cập nhật: 2026-06-20 — W1 Data Model hoàn chỉnh

---

## Điểm tham chiếu (Reference Point)

| Loại tường | Reference | Lý do |
|-----------|-----------|-------|
| **RC外壁/内壁** | Mép NGOÀI của RC (= mép sàn bê tông) | Tường ăn theo mép sàn |
| **LGS 間仕切** | **Tim khung LGS** (centerline) | Người vẽ đặt tim vách |

---

## Data Fields (StructuralElement)

```python
wall_finish_inner: list   # lớp từ mặt kết cấu → phía trong phòng
wall_finish_outer: list   # lớp từ mặt kết cấu → phía ngoài/hành lang
wall_finish_type_code: str  # "W-01"..."W-13" hoặc "" (custom)
wall_rc_thickness: float  # RC body thickness, default 180.0mm
lgs_is_staggered: bool    # True = 千鳥配置 (W-01 界壁)
```

Mỗi layer trong list:
```python
{"name": str, "thickness": float, "material_type": str}
```

`material_type` values:
- `"insulation_ur"` — 断熱材 ウレタン
- `"insulation_gw"` — 断熱材 グラスウール
- `"gl"` — GL工法接着剤 (17.5mm)
- `"gypsum"` — 石膏ボード 通常
- `"gypsum_fire"` — 強化石膏ボード
- `"gypsum_hard"` — 硬質石膏ボード
- `"gypsum_wet"` — 耐水石膏ボード
- `"air_gap"` — 中空 (thickness=0)
- `"lgs_frame"` — LGSフレーム (W-04 内部LGS下地)

---

## Helper Functions (structural_element.py)

```python
get_wall_frame_width(e) -> float
# LGS有効フレーム幅
# 通常: stud_width + 2mm (トラック)
# 千鳥: stud_width + 12mm
# 例: LGS45通常 = 47mm, LGS65千鳥 = 77mm

get_wall_total_width(e) -> float
# 総壁厚 = 躯体 + inner layers + outer layers
# LGS: frame_width + inner + outer
# RC:  wall_rc_thickness + inner + outer
```

---

## Wall Presets — _NEVIS_WALL_PRESETS (Nevis_no_ui.py)

### RC外壁

| Code | Cấu tạo (inner) | RC | Tổng finish |
|------|----------------|-----|-------------|
| W-12 | 断熱材(UR)25+GL17.5+石膏12.5 | 180 | 55mm |
| W-13 | GL17.5+石膏12.5 | 180 | 30mm |
| W-04 | 断熱材(GW)35+中空+LGS47+石膏12.5 | 180 | 96.5mm |

### LGS間仕切

| Code | Cấu tạo | Stud | Staggered | Frame | Inner/Outer | Tổng |
|------|---------|------|-----------|-------|-------------|------|
| W-01 | 強化石膏21+硬質9.5 **両面** | 65 | ✓千鳥 | 77 | 30.5+30.5 | **138mm** |
| W-02 | 石膏12.5 **両面** | 45 | ✗ | 47 | 12.5+12.5 | **72mm** |
| W-03 | 耐水石膏12.5 **両面** (水廻り) | 45 | ✗ | 47 | 12.5+12.5 | **72mm** |

---

## Quy tắc Tường-Sàn (W4 — chưa implement)

```
界壁 W-01 (耐火間仕切)
  → CẮT TOÀN BỘ FL finish tại vị trí tường
  → Không 支持脚, không 置床パネル, không フローリング
  → Sàn RC trần tại zone đó

一般間仕切 W-02/W-03
  → Giữ 支持脚 + 置床パネル (置き床 structure)
  → CẮT フローリング tại vị trí tường (gỗ không đi dưới tường)
  → Cắt hẹp bằng wall_total_width tại vị trí giao

RC外壁
  → Sàn dừng tại mép trong RC (outer face = slab edge)
  → Không cần cắt, sàn tự nhiên không chạy ra ngoài sàn
```

---

## Tiến trình thực hiện

| Phase | Nội dung | Trạng thái |
|-------|---------|------------|
| W1 | Data Model + Presets | ✅ XONG (2026-06-20) |
| W2 | Dialog chỉnh tường | ✅ XONG (2026-06-20) |
| W3a | Plan View — LGS rendering + junction merge | ✅ XONG (2026-06-20) |
| W3b | Plan View — RC rendering (hatch) | ✅ XONG (2026-06-20) |
| W4 | Tường-Sàn: FL finish bands trên slab + wall FL-cut annotation | ✅ XONG (2026-06-20) |
| W5 | Section View tường — layer structure với màu per material | ✅ XONG (2026-06-20) |
| W6 | Cột/Dầm finish (H-01/H-12 preset) + RC cross-type merge | ✅ XONG (2026-06-20) |
| W7 | Trần thạch cao | ⏳ Chưa bắt đầu |

---

## Cách test nhanh

```powershell
# Syntax check
python -B -c "import ast; ast.parse(open('Nevis_no_ui.py', encoding='utf-8').read()); print('OK')"

# Full test suite (expected: 274 passed)
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py

# Import check
python -B -c "from modules.structural_element import StructuralElement, get_wall_total_width, get_wall_frame_width; e = StructuralElement(id=1, element_type='wall_lgs'); print('LGS45 frame:', get_wall_frame_width(e)); print('OK')"
```
