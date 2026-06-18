# Next Task

Date: 2026-06-17

## Current State

Elevation Foundation is complete.

Completed:

- Milestone A: PASS
- B1 - Anchor Discovery
- B2 - Wavefront Topology
- B3 - Candidate Evaluation
- B4 - Conflict & Lock Framework
- B5 - Propagation Proposal / Dry Run
- B6 - Proposal Review / Dry Run Report

Final test status:

```text
Ran 32 tests in 0.011s

OK
```

## First Task For Next Session

Read the handoff documents and confirm the Apply Engine scope before writing implementation code.

Recommended first action:

1. Read `docs/ELEVATION_FOUNDATION_COMPLETE.md`.
2. Read `docs/APPLY_ENGINE_ARCHITECTURE.md`.
3. Create an Apply Engine implementation plan or ask for approval to implement Apply Engine.

## Documents To Read

Required:

- `docs/PROJECT_STATUS.md`
- `docs/ELEVATION_FOUNDATION_COMPLETE.md`
- `docs/APPLY_ENGINE_ARCHITECTURE.md`
- `docs/ELEVATION_FOUNDATION_SUMMARY.md`

Useful context:

- `docs/MILESTONE_B_STATUS.md`
- `docs/B6_SCOPE_PLAN.md`
- `docs/ELEVATION_ARCHITECTURE.md`
- `docs/ELEVATION_SCOPE.md`

## Do Not Do Yet

Do not:

- Implement Apply Engine without explicit approval.
- Modify `Nevis_no_ui.py` without explicit approval.
- Add UI.
- Add save/open integration.
- Add preview/apply UI.
- Add Milestone C physical modeling.
- Resolve conflicts automatically.
- Bypass locked values.
- Write `Node.z`.
- Overwrite known endpoint values without an approved validation rule.

## Current Recommended Next Milestone

Apply Engine.

Goal:

- Safely apply reviewed `Proposed` rows from B6 to `edge.start_z` / `edge.end_z`.
- Add validation, undo snapshot, and rollback strategy.
- Keep UI/save/open integration out of the first implementation unless separately approved.
