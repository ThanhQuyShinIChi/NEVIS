# Elevation Foundation Complete

Date: 2026-06-17

## Completed Scope

The Elevation Foundation from B1 through B6 is complete under the approved narrow, read-only scope.

## B1 To B6 Summary

### B1 - Anchor Discovery

Completed:

- Discovers edge endpoint anchors from `edge.start_z` and `edge.end_z`.
- Resolves endpoint level IDs through `model.level_datums`.
- Discovers node anchors from `node.level_id`.
- Ignores `Node.z` as input.
- Does not mutate the model.

### B2 - Wavefront Topology

Completed:

- Reads B1 anchor output.
- Builds wavefront topology data.
- Builds candidate propagation paths.
- Does not calculate elevation values.
- Does not mutate the model.

### B3 - Candidate Evaluation

Completed:

- Reads B2 candidate paths.
- Produces evaluation result data.
- Classifies usable and blocked candidates.
- Reports conflict conditions only.
- Reports lock conditions only.
- Does not resolve conflicts.
- Does not mutate the model.

### B4 - Conflict & Lock Framework

Completed:

- Reads B1/B2/B3 data.
- Detects anchor conflicts at the same topological node.
- Copies candidate conflict reports.
- Detects lock-related conditions.
- Produces report-only conflict and lock result data.
- Does not resolve conflicts.
- Does not enforce locks.
- Does not mutate the model.

### B5 - Propagation Proposal / Dry Run

Completed:

- Reads B4 conflict and lock result.
- Creates read-only propagation proposal data.
- Blocks proposals affected by conflict.
- Blocks proposals affected by lock conditions.
- Skips known target endpoints.
- Does not apply proposals.
- Does not mutate the model.

### B6 - Proposal Review / Dry Run Report

Completed:

- Reads B5 proposal output.
- Creates review report data.
- Classifies rows as:
  - `Proposed`
  - `Blocked by Conflict`
  - `Blocked by Lock`
  - `Skipped (Known Target)`
- Produces summary counts.
- Does not apply proposals.
- Does not mutate the model.

## Modules

- `modules/elevation_anchor.py`
- `modules/elevation_wavefront.py`
- `modules/elevation_candidate.py`
- `modules/elevation_conflict_lock.py`
- `modules/elevation_proposal.py`
- `modules/elevation_review.py`

## Tests

- `tests/test_elevation_anchor_discovery.py`
- `tests/test_elevation_wavefront.py`
- `tests/test_elevation_candidate.py`
- `tests/test_elevation_conflict_lock.py`
- `tests/test_elevation_proposal.py`
- `tests/test_elevation_review.py`

## Final Test Command

```powershell
python -m unittest discover -s tests -p 'test_elevation*.py'
```

## Final Test Result

```text
Ran 32 tests in 0.011s

OK
```

Result: 32 tests OK.

## Not Done Yet

The following are intentionally not implemented:

- Apply
- UI
- Save/Open integration
- Preview integration
- Milestone C physical modeling
- Catalog dimension elevation logic
- Physical offset/invert modeling
- Hydraulic simulation

## Recommended Next Milestone

Recommended next milestone:

- Apply Engine

Alternative next milestone:

- Preview UI

Recommendation:

Build the Apply Engine first if the next goal is to safely commit reviewed proposal data to the model. Build Preview UI first if the next goal is user inspection before any write path exists.
