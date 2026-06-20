# NEVIS Current Handoff

Cap nhat: 2026-06-20 (session 7) - Visual polish, right-click picker, section overlap bands

## Bat buoc doc truoc khi lam

1. Doc toan bo file nay.
2. Chay `git status --short --branch` va `git log -10 --oneline`.
3. Bao toan tat ca thay doi chua commit.
4. Khong commit/push neu user chua yeu cau ro rang.
5. Doc `PIPE_CODE_LOCKED.md` truoc khi cham vao pipe rendering.
6. Doc `CODEX_TASKS.md` truoc khi cap nhat file do.

## Repo va Git

- Repo: `D:\Nevis2.03`
- Branch: `feature/building-space-model`
- Tat ca thay doi session nay da COMMIT vao 1 commit moi (xem git log).
- Khong push neu user chua yeu cau.

---

## Tong ket thay doi session 7

### 1. Performance freeze (da xu ly session truoc, can user xac nhan GUI)

- `_ensure_library_index_current()` chay rglob trong daemon thread, throttle 120s.
- Common apply debounce 180ms -> 350ms.
- TEMP timing log `PERF apply_common` con trong code (~line 8671-8678) — XOA sau khi user xac nhan performance on.

### 2. Wall junction merge (hoan thanh)

- `_nevis_w3_draw_walls`: RC/column/beam hop nhat thanh 1 outline duy nhat, LGS merge cung preset.
- `_nevis_t28_draw_items`: tuong/cot qua `_nevis_w3_draw_walls`, slab dung punch-out logic rieng.
- `QPainterPath` import fix trong `_union_paths`.

### 3. Default bottom elevation = SL±0 (hoan thanh)

- Dialog tao tuong/cot/vach: `init_bot` mac dinh `0.0` thay vi `-500.0`.

### 4. Wall bottom follows stepped slab in section view (hoan thanh)

- `_slab_floor_map`: list `(start_mm, end_mm, top_elevation)` tu `slab_assemblies`.
- `_wall_bottom_segments(h_start, h_end, stored_bot)`: chia tuong thanh cac doan, moi doan co `eff_bot = min(stored_bot, slab_top_tai_vi_tri_do)`.
- Chi ap dung cho `wall_rc`, `wall_lgs`, `column`, `beam` (khong ap dung slab/ceiling).

### 5. Visual polish - mat bang (hoan thanh)

**Net manh hon (1.0px thay vi 2.0px):**
- RC group, LGS, slab, stepped, ceiling: tat ca pen 1.0px.

**Mau rieng tung loai:**
- RC/cot/dam: xam toi + FDiag hatch.
- Vach LGS: xanh duong nhat, fill nhe.
- San parent: xam nhe, net dut.
- San giat cap (stepped child): **vang solid** (vung ha xuong nhin tu tren).
- Vung chong lan (overlap zone): **cam hatch cheo** (gia co thep, nhin tu duoi); z=9 (duoi slab/vach).
- Tran LGS: xanh la nhat, dash-dot.

**Label chi hien khi selected:**
- Mat bang: khong co chu tren phan tu, chi hien khi click chon (label mau xanh + 8 handle).

### 6. Visual polish - mat cat (hoan thanh)

**Net manh hon:**
- `slab_pen`: 2.0px -> 1.0px.
- Element pen: 2.0px -> 1.0px.

**Mau rieng tung loai:**
```python
_SECT_STYLE = {
    "slab":       xam xanh FDiag hatch
    "wall_rc":    xam toi FDiag hatch
    "column":     xam toi solid
    "beam":       nau nhat solid
    "wall_lgs":   xanh nhat solid
    "ceiling_lgs":xanh la nhat solid
}
```

**Overlap bands trong mat cat (NEW):**
- `assembly.overlap_bands` gio duoc render: cam hatch cheo, z=5.5.
- The hien vung neo gia co thep tai ranh gioi stepped slab.

**Label element khong hien trong mat cat** (giam roi mat), chi con elevation text.

**Huong nhin dung:**
- `_flip_horiz`: axis=X+side=above (nhin Nam) hoac axis=Y+side=right (nhin Tay) thi flip.

### 7. Right-click object picker (hoan thanh)

- Click phai tren mat bang: hien list tat ca doi tuong tai vi tri do.
  ```
  1.  スラブ   5000×3000 mm
  2.  軽量鉄骨壁   150×2500 mm
  ─────────────────────
  スナップ移動
  ```
- Chon ten -> select dung doi tuong do.
- Handle hit van uu tien nhu cu.

### 8. Bug fixes

| Loi | Fix |
|-----|-----|
| `UnboundLocalError: _etype` trong section render | Move `_etype = getattr(...)` truoc `_SECT_STYLE` |
| `UnboundLocalError: etype` trong elevation dialog | Thut vao dung trong `if kind == "element":` |
| `TypeError: int(None)` trong `_nevis_structural_find_element` | Guard None truoc `int()` |
| `RuntimeError: C++ object deleted` trong `_nevis_t15_remove_cut_marker` | `try/except RuntimeError` |

---

## Viec can lam tiep

1. **Xac nhan GUI** sau khi chay `python D:\Nevis2.03\Nevis_no_ui.py`:
   - Doi main size 50/65/75/100 kiem tra khong con freeze.
   - Ve san + san giat cap -> mat bang: vang = vung ha, cam hatch = overlap.
   - Chon duong cat -> mat cat: co cam hatch overlap bands tai ranh gioi stepped.
   - Click phai nhieu phan tu chong nhau -> hien list chon.
   - Hieu chinh: mat cat flip dung theo huong nhin (click tren / duoi duong cat).

2. **Xoa TEMP timing log** `PERF apply_common` (~line 8671-8678) sau khi xac nhan performance on.

3. **Bug: stepped slab bien mat sau khi sua parent** — chua reproduce, can project + cac buoc cu the.

4. Commit/push khi user yeu cau.

---

## Quy tac bao ve

- Khong sua locked pipe line standard, z-order, cosmetic pen hoac fitting rendering neu chua doc `PIPE_CODE_LOCKED.md`.
- Khong thay resolver proven bang heuristic/index scoring khong co test thu vien day du.
- Khong de filesystem `rglob()` chay trong `draw_model()`.
- Khong xoa `section_debug.log` khi debug GUI.
- Khong revert thay doi chua commit cua session truoc.
- Khong commit/push ma khong hoi user.
