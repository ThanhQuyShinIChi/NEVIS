# B2 Scope Plan - Wavefront Topology Candidate Data

Date: 2026-06-17

## Decision Context

B1 is frozen as the current baseline with status `Nearly Complete`.

B2 is allowed to start, but only as a narrow topology-data step. B2 prepares intermediate data for future propagation; it does not perform propagation and does not calculate new elevation values.

## 1. What B2 Will Do

B2 will:

- Call `discover_elevation_anchors(model)`.
- Read only the result returned by `discover_elevation_anchors(model)`.
- Build wavefront topology data from B1 anchors.
- Identify candidate propagation paths in simple topology.
- Produce intermediate read-only data for future propagation stages.
- Preserve B1 source metadata so later stages can explain where a candidate came from.
- Treat `known_endpoint_z` as already assigned data that must not be changed.
- Skip topology that requires conflict resolution, fitting rules, or physical modeling.

B2 should answer one narrow question:

Given B1 anchors, which topology-adjacent endpoints are candidates for future propagation?

## 2. What B2 Must Not Do

B2 must not:

- Mutate the model.
- Write `Node.z`.
- Write `edge.start_z`.
- Write `edge.end_z`.
- Overwrite known values.
- Resolve conflicts.
- Perform actual propagation.
- Calculate new elevation values.
- Infer slope, invert, offset, insertion depth, or physical pipe geometry.
- Implement a propagation engine.
- Implement IN handling.
- Implement Y/LT/DT recognition, validation, or propagation.
- Implement 集合管 single-Z behavior.
- Add UI.
- Change save/open behavior.
- Add preview/apply behavior.
- Use catalog dimensions.
- Use physical offsets.
- Model B寸法.
- Model 差口M/L.
- Model 立て管有効長.
- Model multiple Z per port.
- Model physical invert elevation.
- Add hydraulic simulation.

## 3. Input From B1

B2 input is the existing B1 API result:

```python
discover_elevation_anchors(model)
```

Expected fields from B1:

- `known_endpoint_z`
  - Mapping of known edge endpoint keys to Z values.
  - Current B1 baseline contract: edge endpoint anchors only.

- `endpoint_anchors`
  - Metadata for edge endpoint anchors.
  - Includes edge index, endpoint name, node ID, Z, source, edge key, and level ID.

- `node_anchors`
  - Metadata for node-level anchors derived from `node.level_id`.
  - Current B1 baseline contract: node anchors remain separate from `known_endpoint_z`.

- `initial_frontier`
  - Frontier seed records created from endpoint anchors and node anchors.
  - B2 may read them as topology seeds only.

B2 may inspect model topology only as needed to connect anchor seeds to edge endpoints:

- `model.nodes`
- `model.edges`

B2 must not treat unresolved B1 data as a known value.

## 4. Output Of B2

B2 output should be a read-only result object or equivalent data structure containing intermediate topology/candidate data.

Expected output concepts:

- `b1_result`
  - The B1 discovery result or a read-only reference-safe copy.

- `wavefront_nodes`
  - Topology nodes touched by B1 anchors and eligible for candidate discovery.

- `candidate_paths`
  - Read-only candidate propagation paths.
  - These are proposals only, not applied elevation values.

- `skipped`
  - Read-only records describing why a topology location was not eligible.
  - Examples: degree >2, already known target, missing node, ambiguous topology.

- `warnings`
  - Non-blocking structural notes for later validation.
  - B2 warnings must not become conflict resolution.

B2 output must not contain newly calculated elevation values. If a candidate carries Z, it may only carry the same Z copied from its B1 source anchor as provenance data, not a newly computed result.

## 5. Definition Of Wavefront Topology Data

Wavefront topology data is a read-only description of where future propagation could begin and which topology neighbors are reachable from B1 anchor seeds.

It may include:

- anchor seed identity
- seed kind: edge endpoint anchor or node anchor
- seed node ID
- seed edge index if applicable
- seed endpoint if applicable
- adjacent edge indexes
- adjacent endpoint names
- node degree
- eligibility status
- skip reason when not eligible

It must not include:

- committed propagated values
- model mutations
- resolved conflicts
- physical dimensions
- UI state
- save/open data

Wavefront topology data is not the propagation engine. It is only the topology map that a future propagation engine may consume.

## 6. Definition Of Candidate Propagation Path

A candidate propagation path is a declarative record that says:

From this B1 anchor seed, this adjacent unknown endpoint appears topologically eligible for future propagation.

A candidate path should include:

- source kind
- source node ID
- source edge index if available
- source endpoint if available
- source Z copied from B1 if available
- target node ID
- target edge index
- target endpoint
- topology degree at the connection node
- reason the path is eligible
- source label from B1

A candidate propagation path must not:

- assign the target Z
- write to `known_endpoint_z`
- write to the model
- cross a degree >2 junction
- resolve two competing candidates
- calculate a slope-derived elevation
- apply fitting-specific rules

## 7. Expected Tests

Planned B2 tests should verify:

- B2 consumes `discover_elevation_anchors(model)` as its input.
- B2 produces deterministic output for the same model input.
- A B1 endpoint anchor creates wavefront topology data at its node.
- A B1 node anchor creates wavefront topology data without writing `Node.z`.
- A degree 0 node produces no candidate path.
- A degree 1 node can produce a local candidate path only when the adjacent endpoint is unknown.
- A degree 2 pass-through node can produce candidate path data only.
- A degree >2 node is skipped.
- Already-known endpoints are not overwritten or duplicated.
- Candidate paths copy B1 source metadata.
- B2 does not mutate model nodes.
- B2 does not mutate model edges.
- B2 does not write `edge.start_z`.
- B2 does not write `edge.end_z`.
- B2 does not calculate new elevation values.
- B2 does not perform multi-step propagation.
- B2 does not resolve conflicts.

Tests that must not be added for B2:

- UI tests.
- Save/open persistence tests.
- Preview/apply tests.
- Physical fitting geometry tests.
- Catalog dimension tests.
- Y/LT/DT fitting recognition tests.
- IN fitting tests.
- Full conflict/validation pipeline tests.

## 8. Expected Code Files To Modify Or Create

Expected new code file:

- `modules/elevation_b2_degree.py`

Expected new test file:

- `tests/test_elevation_b2_degree.py`

Existing file allowed as an import/read dependency:

- `modules/elevation_anchor.py`

Files that should not be modified for B2:

- `Nevis_no_ui.py`
- `mainwindow.ui`
- `form.ui`
- save/open logic
- JWW export logic
- library/catalog JSON files
- Milestone C physical modeling files

## 9. Architectural Risks

- B2 could accidentally become propagation.
  - Mitigation: output candidate paths only; never write target values.

- B2 could accidentally calculate elevation values.
  - Mitigation: candidate records may copy source Z for provenance only, never compute target Z.

- B2 could weaken source-of-truth rules.
  - Mitigation: preserve B1 `known_endpoint_z` as read-only and never overwrite it.

- B2 could blur node anchors and endpoint anchors.
  - Mitigation: keep B1 baseline contract explicit: node anchors are separate seeds, not known endpoint assignments.

- B2 could hide conflicts by picking one candidate.
  - Mitigation: do not resolve competing candidates; skip or report structural warning only.

- B2 could drift into B3 wavefront core.
  - Mitigation: B2 builds wavefront topology data; B3 performs actual wavefront propagation.

- B2 could drift into B7 lock precedence.
  - Mitigation: because B2 is non-mutating, it must not enforce or override locked values; it only avoids writes.

- B2 could force later API reshaping.
  - Mitigation: include enough source metadata and skip reasons in intermediate records.

## 10. B2 Completion Conditions

B2 is complete when:

- It consumes B1 output through `discover_elevation_anchors(model)`.
- It produces wavefront topology data.
- It produces candidate propagation paths.
- It keeps all output declarative and intermediate.
- It does not mutate the input model.
- It does not write `Node.z`.
- It does not write `edge.start_z`.
- It does not write `edge.end_z`.
- It does not overwrite known values.
- It does not resolve conflicts.
- It does not perform propagation.
- It does not calculate new elevation values.
- It has focused tests covering degree 0, degree 1, degree 2, degree >2, known target skipping, node anchors, endpoint anchors, and non-mutation.

B2 is not complete if it requires UI, save/open, preview/apply, physical modeling, fitting recognition, conflict resolution, or a propagation engine to pass its tests.
