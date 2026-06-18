# Undo Transaction Plan

Date: 2026-06-18
Status: Plan only - no implementation or wiring approved

## Muc Tieu

Thiet ke mot transaction/token boundary cho undo snapshot chung cua NEVIS de
Apply Engine co the:

- Chup full pre-apply state truoc first write.
- Chi tao user-visible undo step khi Apply thanh cong.
- Huy transaction ma khong tao ghost snapshot neu Apply reject/rollback.
- Bao toan chinh xac undo stack khi stack dang day 3 buoc.

Transaction nay thuoc NEVIS common undo service, khong thuoc Apply Engine.
Tai lieu nay khong phe duyet sua `Nevis_no_ui.py` hoac wiring UI.

## 1. Hien Trang Undo V91

Patch V91 thay co che one-step undo cu bang system-wide stack:

- `_nevis_undo_stack`: danh sach full-model snapshots.
- `_nevis_undo_limit`: mac dinh 3.
- `undo_snapshot`: legacy alias tro toi top item.

Moi snapshot hien tai gom:

- `action`
- `copy.deepcopy(self.model)`
- `selected_node`
- `selected_edge`
- `selected_bushing_id`

`save_undo_snapshot(action)` dang:

1. Copy stack hien tai.
2. Deep-copy model va selection vao snapshot.
3. Append snapshot.
4. Neu vuot limit, trim va chi giu 3 item moi nhat.
5. Gan lai `_nevis_undo_stack` va `undo_snapshot`.

Method nay bat exception, ghi log, nhung khong return success/failure.

`undo_last_action()` dang:

1. Pop top snapshot.
2. Thay `self.model` bang full model trong snapshot.
3. Restore selection va clear pending operation.
4. Goi `rebuild_flow()` va `apply_common()`.
5. Refresh lai selected bushing/node/edge hoac toan view.

Ctrl+Z dung runtime V91 `undo_last_action()`. Vi full model bi thay, moi cached
reference toi model/edge truoc Undo se stale.

## 2. Vi Sao Goi Truc Tiep `save_undo_snapshot()` Chua Du

### Khong co prepare/commit boundary

Apply Engine co the fail sau snapshot:

- Validation race duoc phat hien lai ngay truoc write.
- Edge/lock/known state thay doi.
- Setter write phat sinh exception.
- Internal rollback thanh cong hoac that bai.

`save_undo_snapshot()` push ngay lap tuc, nen Apply failure se de ghost step.

### Stack bi trim qua som

Neu stack dang co 3 item, push snapshot moi se xoa oldest item ngay. Sau Apply
failure, chi pop item moi khong phuc hoi oldest item da bi trim. Undo history da
bi pha du model quay ve pre-apply state.

### Khong xac nhan duoc snapshot success

Method nuot exception va khong return status. Integration co the tiep tuc write
du snapshot chua duoc tao.

### Khong co public cancel API

Apply Engine khong duoc truy cap truc tiep `_nevis_undo_stack`. Hien khong co
public API de cancel pending snapshot, restore stack, hoac verify token owner.

### Khong bao ve nested/concurrent edit

Khong co active transaction marker. Mot helper long nhau co the push them
snapshot hoac Ctrl+Z co the thay model trong khi transaction dang active.

Vi vay, goi truc tiep `save_undo_snapshot()` chi phu hop voi operation don gian
ma mutation gan nhu chac chan xay ra ngay sau call. No chua du cho Apply
all-or-nothing transaction.

## 3. Transaction/Token Can Lam Gi

### Core semantics

Transaction can co ba phase:

1. Begin: capture full pre-operation state vao pending token, chua push stack.
2. Commit: sau successful mutation, append snapshot vao common stack va trim.
3. Rollback: restore full pre-operation state, discard pending token, giu common
   stack nguyen ven.

### Token data

Token nen la opaque object, khong phai dict de caller tu sua. Du lieu toi thieu:

- Unique token ID.
- Reason/action, vi du `apply_elevation_proposals`.
- Owner MainWindow/undo service identity.
- State: `ACTIVE`, `COMMITTED`, `ROLLED_BACK`, hoac `FAILED`.
- Full pre-operation model snapshot.
- Pre-operation selection fields.
- Stack generation/revision luc begin.
- Model instance/generation luc begin.
- Created timestamp optional cho diagnostic.

Token khong nen expose mutable model snapshot cho Apply Engine.

### Invariants

- Chi mot active model transaction tren mot MainWindow.
- Begin khong thay `_nevis_undo_stack` va khong trim history.
- Commit/rollback chi chap nhan active token dung owner.
- Token chi dung mot lan.
- Ordinary save/undo operation bi block hoac fail closed khi transaction active.
- UI/model mutation khac khong duoc xen vao transaction.
- Apply Engine khong doc/ghi private undo fields.

### Stack revision

Undo service nen co revision counter tang khi:

- Snapshot duoc commit/push.
- Undo pop stack.
- Stack bi clear/replace.

Token luu revision tai begin. Commit/rollback phai xac nhan revision chua doi.
Neu doi, transaction tra structured failure va giu recovery snapshot; khong
silently overwrite mot undo operation khac.

## 4. API De Xuat

### 4.1 `begin_model_transaction(reason)`

De xuat:

```python
token = begin_model_transaction(reason: str) -> ModelTransactionToken | None
```

Behavior:

1. Reject empty/invalid reason.
2. Reject neu da co active transaction.
3. Deep-copy model va capture selection.
4. Capture stack revision va model identity.
5. Tao opaque ACTIVE token.
6. Dang ky token la active.
7. Khong push stack, khong trim, khong doi `undo_snapshot`.
8. Return token; failure return structured result/`None` va khong mutate state.

Begin phai hoan tat thanh cong truoc khi first write duoc phep.

### 4.2 `commit_model_transaction(token)`

De xuat:

```python
result = commit_model_transaction(token) -> TransactionResult
```

Preconditions:

- Token dung owner, dang ACTIVE, va la active token hien tai.
- Stack revision bang revision luc begin.
- Model instance/generation phu hop expected transaction lifecycle.

Behavior:

1. Tao candidate stack tu current stack + token snapshot.
2. Chi luc nay moi trim candidate stack xuong `_nevis_undo_limit`.
3. Gan candidate stack atomically.
4. Cap nhat `undo_snapshot` toi top item.
5. Tang stack revision.
6. Mark token COMMITTED va clear active token.
7. Return structured success.

Commit khong deep-copy model lan hai. Snapshot trong token la pre-operation
state da capture tai begin.

Neu commit fail sau successful Apply, caller phai goi rollback transaction de
restore pre-operation model. Khong duoc de model da apply ma khong co undo step.

### 4.3 `rollback_model_transaction(token)`

De xuat:

```python
result = rollback_model_transaction(token) -> TransactionResult
```

Behavior:

1. Validate owner/state/revision.
2. Restore full model tu token pre-operation snapshot.
3. Restore selection va clear Apply/pending state lien quan.
4. Chay common model restore path: `rebuild_flow`, common refresh, selection
   refresh.
5. Khong append hoac trim common undo stack.
6. Bao dam `undo_snapshot` van tro toi top item cu.
7. Mark token ROLLED_BACK va clear active token.

Ngay ca khi Apply Engine da internal rollback endpoint fields thanh cong,
integration van goi transaction rollback/cancel de dong lifecycle va chung
minh full state/stack quay ve baseline. Full transaction restore la safety
backstop cho partial/unexpected mutation.

### 4.4 Phuong an ten API tuong duong

Co the dung:

- `prepare_undo_transaction(reason)`
- `commit_undo_transaction(token)`
- `cancel_undo_transaction(token, restore_model=True)`

Ten khong quan trong bang semantics. Bat buoc la begin khong push/trim, commit
moi push, rollback restore pre-state va khong thay history.

### 4.5 Compatibility voi `save_undo_snapshot()`

Hai huong duoc phep:

- Giu `save_undo_snapshot()` cho operation cu, va dung explicit transaction API
  chi cho operation all-or-nothing nhu Apply.
- Hoac refactor `save_undo_snapshot()` thanh one-shot begin + commit de dung
  chung capture/stack helper.

Khong bat buoc migrate tat ca call site trong blocker resolution dau tien.
Nhung common stack append/trim/alias logic nen co mot implementation duy nhat de
tranh lech semantics.

## 5. Xu Ly Khi Stack Day 3 Buoc

Gia su stack ban dau la `[A, B, C]`, limit 3.

### Begin

- Stack van la `[A, B, C]`.
- Token giu snapshot `D_pre` o pending storage.
- `A` chua bi xoa.

### Successful Apply + commit

- Candidate stack la `[A, B, C, D_pre]`.
- Commit trim atomically thanh `[B, C, D_pre]`.
- `undo_snapshot` tro toi `D_pre`.
- Mot Ctrl+Z restore pre-Apply model.

### Failed Apply + rollback

- Stack van la `[A, B, C]` trong suot transaction.
- Rollback discard pending `D_pre` sau khi restore model.
- Khong item nao bi trim; `A` van con.
- `undo_snapshot` van tro toi `C`.

Day la ly do begin khong duoc goi implementation push-and-trim hien tai.

Commit nen build new list va gan mot lan. Khong mutate live list roi moi trim,
de exception khong de stack o trang thai nua commit.

## 6. Huy Ghost Snapshot Neu Apply Rollback

Thiet ke de khong tao ghost ngay tu dau:

- Begin chi tao pending token ngoai common stack.
- Apply failure khong co committed undo entry de pop.
- Rollback restore model va discard pending token.

Wiring sequence sau nay:

1. Verify B6 report va endpoint-pair plan.
2. `token = begin_model_transaction("apply_elevation_proposals")`.
3. Neu begin fail: hard block, zero write.
4. Goi Apply Engine.
5. Neu Apply success: commit token.
6. Neu Apply failed/rolled back: rollback token.
7. Neu commit fail: rollback token; bao Apply operation failed.

Khong duoc:

- Push snapshot tai begin roi pop khi fail.
- Truy cap `_nevis_undo_stack` tu Apply Engine.
- Commit token truoc Apply success.
- De ACTIVE token ton tai sau khi handler ket thuc.

Neu rollback transaction cung fail, fail closed:

- Disable Apply/edits tiep theo.
- Giu token recovery snapshot.
- Khong save project.
- Bao structured fatal integration error.
- Khong tu dong clear token hoac history.

## 7. Cac Test Bat Buoc

### Begin tests

- Begin tren stack rong tao ACTIVE token va khong push stack.
- Begin tren stack day 3 khong trim oldest item.
- Deep-copy failure return failure, zero state change, zero write.
- Empty reason bi reject.
- Nested begin bi reject.
- Wrong owner/forged token bi reject.

### Commit tests

- Commit successful transaction tao dung mot undo step.
- Action/reason duoc giu dung.
- Stack rong thanh mot item.
- Stack 1/2 item tang dung mot.
- Stack day `[A,B,C]` commit thanh `[B,C,D]`.
- `undo_snapshot` tro toi committed top item.
- Token mark COMMITTED, khong commit lan hai.
- Stack revision mismatch hard-fail.
- Simulated commit failure khong de partial stack mutation.

### Rollback tests

- Rollback restore exact model va selection.
- Rollback khong thay stack rong/khong rong.
- Stack day 3 van giu exact `[A,B,C]` va top alias `C`.
- Token mark ROLLED_BACK, khong rollback lan hai.
- Internal Apply rollback + transaction rollback khong tao ghost step.
- Rollback chay rebuild/refresh path dung mot lan.
- Rollback failure giu recovery token va tra fatal result.

### Apply integration harness tests

Chua can wiring UI, nhung can test adapter/harness:

- Verify failure: khong begin transaction, zero undo step.
- Begin failure: Apply Engine khong duoc goi.
- Apply success + commit: exactly one undo step.
- Apply nhieu endpoints: van mot undo step.
- Apply write failure: engine rollback, transaction rollback, stack exact.
- Apply success nhung commit failure: full model rollback, stack exact.
- Ctrl+Z sau commit restore exact `start_z`/`end_z`.
- `Node.z` khong thay doi.
- Report/reference cu khong duoc reuse sau Ctrl+Z thay model object.

### Compatibility tests

- Existing `save_undo_snapshot()` operations van tao stack nhu truoc.
- Existing Ctrl+Z behavior van restore selection/view.
- Undo limit van la 3.
- Legacy `undo_snapshot` alias luon dung.
- Ordinary save/undo bi block an toan khi explicit transaction ACTIVE.
- Full `test_elevation*.py` van PASS.

## 8. Dieu Kien Duoc Phep Wiring Apply Engine

Chi duoc wiring khi:

1. Transaction/token API thuoc common NEVIS undo service da duoc review.
2. Begin khong push/trim stack.
3. Commit la diem duy nhat append/trim Apply undo snapshot.
4. Rollback restore full pre-state va giu exact pre-transaction stack.
5. Stack-full `[A,B,C]` success/failure tests PASS.
6. Snapshot/deep-copy failure fail closed truoc write.
7. Nested/wrong/stale token tests PASS.
8. Apply success tao exactly one common undo step.
9. Apply rollback/commit failure tao zero ghost step va khong mat history.
10. Ctrl+Z restore exact endpoint Z va selection.
11. Apply Engine khong truy cap private undo stack va khong co stack rieng.
12. Existing undo regression tests va full elevation suite PASS.
13. Khong thay save/open schema, khong ghi `Node.z`, khong Milestone C.
14. Co phe duyet rieng de sua `Nevis_no_ui.py` va wiring Apply action.

Neu mot dieu kien chua dat, safe stop la:

- Khong wiring Apply Engine.
- Khong expose Apply UI action.
- Giu endpoint-pair Apply Engine module-level only.
- Giu V91 undo behavior production hien tai.

## Ket Luan

Phuong an an toan nhat la pending token: begin capture full pre-state nhung
khong push stack; commit moi append/trim; rollback restore pre-state va discard
pending token. Thiet ke nay giai quyet ghost snapshot va stack-full history loss
bang invariant, thay vi co gang sua stack sau khi failure da xay ra.
