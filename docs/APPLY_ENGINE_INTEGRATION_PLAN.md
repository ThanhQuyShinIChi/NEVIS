# Apply Engine Integration Plan

Date: 2026-06-18

## Muc tieu

Tai lieu nay xac dinh cach tich hop Apply Engine voi model thuc trong
`Nevis_no_ui.py`.

Pham vi cua tai lieu chi la phan tich va ke hoach integration. Tai lieu khong
phe duyet UI, save/open integration, Milestone C, hoac thay doi write contract
cua Apply Engine.

## 1. Du lieu Apply Engine dang gia dinh ton tai

Apply Engine nhan hai doi tuong:

- `model`: doi tuong model co the truy cap bang duck typing.
- `ProposalReviewReport`: ket qua B6 duoc tao tu cung model.

### 1.1 Model contract

Apply Engine dang gia dinh:

- `model.edges` ton tai, co the index bang so nguyen, va thu tu edge khong thay
  doi tu luc tao B6 report den luc apply.
- Moi target edge co cac attribute writable:
  - `start_z`
  - `end_z`
  - `elevation_locked`
- `elevation_locked=True` khoa ca hai endpoint cua edge.
- Gia tri chua biet cua `start_z`/`end_z` la `None`.
- Gia tri Z de ghi la so huu han; `bool`, `NaN`, va infinity khong hop le.
- Khong co tac vu khac thay doi model trong khoang validation/snapshot/write.
- `Node.z` khong phai write target va khong can co de Apply Engine hoat dong.

Pipeline B1-B6 con gia dinh model co:

- `model.nodes`: mapping tu node ID sang node.
- `model.level_datums`: mapping tu level ID sang datum.
- Node co `id`, `level_id`; `Node.z` bi bo qua khi tim anchor.
- Edge co `a`, `b`, `start_level_id`, `end_level_id`, `start_z`, `end_z`,
  `elevation_locked`.
- Level datum co `elevation_mm`.
- `model.edges[index]` la cung edge ma B2-B6 da dung de tao target identity.

### 1.2 Review report contract

Apply Engine dang gia dinh:

- Report duoc tao boi B6 va chua `proposal_result`, `rows`, `summary`,
  `warnings`.
- Chi row co status `Proposed` la write candidate.
- Moi `Proposed` row co target edge index, endpoint `start` hoac `end`, va
  `proposed_z` hop le.
- `proposal_result.known_endpoint_z` phan anh model tai thoi diem dry run.
- Cung mot target endpoint khong xuat hien trong nhieu `Proposed` rows.
- Report va model van cung mot revision logic khi apply.

### 1.3 Transaction contract

- Tat ca row duoc validate truoc write dau tien.
- Snapshot ghi lai dung old/new value cua moi field se thay doi.
- Neu bat ky write nao loi, tat ca field trong snapshot duoc restore.
- Apply Engine chi thay doi `edge.start_z` hoac `edge.end_z`.
- Apply Engine khong refresh UI, khong danh dau dirty, khong save project, va
  khong tu dua operation vao undo stack cua NEVIS.

## 2. Doi chieu voi model that trong `Nevis_no_ui.py`

### 2.1 Cac diem tuong thich

Model thuc phu hop voi core contract:

- `PipeModel.edges` la `List[Edge]`.
- `PipeModel.nodes` la `Dict[int, Node]`.
- `PipeModel.level_datums` la `Dict[str, LevelDatum]`.
- `Edge` co `a`, `b`, `start_level_id`, `end_level_id`, `start_z`, `end_z`, va
  `elevation_locked`.
- `Node` co `id`, `z`, va `level_id`.
- `LevelDatum` co `elevation_mm`.
- `start_z` va `end_z` dung `None` cho unknown value.
- `Edge` la dataclass mutable, nen `setattr(edge, "start_z"/"end_z", value)`
  phu hop voi write mechanism hien tai.
- Project payload hien tai da luu `start_z`, `end_z`, va `elevation_locked`;
  Apply Engine khong can doi schema de ghi vao model in-memory.

Endpoint orientation cung phu hop:

- `start` tuong ung node `edge.a` va field `edge.start_z`.
- `end` tuong ung node `edge.b` va field `edge.end_z`.

### 2.2 Hanh vi hien tai lien quan

`Nevis_no_ui.py` da co nhieu write path elevation cu:

- Sua metadata tren selected edge.
- Copy edge elevation sang `Node.z`.
- Sync elevation tu `Node.z` ve edge.
- Propagate simple chain, ghi ca endpoint Z va `Node.z`.

Nhung write path nay khong phai Apply Engine va khong duoc goi gian tiep trong
integration moi. Dac biet, wiring Apply Engine khong duoc tai su dung ham cu nao
co the ghi `Node.z`.

NEVIS cung co undo mechanism rieng:

- `save_undo_snapshot()` deep-copy toan bo model.
- Ban patch V91 thay undo mot buoc bang stack toi da ba full-model snapshots.
- `undo_last_action()` thay `self.model` bang ban deep copy, goi
  `rebuild_flow()`, sau do refresh selection/view.

Apply Engine lai tra compact endpoint snapshot. Hai co che cung phuc vu undo
nhung chua co adapter hoac ownership rule chung.

Khong tim thay model revision token hoac co che dirty-state ro rang. Project
duoc save qua lenh explicit; Apply Engine khong nen tu dong save.

## 3. Nhung khac biet can xu ly

### 3.1 Target identity la integration blocker chinh

Apply Engine/B6 hien dinh danh target bang `edge_index`. Model thuc khong co
stable edge ID va co nhieu operation thay toan bo `model.edges`, filter edge
cu, sau do append edge moi. Vi vay:

- Cung mot index co the tro sang edge khac sau split/delete/connect.
- Index van hop le khong co nghia la identity van dung.
- `Edge.key` dua tren cap node khong huong, trong khi `start`/`end` phu thuoc
  huong `a`/`b`.
- Chi doi chieu `Edge.key` la chua du neu edge duoc tao lai voi huong dao nguoc.

Integration gate bat buoc: truoc wiring phai co stale-report/identity guard.
Guard toi thieu can dong bang target identity khi tao review va xac minh lai
`edge_index`, `a`, `b`, endpoint-to-node mapping truoc apply. Neu identity khong
khop, phai reject toan bo va yeu cau build lai B6 report. Khong duoc tim edge
"gan giong" va tiep tuc ghi.

Lua chon dai han tot hon la them stable edge ID, nhung day la thay doi model
contract rieng va khong nam trong wiring nho dau tien.

### 3.2 Report staleness

Model khong co revision counter. Giua review va apply, cac thay doi sau co the
lam report stale:

- Them/xoa/split/reconnect edge.
- Dao huong `a`/`b` khi tao lai edge.
- Thay `start_z`, `end_z`, level ID, hoac LevelDatum.
- Thay `elevation_locked`.

Apply Engine da kiem tra lai lock va known value tai apply, nhung chua du de
phat hien moi thay doi topology/identity. Can fingerprint/revision check o
integration boundary hoac mo rong engine contract truoc wiring.

### 3.3 Undo ownership

Can chon mot owner duy nhat cho user-visible undo:

- Khong nen vua push full-model snapshot vua expose compact undo nhu hai action
  doc lap cho cung mot apply.
- Goi `save_undo_snapshot()` truoc validation co the tao ghost undo khi apply bi
  reject.
- Goi no sau apply la qua tre de chup pre-apply model.
- Tu chen snapshot vao `_nevis_undo_stack` se phu thuoc vao chi tiet patch V91
  va khong nen lam truc tiep.

Huong wiring an toan dau tien: integration adapter tao pre-apply full-model
snapshot tam, chi commit snapshot do vao public undo mechanism sau khi apply
thanh cong, hoac them mot public API nhan prebuilt snapshot. Quyet dinh nay can
duoc test rieng truoc khi sua `MainWindow`.

Compact snapshot cua Apply Engine van la nguon phuc hoi transaction va co the
lam fallback, nhung khong tu dong thay the undo stack hien tai.

### 3.4 Refresh va state sau apply

Engine khong biet cac ham refresh cua `MainWindow`. Integration layer sau khi
apply thanh cong se can cap nhat toi thieu:

- Selected edge elevation controls, neu selected edge bi anh huong.
- Elevation report.
- Selected elevation summary.
- Preview/model drawing neu view hien thi endpoint elevation.
- Status va kha nang Undo.

Khong co dirty flag ro rang de set. Khong duoc tu tao dirty semantics trong
wiring dau tien; neu can, phai thanh mot scope rieng.

### 3.5 Import boundary

`Nevis_no_ui.py` import PySide6 va chay nhieu runtime patch trong cung module.
Module Apply Engine khong nen import `Nevis_no_ui.py`. Dependency phai mot
chieu: NEVIS/integration adapter import pipeline va Apply Engine.

Contract test voi `PipeModel` thuc co the can import module lon va PySide6.
Khong nen dua Qt type hoac `MainWindow` vao `modules/elevation_apply.py`.

## 4. Integration risks

### Critical

- Stale `edge_index` ghi Z vao sai edge nhung van khong phat sinh exception.
- Edge duoc tao lai voi `a`/`b` dao chieu lam `start`/`end` tro sang sai node.
- Undo snapshot duoc tao sai thoi diem, khong the phuc hoi pre-apply state.

### High

- Model thay doi sau B6 review nhung truoc apply, trong khi khong co revision
  token.
- Existing elevation write paths tiep tuc hoat dong song song va bypass strict
  conflict/lock policy cua Apply Engine.
- Full-model undo va compact engine undo xung dot, tao double undo hoac restore
  model cu khong mong muon.
- UI refresh loi sau apply co the lam view hien thi du lieu cu du model da ghi
  thanh cong.

### Medium

- Level-derived known value co explicit endpoint field la `None`; integration
  phai giu `known_endpoint_z` trong validation, khong chi kiem tra field.
- Direct import `Nevis_no_ui.py` trong test co the phu thuoc PySide6 va cac
  runtime monkey patch.
- Deep-copy full model cho undo co chi phi tren graph lon.
- Project open thay `self.model` bang instance moi, lam report/snapshot cu vo
  hieu.
- Warnings hoac conflict tu report cu co the khong con phan anh model hien tai.

## 5. Test can co truoc khi wiring

Day la test gate. Khong sua `MainWindow` truoc khi cac test module/integration
boundary sau dat.

1. Real model contract:
   - Tao `PipeModel`, `Node`, `Edge`, `LevelDatum` thuc.
   - Chay B1-B6 va Apply Engine tren model thuc.
   - Xac nhan chi `start_z`/`end_z` thay doi va `Node.z` giu nguyen.

2. Endpoint orientation:
   - Test ca target `start` va `end`.
   - Test edge co `a > b` de bao dam logic khong suy endpoint tu sorted key.

3. Stale identity:
   - Tao report, sau do reorder `model.edges`.
   - Tao report, sau do replace target edge tai cung index.
   - Tao report, sau do dao `a`/`b`.
   - Tat ca phai reject toan bo va khong mutate.

4. Stale values and locks:
   - Lock target sau review.
   - Gan explicit endpoint Z sau review.
   - Doi LevelDatum/level ID de target tro thanh known sau review.
   - Tat ca phai reject truoc write.

5. Transaction:
   - Nhieu target tren real-model-compatible fixture.
   - Inject loi o write giua transaction.
   - Xac nhan moi endpoint, ke ca field bi partial write, duoc restore.

6. Undo adapter:
   - Successful apply tao dung mot undo entry.
   - Validation failure va rolled-back failure khong tao ghost undo.
   - Undo phuc hoi endpoint Z, selection, va model/view state can thiet.

7. Model replacement:
   - Tao report tren model A, sau do open/replace bang model B.
   - Apply report cua A vao B phai bi reject.

8. Performance sanity:
   - Do thoi gian build review, snapshot, apply, va full-model undo snapshot tren
     graph lon dai dien.
   - Khong ha strict validation de doi lay toc do.

9. Regression:
   - Toan bo `test_elevation*.py` van PASS.
   - Save/open schema va `Node.z` khong thay doi.

## 6. Ke hoach wiring theo tung buoc nho

### Buoc 0 - Dong bang contract

- Ghi nhan input/output contract cua B6 va Apply Engine.
- Chon identity guard toi thieu cho target edge.
- Chon ownership cua user-visible undo.
- Khong wiring neu hai quyet dinh nay chua duoc duyệt.

### Buoc 1 - Real-model contract tests

- Them test dung class model thuc hoac mot contract harness trich xuat an toan.
- Khong instantiate `MainWindow`.
- Chung minh pipeline va engine chay tren `PipeModel` thuc.

### Buoc 2 - Them stale-report guard

- Luu target identity/fingerprint cung review/apply plan.
- Xac minh model instance/revision, edge index, `a`, `b`, va endpoint node truoc
  write.
- Identity mismatch tra structured rejection; khong auto-remap.
- Chay lai module tests va stale identity tests.

### Buoc 3 - Tao integration adapter khong UI

- Adapter nhan model thuc va B6 report.
- Adapter chi dieu phoi identity check, undo preparation, call engine, va tra
  structured integration result.
- Adapter khong import Qt widget, khong save file, khong ghi `Node.z`.
- Test adapter doc lap voi model thuc.

### Buoc 4 - Giai quyet undo bridge

- Tao pre-apply full-model snapshot tam qua public boundary.
- Chi commit mot undo entry sau successful apply.
- Neu apply reject/rollback, huy snapshot tam.
- Kiem chung Ctrl+Z/undo stack restore dung mot operation.

### Buoc 5 - Wiring toi `MainWindow` o mot entry point rieng

- Chi thuc hien sau phe duyet rieng cho viec sua `Nevis_no_ui.py`.
- Entry point phai build review moi hoac xac minh report revision ngay truoc
  apply.
- Goi integration adapter; khong lap lai validation trong UI.
- Khong tai su dung cac ham elevation cu co ghi `Node.z`.

### Buoc 6 - Post-apply refresh

- Chi refresh sau successful apply.
- Cap nhat elevation controls/report/summary va preview can thiet.
- Hien structured applied/skipped/rejected counts.
- Khong auto-save va khong thay save/open schema.

### Buoc 7 - Integration verification

- Chay contract, adapter, undo, va full elevation tests.
- Manual smoke test tren mot project nho co selection, conflict, lock, va known
  value.
- Manual undo ngay sau successful apply.
- Xac nhan `Node.z`, topology, fitting, flow, va project schema khong thay doi.

Moi buoc phai co commit/review boundary rieng. Khong gop identity guard, undo,
UI entry point, va refresh vao mot thay doi lon.

## 7. Diem dung an toan neu integration that bai

### Truoc write

Dung va tra rejection neu:

- Report/model identity khong khop.
- Edge index, `a`/`b`, hoac endpoint node khong khop fingerprint.
- Conflict, lock, warning blocking, duplicate target, known value, hoac invalid Z
  xuat hien.
- Khong tao duoc pre-apply undo state.

Tai diem nay model phai giu nguyen. Build lai B6 report la hanh dong duy nhat
duoc phep; khong auto-fix hoac partial apply.

### Trong write

- De Apply Engine rollback toan bo snapshot.
- Neu rollback thanh cong, khong commit undo entry va khong refresh nhu mot
  successful apply.
- Neu rollback khong thanh cong, vo hieu hoa apply tiep theo, giu recovery
  snapshot/result, thong bao loi nghiem trong, va khong save model.

### Sau write

- Neu model apply thanh cong nhung UI refresh loi, khong chay apply lan hai.
- Giu ApplyResult va undo state de phuc hoi; refresh lai view doc lap.
- Neu undo bridge khong duoc chung minh dung, dung integration o adapter level
  va khong wiring vao user action.

### Safe baseline

Safe baseline luon la:

- Elevation Foundation B1-B6 van read-only.
- Apply Engine van la module doc lap da test.
- `Nevis_no_ui.py` khong goi Apply Engine.
- Khong co UI, save/open, `Node.z`, hoac Milestone C change.

Neu bat ky integration gate nao khong dat, quay ve baseline nay ma khong can
revert du lieu model hoac sua project file thu cong.

## Ket luan

Core field contract giua Apply Engine va `PipeModel` hien tai la tuong thich.
Tuy nhien, chua an toan de wiring truc tiep vi target identity dua tren
`edge_index` khong ben vung va undo ownership chua duoc quyet dinh. Hai van de
nay, cung real-model contract tests, la dieu kien bat buoc truoc moi thay doi
trong `Nevis_no_ui.py`.
