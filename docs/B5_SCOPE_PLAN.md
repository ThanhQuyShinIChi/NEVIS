# B5 Scope Plan - Propagation Planning

Date: 2026-06-17

## Decision Context

B4 is temporarily approved as the Conflict & Lock Framework.

B5 may start as Propagation Planning, but only as read-only planning data. B5 must not calculate final elevation values and must not write to the model.

## 1. What B5 Will Do

B5 will:

- Read B1 anchor data through downstream results.
- Read B2 wavefront topology and candidate paths.
- Read B3 candidate evaluation result.
- Read B4 conflict and lock reports.
- Select only candidates that are safe to include in a propagation plan.
- Create read-only propagation proposal records.
- Mark blocked candidates with reasons.
- Preserve full source metadata from B1/B2/B3/B4.
- Define what future propagation would need to consume.

B5 should answer this narrow question:

Which evaluated candidates may be included in a future propagation proposal, and which are blocked by known values, conflicts, locks, or missing metadata?

## 2. What B5 Must Not Do

B5 must not:

- Mutate the model.
- Write `Node.z`.
- Write `edge.start_z`.
- Write `edge.end_z`.
- Overwrite known values.
- Resolve conflicts.
- Choose a winner among conflicting candidates.
- Apply proposal data.
- Calculate final elevation values.
- Calculate slope-derived elevation.
- Implement real propagation.
- Implement Apply.
- Add UI.
- Change save/open behavior.
- Add preview/apply integration.
- Use catalog dimensions.
- Use physical offsets.
- Model B寸法.
- Model 差口M/L.
- Model 立て管有効長.
- Model multiple Z per port.
- Model physical invert elevation.
- Add hydraulic simulation.
- Implement Milestone C physical modeling.

## 3. Input From B1/B2/B3/B4

B5 should normally read one top-level B4 result:

```python
build_conflict_lock_report(model)
```

Through that B4 result, B5 can access:

### From B1 - Anchor

- `known_endpoint_z`
- `endpoint_anchors`
- `node_anchors`
- `initial_frontier`
- anchor source metadata

### From B2 - Wavefront

- `wavefront_nodes`
- `candidate_paths`
- `skipped`
- candidate topology metadata

### From B3 - Evaluation

- `usable_candidates`
- `blocked_candidates`
- `conflict_reports`
- `lock_reports`
- evaluated candidate metadata

### From B4 - Conflict & Lock Framework

- `anchor_conflicts`
- `candidate_conflicts`
- `lock_conditions`
- `known_endpoint_z`
- report-only safety metadata

B5 may inspect model topology only to preserve identity metadata. It must not write anything back.

## 4. Output Of B5

B5 output should be a read-only propagation plan result.

Expected output concepts:

- `conflict_lock_result`
  - The B4 result or a reference-safe copy.

- `proposal_steps`
  - Read-only proposal records for candidates allowed by B4.
  - These are not applied and do not write target values.

- `blocked_steps`
  - Candidate records excluded from proposal with blocking reason.

- `source_known_endpoint_z`
  - Copy of known endpoint values used for planning.
  - Must not be overwritten.

- `planning_notes`
  - Non-mutating notes for future dry-run propagation.

B5 output must remain declarative. It is a plan for future propagation, not propagation itself.

## 5. Expected Propagation Proposal Data Structure

Proposed public data structures:

```text
PropagationPlanResult
  conflict_lock_result
  source_known_endpoint_z
  proposal_steps
  blocked_steps
  planning_notes

PropagationProposalStep
  source_kind
  source_node_id
  source_edge_index
  source_endpoint
  source_z
  target_node_id
  target_edge_index
  target_endpoint
  topology_degree
  source_label
  status
  reason

BlockedPropagationStep
  target_edge_index
  target_endpoint
  reason
  source_edge_index
  source_endpoint
```

Important rule:

- `source_z` may be copied from B1/B2 metadata for provenance.
- B5 must not create `target_z`, `proposed_z`, or any newly calculated elevation field.

## 6. Conflict Handling Rule - Blocked / Report-Only

B5 must treat conflicts as blockers.

Blocked conflict cases:

- Target endpoint appears in B4 `candidate_conflicts`.
- Candidate belongs to a node with B4 `anchor_conflicts`.
- Target endpoint is already known.
- Multiple candidates target the same endpoint.

B5 must not:

- Resolve conflicts.
- Pick a preferred candidate.
- Merge candidate values.
- Calculate compromise values.
- Change `known_endpoint_z`.
- Change model fields.

Conflict data remains report-only and should be copied into blocked step reasons.

## 7. Locked Values Rule - Blocked / Report-Only

B5 must treat relevant lock conditions as blockers for proposal steps.

Blocked lock cases:

- Candidate source edge is locked.
- Candidate target edge is locked.
- Candidate target endpoint belongs to an edge with known locked elevation metadata.
- B4 reports any lock condition involving the candidate source or target edge.

B5 must not:

- Enforce locks by writing.
- Unlock anything.
- Route around locked values.
- Apply propagation through locked edges.
- Remove known endpoint values.

Lock data remains report-only and should be copied into blocked step reasons.

## 8. Expected Tests

Planned B5 tests should verify:

- B5 reads B4 result.
- B5 creates proposal steps from safe usable candidates.
- B5 creates blocked steps for conflict candidates.
- B5 creates blocked steps for locked candidates.
- B5 does not mutate model nodes.
- B5 does not mutate model edges.
- B5 does not write `Node.z`.
- B5 does not write `edge.start_z`.
- B5 does not write `edge.end_z`.
- B5 does not overwrite known endpoint values.
- B5 does not resolve conflicts.
- B5 does not calculate new elevation values.
- B5 proposal steps do not contain `target_z` or `proposed_z`.
- B5 preserves source/target metadata.

Tests that must not be part of B5:

- UI tests.
- Save/open persistence tests.
- Preview/apply tests.
- Physical fitting geometry tests.
- Catalog dimension tests.
- Slope calculation tests.
- Final propagation engine tests.
- Conflict resolution tests.
- Lock enforcement write tests.

## 9. Expected Code Files To Modify Or Create

Expected new code file:

- `modules/elevation_propagation_plan.py`

Expected new test file:

- `tests/test_elevation_propagation_plan.py`

Existing files allowed as import/read dependencies:

- `modules/elevation_anchor.py`
- `modules/elevation_wavefront.py`
- `modules/elevation_candidate.py`
- `modules/elevation_conflict_lock.py`

Files that should not be modified for B5:

- `Nevis_no_ui.py`
- `mainwindow.ui`
- `form.ui`
- save/open logic
- JWW export logic
- library/catalog JSON files
- Milestone C physical modeling files

## 10. B5 Completion Conditions

B5 is complete when:

- It reads B4 Conflict & Lock Framework output.
- It produces read-only propagation proposal steps.
- It blocks/report-only handles conflict-related candidates.
- It blocks/report-only handles lock-related candidates.
- It copies known endpoint values without overwriting them.
- It preserves source and target metadata.
- It does not mutate the model.
- It does not write `Node.z`.
- It does not write `edge.start_z`.
- It does not write `edge.end_z`.
- It does not resolve conflicts.
- It does not apply proposals.
- It does not calculate new elevation values.
- It has focused tests for safe proposals, conflict blockers, lock blockers, metadata preservation, non-mutation, and no new elevation fields.

B5 is not complete if it requires UI, save/open, preview/apply, conflict resolution, lock enforcement, actual propagation, or Milestone C physical modeling to pass.
