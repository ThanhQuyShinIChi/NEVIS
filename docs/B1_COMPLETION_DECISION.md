# B1 Completion Decision

Date: 2026-06-17

## Purpose

This document classifies the remaining B1 Anchor Discovery gaps before deciding whether to move to B2 Degree <=2 Handler.

Source documents:

- `docs/B1_STATUS_REVIEW.md`
- `docs/ELEVATION_ARCHITECTURE.md`
- `docs/ELEVATION_SCOPE.md`
- `docs/ELEVATION_IMPLEMENTATION_PLAN.md`

## Classification Of Remaining Items

### Required Before B2

These items should be resolved before B2 starts because B2 will consume B1 output directly.

- Document the B1 output contract for node anchors versus `known_endpoint_z`.
  - Reason: B2 needs to know whether node-level anchors are immediate known endpoint values, frontier seeds only, or separate topology hints.
  - Without this, B2 may duplicate anchor resolution or make incompatible assumptions.

- Add/confirm tests for explicit Z precedence over level-derived Z when both exist.
  - Reason: architecture defines `Edge.start_z` and `Edge.end_z` as source of truth.
  - This should be proven before B2 starts using B1 anchors as input.

- Add/confirm behavior for missing or unknown `level_id`.
  - Reason: B2 must safely walk degree <=2 chains even when some anchors are absent.
  - The expected B1 behavior should be stable: skip unresolved anchors, report diagnostics, or both.

### Optional Hardening

These items improve quality and debugging but do not block B2 if the B2 implementation treats B1 anchors conservatively.

- Add an explicit diagnostic list for invalid level IDs, malformed node/edge IDs, or malformed elevation values.
  - Useful for later validation and UI reporting.
  - Not strictly required for B2 if unresolved values simply do not become anchors.

- Add tests for string numeric values such as `"100.0"`.
  - Current implementation appears to support this through tolerant float parsing.
  - Test coverage would lock the behavior.

- Add tests for malformed/non-numeric Z values.
  - Current implementation appears to ignore malformed values.
  - Test coverage would make the behavior explicit.

- Add integration test against the real `Nevis_no_ui.py` model classes.
  - Useful because current tests use dummy model classes.
  - Not mandatory if B2 remains module-level and does not integrate with UI/save/open.

- Carry `elevation_locked` state into anchor metadata.
  - Useful for later lock-aware stages.
  - Not blocking for B2 as long as B2 does not overwrite model data and does not attempt final conflict resolution.

### Can Defer To Later Milestone Or Later Milestone B Step

These items are important, but they naturally belong after B1 or in later Milestone B stages.

- Full conflict reporting between node-level anchors and edge endpoint anchors at the same topological node.
  - Architecture requires conflict over guessing, but the propagation model places conflict after propagation.
  - B1 may remain discovery-only if it does not overwrite or infer.
  - Minimal B1 conflict awareness can be optional hardening; full conflict pipeline belongs closer to B3/B8.

- Tests for multiple edges sharing the same node and producing conflicting anchors.
  - Best handled with the conflict model in B3/B8 unless B2 is designed to surface conflicts.

- Full lock precedence enforcement.
  - B7 is explicitly named `Lock Precedence` in the implementation plan.
  - B1 should not violate lock rules, but complete lock behavior can defer to B7.

- UI, preview, apply, save/open, catalog, physical offset, catalog dimensions, invert modeling, multiple Z per port, and hydraulic concerns.
  - These are outside B1.
  - Several are outside Milestone B entirely and belong to Milestone C.

## Proposed Final Status

Recommended decision: Keep B1 Nearly Complete.

Reason:

- Existing B1 is a real implementation with passing tests.
- It is scope-compliant and does not mutate model data.
- However, the B1-to-B2 contract is not explicit enough yet.
- The most important missing piece is architectural clarity: how B2 should consume node anchors, endpoint anchors, known endpoint values, and unresolved level metadata.

Alternative decision:

- Declare B1 Complete only if the team accepts the current output contract as-is:
  - `known_endpoint_z` contains only edge endpoint anchors.
  - `node_anchors` are separate frontier seeds.
  - unresolved or malformed metadata is silently ignored.
  - conflict detection is deferred to later propagation/validation stages.

## Risks If Moving To B2 Immediately

- B2 may interpret node anchors inconsistently.
  - Example: one implementation may treat `node.level_id` as applying to all connected endpoints, while another may treat it only as a frontier hint.

- B2 may accidentally introduce propagation behavior too early.
  - Degree <=2 handling can easily drift from local chain handling into wavefront propagation, which belongs to B3.

- Missing/unknown levels may be handled ad hoc.
  - If B1 has no formal diagnostics contract, B2 may silently skip data in a way that is hard to debug later.

- Source-of-truth precedence may become implicit instead of guaranteed.
  - If explicit `start_z/end_z` versus level-derived values is not tested, future edits could accidentally weaken the architecture rule.

- Conflict handling may be postponed without a clear boundary.
  - This is acceptable only if B2 remains discovery/handler logic and does not assign final known values over existing ones.

- Lock precedence may be forgotten until B7.
  - This is acceptable only if B2 remains non-mutating and never overwrites locked values.

- Later UI/preview/apply stages may need API reshaping.
  - If B1 result objects do not eventually carry diagnostics or enough source metadata, B9/B10/B11 may require breaking changes.

## Decision Summary

B1 should remain `Nearly complete` until the B1 output contract is explicitly accepted or documented.

The project may move to B2 immediately only under a narrow rule:

- B2 must consume the existing B1 result conservatively.
- B2 must not mutate the model.
- B2 must not perform general propagation.
- B2 must not overwrite known endpoint values.
- B2 must not implement UI, save/open, preview, apply, or Milestone C physical modeling.
