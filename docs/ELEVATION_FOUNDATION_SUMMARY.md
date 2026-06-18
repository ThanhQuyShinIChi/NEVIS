# Elevation Foundation Summary

Date: 2026-06-17

## Purpose

This document summarizes the current Elevation Foundation so a reviewer can understand the implemented and planned architecture from one place.

## 1. Files Created From Milestone A To Current State

### Documentation

- `IMPLEMENTATION_REVIEW.md`
- `docs/B1_STATUS_REVIEW.md`
- `docs/B1_COMPLETION_DECISION.md`
- `docs/B2_SCOPE_PLAN.md`
- `docs/B3_SCOPE_PLAN.md`
- `docs/MILESTONE_B_STATUS.md`
- `docs/B4_ARCHITECTURE_DECISION.md`
- `docs/ELEVATION_FOUNDATION_SUMMARY.md`

### Code

- `modules/elevation_anchor.py`
- `modules/elevation_wavefront.py`
- `modules/elevation_candidate.py`

### Tests

- `tests/test_elevation_anchor_discovery.py`
- `tests/test_elevation_wavefront.py`
- `tests/test_elevation_candidate.py`

## 2. Short Description Of Each File

### `IMPLEMENTATION_REVIEW.md`

Initial review of the elevation documents and current repository state before implementation work continued.

### `docs/B1_STATUS_REVIEW.md`

Classifies B1 Anchor Discovery as `Nearly complete`, documents what exists, what is missing, test status, and scope compliance.

### `docs/B1_COMPLETION_DECISION.md`

Decides that B1 remains `Nearly complete` and can be frozen as the baseline while B2 starts under a narrow scope.

### `docs/B2_SCOPE_PLAN.md`

Defines B2 as read-only wavefront topology data and candidate propagation path construction. Explicitly excludes mutation, propagation, elevation calculation, UI, save/open, preview/apply, and Milestone C physical modeling.

### `docs/B3_SCOPE_PLAN.md`

Defines B3 as candidate evaluation report data. Conflict handling and lock handling are report-only.

### `docs/MILESTONE_B_STATUS.md`

Summarizes the current Milestone B status: B1, B2, and B3 are present under narrow scopes; propagation, apply, UI, save/open integration, conflict resolution, and lock enforcement do not exist yet.

### `docs/B4_ARCHITECTURE_DECISION.md`

Recommends B4 as `Conflict & Lock Framework` before propagation planning, because propagation should not run before conflict and lock safety rules are explicit.

### `docs/ELEVATION_FOUNDATION_SUMMARY.md`

This document.

### `modules/elevation_anchor.py`

B1 module. Discovers elevation anchors from edge endpoint metadata and node level metadata without mutating the model.

### `modules/elevation_wavefront.py`

B2 module. Builds read-only wavefront topology data and candidate propagation paths from B1 anchors.

### `modules/elevation_candidate.py`

B3 module. Evaluates B2 candidate paths, produces usable/blocked candidate lists, and reports conflicts/locks without resolving or enforcing them.

### `tests/test_elevation_anchor_discovery.py`

B1 tests for anchor discovery behavior.

### `tests/test_elevation_wavefront.py`

B2 tests for wavefront and candidate path construction.

### `tests/test_elevation_candidate.py`

B3 tests for candidate evaluation, report-only conflict/lock behavior, non-mutation, and no new elevation values.

## 3. Public API By Module

### `modules/elevation_anchor.py`

Primary public function:

- `discover_elevation_anchors(model) -> AnchorDiscoveryResult`

Public data structures:

- `EndpointAnchor`
- `NodeAnchor`
- `FrontierItem`
- `AnchorDiscoveryResult`
- `EndpointKey`

Important result fields:

- `known_endpoint_z`
- `endpoint_anchors`
- `node_anchors`
- `initial_frontier`

Notes:

- `Edge.start_z` and `Edge.end_z` are treated as source-of-truth endpoint anchors.
- `Node.z` is intentionally ignored as input.
- `node.level_id` may create a node anchor through `model.level_datums`.
- The function does not mutate the model.

### `modules/elevation_wavefront.py`

Primary public function:

- `build_elevation_wavefront(model) -> ElevationWavefrontResult`

Public data structures:

- `TopologyEndpoint`
- `WavefrontNode`
- `CandidatePropagationPath`
- `SkippedWavefrontItem`
- `ElevationWavefrontResult`
- `EndpointKey`

Important result fields:

- `b1_result`
- `known_endpoint_z`
- `wavefront_nodes`
- `candidate_paths`
- `skipped`

Notes:

- Reads B1 through `discover_elevation_anchors(model)`.
- Builds topology/candidate data only.
- Does not calculate target elevations.
- Does not mutate the model.

### `modules/elevation_candidate.py`

Primary public function:

- `evaluate_elevation_candidates(model) -> CandidateEvaluationResult`

Public data structures:

- `CandidateIssue`
- `ConflictReport`
- `LockReport`
- `CandidateEvaluationResult`
- `EndpointKey`

Important result fields:

- `b2_result`
- `known_endpoint_z`
- `usable_candidates`
- `blocked_candidates`
- `conflict_reports`
- `lock_reports`

Notes:

- Reads B2 through `build_elevation_wavefront(model)`.
- Evaluates candidate paths.
- Conflict handling is report-only.
- Lock handling is report-only.
- Does not propagate, calculate new elevation values, resolve conflicts, enforce locks, or mutate the model.

## 4. Relationship Between Anchor, Wavefront, Candidate, Evaluation

Current flow:

```text
Anchor
-> Wavefront
-> Candidate
-> Evaluation
```

### Anchor

Anchor is B1. It identifies known elevation seeds:

- edge endpoint anchors from `edge.start_z` and `edge.end_z`
- edge endpoint anchors from endpoint level IDs resolved through `level_datums`
- node anchors from `node.level_id`

Output:

- known endpoint values
- endpoint anchor metadata
- node anchor metadata
- initial frontier seed data

### Wavefront

Wavefront is B2. It uses anchor seed data to inspect topology around anchors.

Output:

- wavefront nodes
- candidate propagation paths
- skipped topology records

Wavefront does not assign or calculate elevation.

### Candidate

Candidate path data is produced by B2. It describes possible future propagation edges:

- source anchor/seed
- target endpoint
- topology degree
- copied source metadata

Candidate paths are proposals only.

### Evaluation

Evaluation is B3. It consumes candidate paths and classifies them:

- usable candidates
- blocked candidates
- conflict reports
- lock reports

Evaluation does not resolve conflicts, enforce locks, or write model data.

## 5. Existing Tests

### B1 Tests

File:

- `tests/test_elevation_anchor_discovery.py`

Tests:

- `test_edge_explicit_start_end_z_become_known_endpoints`
- `test_edge_level_ids_resolve_to_level_datum_elevation`
- `test_node_level_id_becomes_node_anchor_without_using_node_z`
- `test_empty_elevation_model_has_no_known_or_frontier`
- `test_discovery_does_not_mutate_model`

### B2 Tests

File:

- `tests/test_elevation_wavefront.py`

Tests:

- `test_reads_anchor_result_from_b1`
- `test_known_endpoint_anchor_creates_wavefront_candidate_path`
- `test_wavefront_does_not_mutate_model`
- `test_wavefront_does_not_create_new_elevation_values`
- `test_wavefront_does_not_overwrite_known_endpoint_values`

### B3 Tests

File:

- `tests/test_elevation_candidate.py`

Tests:

- `test_reads_b2_data_and_creates_evaluation_result`
- `test_b3_consumes_b2_output`
- `test_conflict_is_report_only_without_mutation`
- `test_lock_is_report_only_without_mutation`
- `test_does_not_mutate_model_or_create_elevation_values`
- `test_does_not_overwrite_known_endpoint_values`

### Current Combined Test Command

```powershell
python -m unittest tests.test_elevation_anchor_discovery tests.test_elevation_wavefront tests.test_elevation_candidate
```

Last known result:

```text
Ran 16 tests

OK
```

## 6. Existing Logic Coverage

Covered behavior:

- Explicit `edge.start_z` and `edge.end_z` become known endpoint anchors.
- Endpoint level IDs resolve through `model.level_datums`.
- Node level IDs create node anchors.
- `Node.z` is ignored for anchor discovery.
- Empty elevation metadata produces no anchors/frontier.
- B1 does not mutate the model.
- B2 reads B1 output.
- B2 creates wavefront items and candidate paths.
- B2 does not mutate the model.
- B2 does not create new elevation values.
- B2 does not overwrite known endpoint values.
- B3 reads B2 output.
- B3 creates evaluation result data.
- B3 reports duplicate-target conflict conditions without resolving them.
- B3 reports lock context without enforcing locks.
- B3 does not mutate the model.
- B3 does not create new elevation values.
- B3 does not overwrite known endpoint values.

Covered architecture constraints:

- Read-only foundation through B3.
- No `Node.z` writes.
- No `edge.start_z` or `edge.end_z` writes.
- No propagation.
- No apply.
- No UI.
- No save/open integration.
- No Milestone C physical modeling.

## 7. Missing Logic Coverage

Missing or incomplete test coverage:

- Explicit precedence test when both endpoint Z and endpoint level ID exist.
- Unknown or missing level ID diagnostics.
- Malformed/non-numeric Z behavior.
- Numeric string Z behavior.
- Multiple model shapes using real `Nevis_no_ui.py` classes.
- Degree 0/1/2/>2 topology cases beyond the current focused B2 paths.
- More detailed skipped topology reasons.
- Source metadata edge cases.
- Candidate paths with missing/malformed target identity.
- Already-known target candidates at B3 using direct B2 fixtures.
- Lock reports for only-source-locked and only-target-locked cases separately.
- Conflict reports with different source Z values are currently report-only but not deeply categorized.
- Ordering/determinism coverage for larger graphs.

Missing architecture coverage:

- Formal Conflict & Lock Framework acceptance tests.
- Propagation planning tests.
- Dry-run proposed value tests.
- Apply tests.
- UI/preview tests.
- Save/Open integration tests.

## 8. Completely Not Existing Yet

The following do not exist yet:

- Propagation engine.
- Propagation planning module.
- Dry-run propagation result module.
- Conflict resolution.
- Lock enforcement.
- Apply logic.
- UI integration for elevation foundation.
- Preview integration.
- Save/Open integration for new foundation result data.
- Validation pipeline.
- Engine API.
- IN handler.
- Y/LT/DT recognition.
- Y/LT/DT validation.
- Y/LT/DT propagation.
- 集合管 single-Z handling.
- Milestone C physical modeling.
- Catalog dimension elevation logic.
- Physical offset/invert modeling.
- Multiple Z per port.
- Hydraulic simulation.

## Review Summary

The current Elevation Foundation is a read-only pipeline:

```text
B1 Anchor Discovery
-> B2 Wavefront Topology / Candidate Paths
-> B3 Candidate Evaluation Reports
```

It is intentionally not an elevation propagation system yet.

The recommended next architecture step remains B4: Conflict & Lock Framework.
