# NEVIS Current Handoff

Cap nhat: 2026-06-20 (Asia/Bangkok) — sau phien Z-order + edge snap + FL datum + finish_thickness

## Doc truoc khi lam

1. Doc file nay.
2. Doc `SECTION_TEST_LOG.md` neu can lich su chi tiet va so lieu tung lan GUI test.
3. Chay `git status --short --branch` va `git log -10 --oneline`.
4. Khong ghi de thay doi dang co trong `CODEX_TASKS.md`.
5. Hoi nguoi dung truoc moi dot sua/commit/push.

## Repo va Git

- Repo dang lam: `D:\nevis2.03`.
- Branch: `feature/building-space-model`.
- Commit moi nhat: `c252046` (Task 22c + GL datum + Section refresh).
- Remote: `https://github.com/ThanhQuyShinIChi/NEVIS.git`.
- Thay doi da commit phien nay: xem commit moi nhat.

## Muc tieu san pham da thong nhat

- Mat bang va mat cat cung ton tai, dung chung model va sau nay cap nhat hai chieu.
- Mat cat phai dung kich thuoc/ty le that, phuc vu clash detection va xuat JWW.
- San cha va san giat cap la mot cau kien lien tuc, khong phai hai khoi mau khac nhau.
- Man hinh lam viec uu tien hinh hoc/mau ro; hatch chi tiet de danh cho profile xuat JWW.
- GL la datum bo sung cho tang 1, khong thay the SL.
- FL la datum hoan thien tren slab (置き床 ~200mm, gach ~30mm, go truc tiep ~15mm).
- Clash Detection: ong MEP xuyen ket cau hien do, phat hien tu dong khi bam nut.

## Da hoan thanh trong phien nay (DA COMMIT)

### Z-order fix
- Slabs: z=10, walls_lgs/ceiling: z=11, beams/columns/walls_rc: z=12.
- Ket qua: dam/cot/tuong luon ve len tren slab, khong bi an di.

### Snap-to-slab-edge
- Helper `_nevis_slab_edge_candidates(mainwin)`: thu thap goc slab va diem giua canh.
- Trong `_nevis_structural_snap_scene_point`: kiem tra slab edge TRUOC (tolerance 20px), roi moi den grid snap.
- Ket qua: khi keo dam/cot den gan canh slab, tu dong bat vao mep.

### FL datum trong mat cat
- Trong `_nevis_t29_render_section`: kiem tra `level_datums["FL"]` hoac tu tinh tu `slab.finish_thickness_mm`.
- Duong xanh da troi (`QColor(30, 100, 180)`), net dut, nhan "▽FL".
- Neu finish_thickness_mm > 0: FL = top_elevation + finish_thickness_mm.

### finish_thickness_mm field
- `modules/structural_element.py`: them `finish_thickness_mm: float = 0.0` vao `StructuralElement`.
- Serialize/deserialize: cap nhat `structural_element_to_dict` va `structural_element_from_dict`.
- Dialog: them field "Lop hoan thien (mm)" hien thi chi khi type = slab.
- Tat ca 3 caller create/edit da cap nhat de truyen `finish_mm`.

## Xac minh da chay

- Full suite: `274 passed, 38 warnings` — khong co regression.
- Lenh chay:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py
```

## Trang thai GUI

- Chua retest GUI cho cac tinh nang moi nhat:
  - Z-order: dam/cot phai hien tren slab.
  - Snap-to-slab-edge: keo dam den gan mep slab.
  - FL datum: ve mat cat sau khi dat finish_thickness_mm > 0 cho slab.
  - Clash detection overlay (Task 22c).
  - GL datum trong mat cat.

## Wall System — Trang thai (2026-06-20)

| Phase | Noi dung | Trang thai |
|-------|---------|------------|
| W1 | Data Model + Presets (W-01~W-13) | XONG |
| W2 | Dialog chinh tuong (preset, RC thick, LGS stud, stagger) | XONG |
| W3a | Plan View LGS — junction auto-merge QPainterPath.united() | XONG |
| W3b | Plan View RC — hatch fill (FDiagPattern) | XONG |
| W4 | Section: FL finish bands tren slab + wall FL-cut annotation | XONG |
| W5 | Section: Wall layer structure theo material_type voi mau rieng | XONG |
| W6 | Dam/Cot finish (H-01, H-12) | CHO SPEC |
| W7 | Tran thach cao LGS | CHO SPEC |

## Viec tiep theo

1. Nguoi dung test GUI: tao tuong LGS va RC, chon preset W-01/W-02/W-12, xem plan view va mat cat.
2. Commit + push khi nguoi dung confirm OK.
3. W6/W7: can nguoi dung cung cap chi tiet ban ve H-01, H-12, LGS tran.
4. JWW export profile (hatch, layer, net in) — dai han.
5. Kiem tra overlap display trong mat cat.

## Lenh tiep tuc nhanh

```powershell
cd D:\nevis2.03
git status --short --branch
git log -10 --oneline
python -B Nevis_no_ui.py
```

## Ghi chu quan trong

- **PIPE CODE LOCKED:** Doc `PIPE_CODE_LOCKED.md` truoc khi cham vao pipe rendering, fitting lookup, hoac PIPE_COLORS. Cac section nay da chot 2026-06.
- `section_debug.log`: Khi debug GUI, khong xoa file nay; dung session ID va timestamp de doi chieu.
- GEOMETRY_SCALE = 0.1 (scene unit / mm) trong mat cat.
- Monkey-patching pattern: NEVIS patch vao MainWindow va PreviewView o cuoi file.
- 置き床 (oki-yuka): SL → +168mm chan do (支持脚) → +20mm ban (置床) → +12mm san go (フローリング) = FL tai SL+200mm.
