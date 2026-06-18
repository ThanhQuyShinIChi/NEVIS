# B4 Architecture Decision

Date: 2026-06-17

## Decision Question

B4 should be chosen as one of:

- A. Propagation Planning
- B. Conflict & Lock Framework

This document decides the safer architecture order before any B4 implementation.

## 1. Dependency Analysis

### Anchor

Anchor discovery is the root input.

Current module:

- `modules/elevation_anchor.py`

Current responsibility:

- Discover known edge endpoint elevations.
- Discover node-level anchor seeds.
- Preserve source metadata.
- Avoid mutation.

Dependency role:

- Everything downstream depends on anchor data being stable.

### Wavefront

Wavefront data maps anchor seeds to reachable topology.

Current module:

- `modules/elevation_wavefront.py`

Current responsibility:

- Read B1 anchor output.
- Build wavefront topology data.
- Build candidate propagation paths.
- Avoid propagation and mutation.

Dependency role:

- Candidate and evaluation stages depend on wavefront paths.

### Candidate

Candidate paths describe possible future propagation targets.

Current source:

- `modules/elevation_wavefront.py`

Current responsibility:

- Describe possible source-to-target paths.
- Preserve metadata.
- Avoid assigning target elevation.

Dependency role:

- Propagation cannot safely run without candidate paths.

### Evaluation

Evaluation classifies candidate paths.

Current module:

- `modules/elevation_candidate.py`

Current responsibility:

- Identify usable candidates.
- Report blocked candidates.
- Report conflicts only.
- Report locks only.
- Avoid resolving or enforcing anything.

Dependency role:

- Propagation should consume evaluated candidates, not raw candidates.

### Conflict

Conflict handling is currently report-only.

Current state:

- Possible conflicts can be detected and reported.
- No conflict resolution policy exists.
- No winner is selected among competing candidates.

Dependency role:

- Propagation depends on a clear conflict framework.
- Without it, propagation may accidentally choose values, overwrite known data, or hide ambiguity.

### Lock

Lock handling is currently report-only.

Current state:

- Lock-related context can be reported.
- No lock enforcement exists.
- `elevation_locked always wins` is an architecture rule, but not yet an executable framework.

Dependency role:

- Propagation depends on lock rules before it can assign or propose committed values.
- Apply depends on lock enforcement even more strongly.

### Propagation

Propagation does not exist yet.

Future responsibility:

- Consume evaluated candidates.
- Produce proposed propagated endpoint values.
- Respect known values.
- Respect conflicts.
- Respect locks.
- Avoid physical modeling unless Milestone C is approved.

Dependency role:

- Propagation is downstream of Anchor, Wavefront, Candidate, Evaluation, Conflict, and Lock.

## 2. Risks If Propagation Is Implemented First

Implementing propagation before conflict/lock framework creates these risks:

- Propagation may overwrite known endpoint values.
- Propagation may implicitly resolve conflicts by traversal order.
- Propagation may ignore locked edges because lock enforcement is not defined.
- Propagation may create target elevation values without a safe blocking policy.
- Propagation may convert report-only warnings into silent behavior.
- Propagation may make later conflict handling harder because bad assumptions become embedded in engine behavior.
- Propagation tests may pass only for simple paths and fail later at junctions, duplicate candidates, or locked data.
- Propagation may blur the boundary between planning, validation, and apply.
- Propagation could accidentally become an apply step if it writes to model fields.

The core architectural risk:

Propagation changes the meaning of data from `candidate` to `proposed value`. That transition should not happen until conflict and lock behavior are explicit.

## 3. Benefits If Conflict/Lock Is Implemented First

Implementing a Conflict & Lock Framework before propagation provides:

- A clear blocking policy before values are generated.
- A stable contract for propagation to consume.
- Protection against overwriting `known_endpoint_z`.
- Explicit handling of duplicate candidates for the same target.
- Explicit handling of already-known target endpoints.
- Explicit report of locked source and target edges.
- Separation between:
  - detection
  - reporting
  - resolution
  - enforcement
  - propagation
  - apply
- Better tests for future propagation edge cases.
- Lower risk that propagation will accidentally become conflict resolution or apply.

The main benefit:

B4 can define the safety rails that propagation must obey later.

## 4. Proposed Implementation Order

### B4 - Conflict & Lock Framework

Recommended B4 scope:

- Convert current report-only conflict and lock behavior into a formal framework.
- Define conflict categories.
- Define lock report categories.
- Define blocking decisions for future propagation.
- Keep all behavior read-only.
- Do not resolve conflicts.
- Do not enforce locks by writing.
- Do not propagate.
- Do not mutate model data.

Expected output:

- A structured safety report that says which candidates are allowed, blocked, conflict-prone, or lock-sensitive for future propagation.

### B5 - Propagation Planning

Recommended B5 scope:

- Use B4 framework output.
- Plan propagation steps from allowed candidates only.
- Produce proposed propagation plan data.
- Do not apply to model yet.
- Do not write `Node.z`.
- Do not write `edge.start_z` or `edge.end_z`.

Expected output:

- A read-only propagation plan.
- No model mutation.

### B6 - Propagation Proposal / Dry Run

Recommended B6 scope:

- Convert B5 plan into proposed endpoint values in memory only.
- Respect conflict blocks.
- Respect lock blocks.
- Preserve known values.
- Still do not apply to model.
- Still no UI/save/open/apply.

Expected output:

- Dry-run propagation result.
- Proposed values separate from the model.

Apply should remain after propagation planning and dry-run behavior are stable.

## 5. Final Recommendation

Recommendation: choose B. Conflict & Lock Framework for B4.

Reason:

- Current B1-B3 pipeline already produces candidate and evaluation data.
- The next unsafe transition is propagation.
- Before propagation exists, the project needs formal safety rules for conflicts and locks.
- Conflict and lock behavior currently exists only as report-only metadata.
- Turning that into a formal framework first reduces the chance that propagation will overwrite, guess, or silently resolve ambiguous data.

B4 should not implement propagation.

B4 should define the framework that future propagation must obey.
