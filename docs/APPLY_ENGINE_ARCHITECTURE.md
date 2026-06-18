# Apply Engine Architecture

Date: 2026-06-17

## Context

Elevation Foundation B1-B6 is complete under a read-only scope.

The next milestone is Apply Engine: the first controlled write path from reviewed elevation proposal data into the model.

This document is architecture only. No implementation is included.

## 1. What Apply Engine Will Do

Apply Engine will:

- Read B6 Dry Run Review Report.
- Validate that only safe `Proposed` rows are eligible for apply.
- Create an apply plan from approved proposal rows.
- Snapshot all model fields that may be changed.
- Write approved proposed endpoint values into model edge endpoint elevation fields.
- Produce an apply result report.
- Preserve enough data for undo and rollback.
- Avoid writing blocked/skipped rows.
- Avoid resolving conflicts during apply.

Primary write targets:

- `edge.start_z`
- `edge.end_z`

Apply Engine may optionally update derived display-only state later, but the first architecture should treat `Node.z` as non-writeable because `Node.z` is derived/display only.

## 2. What Apply Engine Must Not Do

Apply Engine must not:

- Apply `Blocked by Conflict` rows.
- Apply `Blocked by Lock` rows.
- Apply `Skipped (Known Target)` rows.
- Resolve conflicts.
- Choose winners among conflicting proposals.
- Overwrite locked values.
- Overwrite known endpoint values unless explicitly approved by validation rules.
- Write `Node.z` as source-of-truth data.
- Calculate slope-derived elevation.
- Use catalog dimensions.
- Use physical offsets.
- Model B寸法.
- Model 差口M/L.
- Model 立て管有効長.
- Model multiple Z per port.
- Model physical invert elevation.
- Add hydraulic simulation.
- Implement Milestone C physical modeling.
- Change save/open schema in the first Apply Engine implementation.
- Add UI behavior directly into the engine.

## 3. Input From B6 Dry Run Report

Apply Engine input should be:

```python
ProposalReviewReport
```

Expected B6 fields:

- `proposal_result`
  - B5 proposal result.

- `rows`
  - Review rows classified as:
    - `Proposed`
    - `Blocked by Conflict`
    - `Blocked by Lock`
    - `Skipped (Known Target)`

- `summary`
  - Counts by classification.

- `warnings`
  - Report-only warnings.

Eligible input rows:

- Only rows with status `Proposed`.

Required row fields for apply:

- target edge index
- target endpoint
- proposed Z
- source edge index
- source endpoint
- reason/source metadata

Rows with missing target identity or missing proposed Z must be rejected before apply.

## 4. Output After Apply

Apply Engine should return a structured result:

```text
ApplyResult
  applied_steps
  skipped_steps
  rejected_steps
  undo_snapshot
  rollback_available
  summary
```

Expected output concepts:

- `applied_steps`
  - Rows successfully written to model edge endpoint fields.

- `skipped_steps`
  - Rows intentionally skipped, such as blocked/skipped B6 rows.

- `rejected_steps`
  - Rows rejected during validation.

- `undo_snapshot`
  - Exact pre-apply values for every field written.

- `rollback_available`
  - Boolean indicating whether the result can be rolled back.

- `summary`
  - Counts for applied/skipped/rejected.

Apply result should not silently hide partial failure. If only part of the apply succeeds, rollback strategy must decide whether to restore the whole transaction.

## 5. Validation Rules Before Apply

Apply Engine must validate all rows before writing.

Required validation:

- Row status must be `Proposed`.
- Target edge index must exist.
- Target endpoint must be `start` or `end`.
- Proposed Z must be present and numeric.
- Target endpoint must not be locked.
- Target endpoint must not already contain a known value unless overwrite is explicitly allowed.
- B6 report must not contain warnings that are configured as blocking.
- B6 summary must not show unresolved conflict rows if strict mode is enabled.
- The same target endpoint must not appear in more than one proposed row.

Default validation mode:

- Strict.
- No overwrite of existing endpoint Z.
- No write through locked edges.
- No conflict resolution.

Validation failure should prevent writes unless a future explicit partial-apply mode is approved.

## 6. Undo Strategy

Undo should be based on exact pre-apply snapshots.

For every write, store:

- edge index
- endpoint
- field name: `start_z` or `end_z`
- old value
- new value
- source proposal row identity

Undo should:

- Restore each written field to its old value.
- Not recalculate anything.
- Not touch fields not written by the apply operation.
- Produce an undo result report.

Undo should be available immediately after a successful apply result.

If the app already has an undo stack, Apply Engine should provide a compact operation object that can be pushed onto that stack by integration code.

## 7. Rollback Strategy

Rollback handles failure during apply.

Recommended strategy:

- Transaction-like best effort.
- Validate everything before first write.
- Snapshot everything before first write.
- If any write fails, restore all previously written fields from the snapshot.
- Return an apply result marked failed and rolled back.

Rollback should cover:

- Exceptions during write.
- Missing edge during write.
- Unexpected locked state detected during write.
- Type errors during write.

Rollback should not:

- Retry with modified values.
- Skip failed rows silently.
- Resolve conflicts.

## 8. Conflict Handling

Apply Engine must treat conflicts as blockers.

Rules:

- `Blocked by Conflict` rows are never applied.
- Candidate conflicts are never resolved during apply.
- Anchor conflicts are never resolved during apply.
- Duplicate target proposals are rejected.
- Conflicting proposed Z values are rejected.

Apply Engine may report:

- conflict row count
- affected target endpoints
- source proposal metadata

Apply Engine must not choose a winner.

## 9. Locked Value Handling

Apply Engine must treat locks as hard blockers.

Rules:

- `Blocked by Lock` rows are never applied.
- Any target edge with `elevation_locked=True` blocks writes to both endpoint Z fields unless a later endpoint-specific lock model exists.
- If lock state changes between dry run and apply, apply validation must re-check lock state and reject the row.
- Existing locked endpoint values must never be overwritten.

Apply Engine may report:

- locked edge index
- attempted endpoint
- proposal source
- reason

Apply Engine must not unlock or bypass locks.

## 10. Integration Points With `Nevis_no_ui.py`

Apply Engine should be implemented as a separate module first, not inside UI code.

Recommended integration points:

- Import the Apply Engine module from `Nevis_no_ui.py`.
- Pass the current model into the dry-run/review pipeline.
- Pass the B6 `ProposalReviewReport` into Apply Engine.
- Receive `ApplyResult`.
- Refresh existing report/summary views after apply.
- Push undo snapshot into existing undo mechanism if available.
- Mark model dirty after successful apply.

Potential UI integration later:

- Button: Apply reviewed elevation proposals.
- Confirmation dialog showing applied/skipped/rejected counts.
- Error dialog for validation failure.
- Undo command integration.

Integration constraints:

- `Nevis_no_ui.py` should not duplicate Apply Engine validation logic.
- Save/Open schema should not be changed until apply behavior is stable.
- UI should call the engine; the engine should not depend on UI classes.

## 11. Test Strategy

Apply Engine tests should be module-level first.

Required tests:

- Applies only `Proposed` rows.
- Does not apply `Blocked by Conflict`.
- Does not apply `Blocked by Lock`.
- Does not apply `Skipped (Known Target)`.
- Rejects missing target edge.
- Rejects invalid endpoint.
- Rejects missing/non-numeric proposed Z.
- Rejects duplicate target proposals.
- Rejects locked target edge.
- Rejects overwrite of existing endpoint Z in strict mode.
- Writes `edge.start_z` when target endpoint is `start`.
- Writes `edge.end_z` when target endpoint is `end`.
- Does not write `Node.z`.
- Creates undo snapshot before write.
- Undo restores previous values.
- Rollback restores previous values after simulated failure.
- Does not mutate model when validation fails.

Integration tests with `Nevis_no_ui.py` should come later and should be limited to wiring:

- UI calls engine.
- Result is displayed/refreshed.
- Dirty state/undo hook is triggered.

No Milestone C tests should be added for Apply Engine.

## 12. Completion Conditions

Apply Engine is complete when:

- It consumes B6 Dry Run Review Report.
- It validates proposed rows before writing.
- It applies only safe `Proposed` rows.
- It blocks conflict rows.
- It blocks locked rows.
- It skips known-target rows.
- It writes only `edge.start_z` and/or `edge.end_z`.
- It does not write `Node.z`.
- It does not resolve conflicts.
- It does not bypass locks.
- It does not perform Milestone C physical modeling.
- It returns structured apply result data.
- It creates undo snapshots.
- It can roll back partial failure.
- It has focused module-level tests for apply, validation, undo, and rollback.

Apply Engine is not complete if it requires UI, save/open schema changes, conflict resolution, lock bypass, physical modeling, or manual cleanup after failed apply.
