# Apply Engine Undo Integration Plan

Date: 2026-06-18
Status: Plan/investigation only - no wiring approved

## Muc tieu

Tai lieu nay xac dinh cach Apply Engine sau nay tham gia co che Undo chung cua
NEVIS ma khong tao undo stack rieng.

Pham vi hien tai chi la investigation va plan. Khong sua `Nevis_no_ui.py`,
khong wiring UI, va khong thay doi Apply Engine.

## 1. Co Che Undo Hien Tai Cua NEVIS

### 1.1 Implementation goc

`MainWindow` ban dau co:

- `save_undo_snapshot(action)`: luu mot dict gom action, deep copy cua model,
  selected node, selected edge, va selected bushing.
- `undo_last_action()`: thay `self.model` bang model trong snapshot, restore
  selection, chay `rebuild_flow()`, sau do refresh state/view.
- `self.undo_snapshot`: legacy one-step snapshot.

Ctrl+Z duoc noi voi `self.undo_last_action` qua `QAction` `act_undo`.

### 1.2 Runtime implementation thuc te

Patch V91 override ca hai method tren class `MainWindow`:

- `_nevis_undo_stack`: system-wide undo stack.
- `_nevis_undo_limit`: mac dinh 3.
- Moi snapshot chua:
  - `action`
  - `copy.deepcopy(self.model)`
  - `selected_node`
  - `selected_edge`
  - `selected_bushing_id`
- Khi stack vuot limit, chi giu 3 snapshot moi nhat.
- `self.undo_snapshot` van tro toi item moi nhat de giu compatibility.

Runtime `undo_last_action()`:

1. Block neu dang o read-only detail preview.
2. Pop snapshot moi nhat.
3. Thay toan bo `self.model` bang deep-copied pre-operation model.
4. Restore selection va clear pending operation.
5. Goi `rebuild_flow(self.model)`.
6. Goi `apply_common()` va refresh/select lai bushing, node, edge, hoac toan view.
7. Cap nhat trang thai undo con lai.

Do method V91 duoc gan lai vao `MainWindow` truoc khi instance chay, Ctrl+Z
thuc te dung V91 stack toi da 3 buoc, khong dung implementation one-step goc.

### 1.3 Dac diem quan trong

- Snapshot la full-model snapshot, khong phai field-level delta.
- Undo thay object `self.model`; moi reference cu den model/edge se stale sau
  Ctrl+Z.
- Snapshot luu selection nhung khong luu toan bo UI state.
- `save_undo_snapshot()` bat exception, ghi log, va khong return success/failure.
- Stack bi trim ngay khi snapshot duoc push.
- Khong co public API de discard/rollback mot snapshot vua push.

Hai diem cuoi la blocker can giai quyet truoc Apply wiring.

## 2. `save_undo_snapshot()` Dang Duoc Goi O Dau

Investigation tim thay cac call site production sau:

### Move/drag va topology optimization

- `slide_pipe_run`
- `move_pipe_run`
- `smart_drag_optimize`
- `move_special_equipment`

Drag paths dung flag nhu `_move_undo_saved` de chi luu mot snapshot cho mot lan
drag, khong luu mot snapshot moi cho moi mouse event.

### Bushing/reducer/IN topology edits

- `insert_bushing`
- `edit_bushing`
- `delete_bushing`
- `insert_in`
- `delete_in`
- `pending_insert_reducer`

### Material edits

- `branch_material`
- `clear_branch_material`

### Connection va special equipment

- `connect_orphan_centerline`
- `special_equipment` tai nhieu generation patch
- `quick_special_node`
- `quick_special_edge`
- `pending_insert_special`
- `quick_special_node_direct`

Pattern dung o cac flow tot la:

1. Xac nhan operation co the thuc hien.
2. Goi `save_undo_snapshot(action)` mot lan.
3. Mutate model.
4. Refresh UI.

Mot so patched flow co the goi helper long nhau. Apply integration khong duoc
copy pattern co nguy co double snapshot; adapter phai la owner duy nhat cua
snapshot cho mot Apply action.

## 3. Vi Tri Snapshot Khi Wiring Apply Engine

### 3.1 Thu tu bat buoc

Khi duoc phep wiring sau nay, thu tu phai la:

1. Build reviewed B6 report.
2. Resolve endpoint-pair identities.
3. Chay toan bo verify-before-write:
   - model/report context
   - edge existence
   - pair va orientation
   - global multi-edge uniqueness
   - duplicate target
   - conflict
   - lock
   - existing known value
   - proposed Z
4. Dong bang verified apply plan.
5. Xac nhan NEVIS undo service san sang.
6. Goi `save_undo_snapshot("apply_elevation_proposals")` dung mot lan.
7. Xac nhan snapshot da duoc push thanh cong.
8. Goi Apply Engine de write transaction.
9. Neu success, commit undo step va refresh UI/state.
10. Neu engine rollback, restore undo stack ve dung trang thai truoc buoc 6.

Snapshot phai nam sau tat ca preflight verification nhung ngay truoc first
write. Khong duoc dat snapshot trong loop tung Proposed row.

### 3.2 Can mot undo transaction boundary cua NEVIS

`save_undo_snapshot()` hien khong return status va khong co public discard.
Apply wiring can mot boundary nho thuoc NEVIS undo service, khong thuoc Apply
Engine. Boundary can dam bao:

- Save dung full pre-apply model bang co che chung.
- Tra ve success/token co the verify.
- Commit token khi apply thanh cong.
- Cancel token neu validation muon, write failure, hoac internal rollback.
- Cancel phai restore undo stack chinh xac nhu truoc operation.

Chi pop item moi nhat sau failure la chua du. Neu stack da day 3 buoc,
`save_undo_snapshot()` trim item cu nhat ngay lap tuc; pop snapshot moi se lam
mat vinh vien item cu. Cancel transaction phai bao toan ca item bi trim.

Neu khong co public transaction/cancel API, chua duoc wiring. Apply Engine khong
duoc truy cap truc tiep `_nevis_undo_stack` de tu sua van de nay.

### 3.3 Snapshot confirmation

Vi `save_undo_snapshot()` nuot exception, wiring khong duoc gia dinh call xong
la snapshot thanh cong. Lua chon can review:

- Cho method chung return structured success/token; hoac
- Them public undo transaction API bao quanh method hien tai.

Khong nen tiep tuc write neu khong chung minh duoc pre-apply snapshot da ton
tai.

## 4. Vi Sao Apply Engine Khong Duoc Co Undo Stack Rieng

- NEVIS da co mot Ctrl+Z entry point va system-wide ordering cho moi edit.
- Hai stack rieng se khong biet operation nao xay ra sau cung.
- Ctrl+Z co the undo operation khac trong khi Apply endpoint changes van con.
- Full-model undo thay `self.model`; compact Apply snapshot co the giu stale
  edge/index references sau mot undo/topology edit.
- Hai stack co the tao double undo cho cung mot Apply.
- Selection, flow rebuild, pending state, va UI refresh chi duoc co che NEVIS
  undo xu ly day du.
- Undo history limit 3 phai ap dung nhat quan cho Apply va moi operation khac.

Phan biet hai khai niem:

- Apply Engine snapshot: transaction rollback khi write dang chay bi loi.
- NEVIS snapshot: user-visible Undo sau successful Apply.

Engine snapshot duoc giu de rollback/audit, nhung khong duoc push thanh mot
undo stack thu hai hoac noi truc tiep voi Ctrl+Z.

## 5. Tests Can Co Truoc Khi Wiring

### 5.1 Apply tao dung mot undo step

Test voi stack rong, stack co san item, va stack day 3 item:

- Verified successful Apply goi common undo snapshot dung mot lan.
- Action label la `apply_elevation_proposals`.
- Stack tang mot logical step; khi day, limit van la 3.
- Khong co snapshot theo tung row.
- Validation/conflict/lock/multi-edge failure tao zero undo step.
- UI/helper long nhau khong tao duplicate snapshot.

### 5.2 Ctrl+Z khoi phuc `start_z`/`end_z`

- Apply mot target `start_z`, Ctrl+Z restore exact old value.
- Apply mot target `end_z`, Ctrl+Z restore exact old value.
- Apply nhieu endpoints trong mot transaction, mot Ctrl+Z restore tat ca.
- `Node.z` khong thay doi do Apply hoac undo.
- Selection duoc restore.
- Model sau undo da chay `rebuild_flow()` va view refresh path.
- Undo chi Apply step, khong undo them operation truoc no.

Test can trigger cung `undo_last_action()` ma Ctrl+Z QAction dung, khong goi
compact `undo_elevation_apply()` thay the.

### 5.3 Internal rollback khong pha common undo stack

Voi stack rong, mot item, va day 3 item:

- Inject failure tai write dau va write giua transaction.
- Apply Engine rollback endpoint fields day du.
- Common undo stack sau cancel giong chinh xac pre-call stack:
  - cung so item
  - cung order
  - cung action
  - khong mat oldest item khi stack tung day
- `undo_snapshot` legacy alias van tro dung top item cu.
- Khong co ghost Apply step.
- Undo operation truoc Apply van hoat dong binh thuong.

### 5.4 Snapshot failure

- Inject `copy.deepcopy` failure hoac save failure.
- Apply khong duoc write bat ky endpoint nao.
- Undo stack giu nguyen.
- Ket qua tra ve structured integration error.

### 5.5 Integration boundary

- Test sequencing: verify -> snapshot -> first write -> refresh.
- Khong snapshot neu fresh B6 report mismatch.
- Khong refresh nhu success neu engine rolled back.
- Full `test_elevation*.py` van PASS.
- Test khong can save/open schema va khong ghi `Node.z`.

## 6. Rui Ro Neu Goi Snapshot Sai Thoi Diem

### Qua som

Neu snapshot truoc validation/identity verification:

- Rejected Apply tao ghost undo step.
- Stack day co the mat oldest valid history du khong write gi.
- Nguoi dung Ctrl+Z thay model khong thay doi va mat niem tin vao undo.

### Qua muon

Neu snapshot sau first write hoac sau Apply success:

- Snapshot chua partial/post-apply state.
- Ctrl+Z khong restore dung pre-apply Z.
- Failure giua transaction co the khong co full-model recovery point.

### Goi nhieu lan

Neu snapshot trong loop hoac ca UI va adapter cung goi:

- Mot Apply chiem nhieu undo steps.
- Mot Ctrl+Z chi restore mot phan endpoints.
- Stack limit 3 bi day va trim history rat nhanh.

### Snapshot failure bi bo qua

Vi method hien tai nuot exception, write co the thanh cong ma khong co Ctrl+Z.
Wiring phai fail closed neu snapshot khong duoc confirm.

### Rollback nhung khong cancel undo transaction

- Tao ghost undo step.
- Neu stack day, oldest history co the da bi mat.
- Legacy `undo_snapshot` co the tro sai item.

### Reference lifecycle

Sau Ctrl+Z, `self.model` la object moi. Adapter/UI khong duoc cache model, edge,
report, hoac ApplyResult references de reuse sau undo. Phai build lai review tu
model hien tai.

## 7. Dieu Kien Duoc Phep Wiring

Chi duoc wiring Apply Engine vao `Nevis_no_ui.py` khi tat ca dieu kien sau dat:

1. Endpoint-pair verifier production va full elevation tests van PASS.
2. Undo owner duoc xac nhan la NEVIS common undo service.
3. Co public snapshot transaction/token hoac giai phap tuong duong da review.
4. Snapshot success co the duoc confirm; save failure phai block write.
5. Failed Apply/rollback restore undo stack chinh xac, ke ca stack day 3 item.
6. Successful Apply tao dung mot undo step.
7. Ctrl+Z restore exact `start_z`/`end_z`, selection, va refresh model/view.
8. Apply Engine khong truy cap `_nevis_undo_stack` va khong co UI undo stack.
9. Validation failure tao zero undo step.
10. Tat ca tests tai muc 5 PASS.
11. Khong thay save/open schema, khong ghi `Node.z`, khong Milestone C.
12. Co phe duyet rieng de sua `Nevis_no_ui.py` va wiring UI.

Neu bat ky dieu kien nao chua dat, safe stop la:

- Apply Engine van module-level only.
- NEVIS common undo code giu nguyen.
- `Nevis_no_ui.py` khong import/call Apply Engine.
- Khong co user-visible Apply action.

## Ket Luan

NEVIS da co full-model undo stack phu hop de lam owner cho Apply Engine. Vi tri
snapshot dung la sau toan bo verify va ngay truoc first write. Blocker con lai
khong phai cach restore Z, ma la transaction lifecycle cua undo snapshot:
confirm save, commit success, va cancel failure ma khong lam mat history khi
stack day. Can giai quyet va test public boundary nay truoc wiring.
