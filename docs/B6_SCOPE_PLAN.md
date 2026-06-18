# B6 Scope Plan - Proposal Review / Dry Run Report

Date: 2026-06-17

## Decision Context

B5 produces `PropagationProposalResult` as read-only propagation proposal data. B6 will convert that result into reviewable report data.

B6 is still not Apply. B6 does not write to the model and does not perform UI/save/open/preview/apply integration.

## 1. Goal

B6 will create a human-reviewable dry-run report from B5 proposal data.

The report will classify each proposal or blocked item into:

- Proposed
- Blocked by Conflict
- Blocked by Lock
- Skipped (Known Target)

B6 should answer this narrow question:

What would the propagation proposal do if reviewed, and why are some items blocked or skipped?

## 2. Input From B5

B6 input should be the B5 result:

```python
build_elevation_proposals(model)
```

Expected B5 fields:

- `conflict_lock_result`
  - B4 safety report.

- `known_endpoint_z`
  - Known endpoint values copied from upstream.
  - Read-only.

- `proposal_steps`
  - Proposed dry-run steps.
  - Not applied.

- `blocked_steps`
  - Steps blocked by conflict, lock, known target, or other safety reasons.

B6 may read metadata inside each B5 step:

- source edge index
- source endpoint
- source node ID
- source Z
- target edge index
- target endpoint
- target node ID
- proposed Z copied from B5
- reason

B6 must not modify B5 data or model data.

## 3. Output Review Report

B6 output should be a read-only review report object or equivalent structure.

Expected output concepts:

- `proposal_result`
  - The B5 result or a reference-safe copy.

- `rows`
  - Ordered review rows.
  - Each row is classified as Proposed, Blocked by Conflict, Blocked by Lock, or Skipped (Known Target).

- `summary`
  - Counts by classification.

- `warnings`
  - Non-mutating notes for malformed or unknown reasons.

B6 output is review data only. It is not an apply plan and does not contain apply actions.

## 4. Report Structure

Proposed public data structures:

```text
ProposalReviewReport
  proposal_result
  rows
  summary
  warnings

ProposalReviewRow
  status
  source_edge_index
  source_endpoint
  target_edge_index
  target_endpoint
  target_node_id
  source_z
  proposed_z
  reason
  source_label

ProposalReviewSummary
  proposed_count
  blocked_by_conflict_count
  blocked_by_lock_count
  skipped_known_target_count
  warning_count
```

Status values:

- `Proposed`
- `Blocked by Conflict`
- `Blocked by Lock`
- `Skipped (Known Target)`

Reason mapping:

- `anchor_conflict_at_source_node` -> `Blocked by Conflict`
- `anchor_conflict_at_target_node` -> `Blocked by Conflict`
- `candidate_conflict` -> `Blocked by Conflict`
- `multiple_candidates_for_target` -> `Blocked by Conflict`
- `source_edge_locked` -> `Blocked by Lock`
- `target_edge_locked` -> `Blocked by Lock`
- `known_endpoint_edge_locked` -> `Blocked by Lock`
- `target_already_known` -> `Skipped (Known Target)`

Unknown reasons should remain report-only warnings and should not be applied.

## 5. Expected Tests

Planned B6 tests should verify:

- B6 reads B5 `PropagationProposalResult`.
- B6 creates `Proposed` rows from `proposal_steps`.
- B6 creates `Blocked by Conflict` rows from conflict-related blocked reasons.
- B6 creates `Blocked by Lock` rows from lock-related blocked reasons.
- B6 creates `Skipped (Known Target)` rows from known-target blocked reasons.
- B6 creates summary counts.
- B6 preserves source and target metadata.
- B6 does not mutate model nodes.
- B6 does not mutate model edges.
- B6 does not write `Node.z`.
- B6 does not write `edge.start_z`.
- B6 does not write `edge.end_z`.
- B6 does not create apply actions.

Tests that must not be part of B6:

- UI tests.
- Save/open persistence tests.
- Preview/apply tests.
- Physical fitting geometry tests.
- Catalog dimension tests.
- Apply execution tests.
- Model mutation tests that expect writes.

## 6. Completion Conditions

B6 is complete when:

- It consumes B5 proposal output.
- It creates reviewable report rows.
- It classifies rows into Proposed, Blocked by Conflict, Blocked by Lock, and Skipped (Known Target).
- It creates summary counts.
- It preserves source/target metadata.
- It does not mutate the model.
- It does not write `Node.z`.
- It does not write `edge.start_z`.
- It does not write `edge.end_z`.
- It does not apply proposals.
- It does not add UI/save/open/preview/apply integration.
- It does not introduce Milestone C physical modeling.

B6 is not complete if review requires applying data to the model, resolving conflicts, enforcing locks, or creating UI/save/open behavior.
