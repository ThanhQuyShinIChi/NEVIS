# NEVIS 2.03 Implementation Review

Date: 2026-06-17

## Documents Read

- `docs/NEXT_TASK.md`
- `docs/ELEVATION_SCOPE.md`
- `docs/ELEVATION_ARCHITECTURE.md`
- `docs/ELEVATION_IMPLEMENTATION_PLAN.md`
- `docs/ELEVATION_DECISIONS.md`

## Current Status Summary

- Milestone A status: `PASS`.
- Documentation status: `PASS`.
- Current phase from `docs/NEXT_TASK.md`: `B1 - Anchor Discovery`.
- Stated next action: implement Anchor Discovery only.
- Explicit guardrails:
  - No propagation.
  - No UI.
  - No save/open changes.
  - Do not implement Milestone C physical concerns.

## Scope Interpretation

Milestone B is topology only.

Included in Milestone B:

- LevelDatum
- Node Elevation
- Pipe Elevation
- Propagation
- Y
- LT
- DT
- IN
- 集合管
- Validation
- Preview
- Apply

Excluded from Milestone B:

- Physical Offset
- Catalog Dimensions
- B寸法
- 差し口M/L
- 立て管有効長
- Multiple Z per Port
- Hydraulic Simulation
- Physical Invert Modeling

These excluded items belong to Milestone C unless explicitly approved.

## Architecture Rules To Preserve

- `Edge.start_z` and `Edge.end_z` are the source of truth.
- `Node.z` is derived/display only.
- `elevation_locked` always wins.
- Locked values must never be overwritten.
- Known endpoint values must not be overwritten; conflicts should be reported instead.
- The propagation model is: Anchor -> Frontier -> Known Set -> Propagation -> Conflict -> Validation.
- Fail loud: conflict is preferred over automatic guessing.
- Do not infer building structure such as stack middle, stack end, or final manifold.

## Confirmed Active Milestone

The active milestone is Milestone B, phase B1: Anchor Discovery.

The permitted implementation unit is Anchor Discovery only.

## Repository Observation

Although `docs/NEXT_TASK.md` says B1 implementation is not started, the repository already contains:

- `modules/elevation_anchor.py`
- `tests/test_elevation_anchor_discovery.py`

These files appear to implement and test an Anchor Discovery pass that:

- Does not mutate the model.
- Treats edge endpoint Z values as anchors.
- Resolves edge level IDs through `model.level_datums`.
- Creates node anchors from `Node.level_id`.
- Intentionally ignores `Node.z` as an input source.

This means the next work should first verify whether the existing implementation is accepted as B1, needs adjustment, or should be replaced.

## Code Files Likely To Be Modified After Approval

For B1 Anchor Discovery only:

- `modules/elevation_anchor.py`
- `tests/test_elevation_anchor_discovery.py`

Potential integration touchpoints, only if approval expands B1 integration:

- `Nevis_no_ui.py`
- `modules/graph.py`

Files that should not be modified for B1 based on the current guardrails:

- UI files such as `mainwindow.ui` and `form.ui`
- save/open persistence code in `Nevis_no_ui.py`
- library/catalog JSON files
- JWW export files
- propagation, validation, preview, and apply logic beyond anchor discovery

## Recommended Next Step

Before any code change, confirm one of these directions:

1. Treat the existing `modules/elevation_anchor.py` and tests as the B1 baseline, then run/verify tests and make only minimal corrections if needed.
2. Rework B1 to a different contract if the current anchor result shape is not what the Milestone B engine should consume.
3. Defer code changes and update documentation first to reflect the existing B1 implementation.

No implementation code has been changed in this review step.
