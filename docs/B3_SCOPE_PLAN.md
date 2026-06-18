# B3 Scope Plan - Candidate Evaluation Report

Date: 2026-06-17

## Decision Context

B2 is temporarily complete.

B3 may start as a planning and evaluation layer over B2 candidate propagation paths. B3 does not propagate, does not calculate new elevation values, and does not write to the model.

## 1. What B3 Will Do

B3 will:

- Read B2 output from `build_elevation_wavefront(model)`.
- Evaluate B2 `candidate_paths`.
- Classify candidate paths for future propagation readiness.
- Identify which candidate data future propagation may consume.
- Report candidate blockers.
- Report potential conflicts without resolving them.
- Report lock-related concerns without enforcing or overriding them.
- Preserve B1 and B2 source metadata for traceability.

B3 should answer this narrow question:

Which B2 candidate paths are structurally usable for a future propagation step, and which should be blocked or reported before propagation exists?

## 2. What B3 Must Not Do

B3 must not:

- Mutate the model.
- Write `Node.z`.
- Write `edge.start_z`.
- Write `edge.end_z`.
- Overwrite known values.
- Create or run a propagation engine.
- Perform actual propagation.
- Calculate new elevation values.
- Resolve conflicts.
- Enforce locks by writing or changing data.
- Add UI.
- Change save/open behavior.
- Add preview/apply behavior.
- Implement IN handling.
- Implement Y/LT/DT recognition, validation, or propagation.
- Implement 集合管 single-Z behavior.
- Use catalog dimensions.
- Use physical offsets.
- Model B寸法.
- Model 差口M/L.
- Model 立て管有効長.
- Model multiple Z per port.
- Model physical invert elevation.
- Add hydraulic simulation.

## 3. Input From B2

B3 input is the B2 result from:

```python
build_elevation_wavefront(model)
```

Expected B2 fields:

- `b1_result`
  - Original B1 anchor discovery result.

- `known_endpoint_z`
  - Copy of B1 known endpoint values.
  - Must remain read-only.

- `wavefront_nodes`
  - Topology nodes touched by B1 anchors.

- `candidate_paths`
  - Declarative candidate paths from B2.
  - These are not propagated values.

- `skipped`
  - B2 skip records such as degree >2, already-known target, or missing topology.

B3 may inspect model metadata only for reporting lock status and structural context. It must not write anything back.

## 4. Output Of B3

B3 output should be a read-only evaluation report.

Expected output concepts:

- `b2_result`
  - The B2 result or a reference-safe copy.

- `usable_candidates`
  - Candidate paths that are structurally suitable for future propagation.
  - These are still not applied.

- `blocked_candidates`
  - Candidate paths blocked by known-value, topology, lock, or ambiguity concerns.

- `conflict_reports`
  - Report-only records of possible conflicts.
  - No conflict is resolved in B3.

- `lock_reports`
  - Report-only records of locked edges/endpoints relevant to candidate paths.
  - No lock behavior is enforced in B3.

- `evaluation_notes`
  - General non-mutating notes for future B4+ work.

B3 output must not include newly computed target elevations.

## 5. Candidate Evaluation Rules

B3 candidate evaluation should be conservative.

A candidate may be marked usable when:

- It comes from B2 `candidate_paths`.
- Its target endpoint is not present in `known_endpoint_z`.
- It has source metadata from B1/B2.
- It has a target edge index and endpoint.
- It does not require crossing a degree >2 node.
- It does not require fitting-specific behavior.
- It does not require physical dimensions.
- It does not require conflict resolution.
- It does not require calculating a new elevation.

A candidate should be blocked or reported when:

- The target endpoint is already known.
- The candidate lacks source metadata.
- The candidate lacks target endpoint identity.
- Multiple candidates target the same endpoint.
- The target edge or endpoint is malformed.
- The candidate would require branching logic.
- The candidate would require IN, Y/LT/DT, or 集合管 rules.
- The candidate touches locked elevation metadata and future propagation would need a lock decision.

B3 must not choose a winner among competing candidates.

## 6. Conflict Handling Strategy - Report Only

B3 conflict handling is report-only.

B3 may report:

- Multiple candidates targeting the same endpoint.
- Candidate target already present in `known_endpoint_z`.
- Candidate source Z differs from another candidate source Z for the same target.
- Candidate requires a branch or fitting rule not available in B3.

B3 must not:

- Resolve conflicts.
- Pick a preferred candidate.
- Change `known_endpoint_z`.
- Change model values.
- Calculate a compromise or derived elevation.

Conflict reports should preserve:

- target edge index
- target endpoint
- candidate sources
- source Z values copied from B1/B2 if present
- reason

## 7. Lock Handling Strategy - Report Only

B3 lock handling is report-only.

B3 may inspect whether an edge related to a candidate has `elevation_locked`.

B3 may report:

- candidate target edge is locked
- candidate source edge is locked
- future propagation would need B7 lock-precedence handling

B3 must not:

- Enforce lock precedence.
- Unlock anything.
- Write through a lock.
- Drop known values because of a lock.
- Apply propagation around a lock.

Lock reports should be treated as future B7 input, not as B3 decisions.

## 8. Expected Tests

Planned B3 tests should verify:

- B3 consumes B2 output.
- B3 classifies a simple B2 candidate as usable.
- B3 does not mutate model nodes.
- B3 does not mutate model edges.
- B3 does not write `Node.z`.
- B3 does not write `edge.start_z`.
- B3 does not write `edge.end_z`.
- B3 does not overwrite `known_endpoint_z`.
- B3 does not calculate new elevation values.
- B3 reports duplicate target candidates without resolving them.
- B3 reports already-known target candidates if present.
- B3 reports lock-related candidate context without enforcing locks.
- B3 preserves source and target metadata.

Tests that must not be part of B3:

- UI tests.
- Save/open persistence tests.
- Preview/apply tests.
- Physical fitting geometry tests.
- Catalog dimension tests.
- IN fitting tests.
- Y/LT/DT fitting recognition or propagation tests.
- Full propagation engine tests.

## 9. Expected Code Files To Modify Or Create

Expected new code file:

- `modules/elevation_candidate_evaluation.py`

Expected new test file:

- `tests/test_elevation_candidate_evaluation.py`

Existing files allowed as import/read dependencies:

- `modules/elevation_anchor.py`
- `modules/elevation_wavefront.py`

Files that should not be modified for B3:

- `Nevis_no_ui.py`
- `mainwindow.ui`
- `form.ui`
- save/open logic
- JWW export logic
- library/catalog JSON files
- Milestone C physical modeling files

## 10. B3 Completion Conditions

B3 is complete when:

- It reads B2 candidate propagation paths.
- It evaluates candidates conservatively.
- It reports usable candidates.
- It reports blocked candidates.
- It reports possible conflicts without resolving them.
- It reports lock context without enforcing locks.
- It preserves B1/B2 source metadata.
- It does not mutate the model.
- It does not write `Node.z`.
- It does not write `edge.start_z`.
- It does not write `edge.end_z`.
- It does not overwrite known values.
- It does not calculate new elevation values.
- It does not create or run a propagation engine.
- It has focused tests for usable candidates, duplicate/known-target reports, lock reports, metadata preservation, and non-mutation.

B3 is not complete if it requires UI, save/open, preview/apply, physical modeling, fitting recognition, conflict resolution, or actual propagation to pass.
