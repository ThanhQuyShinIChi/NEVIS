# B1 Status Review - Anchor Discovery

Date: 2026-06-17

## Files Reviewed

- `modules/elevation_anchor.py`
- `tests/test_elevation_anchor_discovery.py`
- `docs/ELEVATION_SCOPE.md`

## Classification

Nearly complete

Reason: B1 is more than a skeleton and already contains a working anchor discovery implementation with focused tests. It is not classified as complete yet because the current implementation lacks explicit diagnostics/conflict reporting, lock-related metadata, and broader edge-case coverage that would make the B1 contract robust before later Milestone B steps consume it.

## What Already Exists

`modules/elevation_anchor.py` already provides:

- Data structures for anchor discovery output:
  - `EndpointAnchor`
  - `NodeAnchor`
  - `FrontierItem`
  - `AnchorDiscoveryResult`
- `discover_elevation_anchors(model)` as the main B1 API.
- Edge endpoint anchor discovery from:
  - `edge.start_z`
  - `edge.end_z`
  - `edge.start_level_id` resolved through `model.level_datums`
  - `edge.end_level_id` resolved through `model.level_datums`
- Node anchor discovery from `node.level_id` resolved through `model.level_datums`.
- Explicit avoidance of `Node.z` as an input source.
- Non-mutating behavior: discovery returns result objects and does not write back into the model.
- Initial frontier construction for later Milestone B wavefront work.
- Basic tolerant numeric parsing through `_optional_float`.

`tests/test_elevation_anchor_discovery.py` already covers:

- Explicit `start_z` and `end_z` become known endpoint anchors.
- Edge level IDs resolve to level datum elevations.
- Node `level_id` becomes a node anchor while ignoring `Node.z`.
- Empty elevation metadata produces no anchors/frontier.
- Discovery does not mutate the model.

## What Is Missing

For B1 to be considered complete and stable as a foundation for B2/B3:

- No explicit diagnostic list for invalid level IDs, malformed node/edge IDs, or malformed elevation values.
- No conflict reporting if node-level anchors and edge endpoint anchors imply different Z values at the same topological node.
- No representation of `elevation_locked` in anchor metadata, even though lock precedence is a global architecture rule.
- No tests for explicit Z precedence over level-derived Z when both exist.
- No tests for missing/unknown `level_id`.
- No tests for string numeric values such as `"100.0"`.
- No tests for malformed/non-numeric Z values.
- No tests for multiple edges sharing the same node and producing conflicting anchors.
- No integration test against the real `Nevis_no_ui.py` model classes.
- No documented formal contract for whether node anchors should enter `known_endpoint_z` immediately or remain separate until a later propagation step.

## Test Result

Command run:

```powershell
python -m unittest tests.test_elevation_anchor_discovery
```

Result:

```text
Ran 5 tests in 0.001s

OK
```

Current B1-specific test status:

- Pass: 5
- Fail: 0

## Scope Compliance

The current implementation is mostly compliant with `docs/ELEVATION_SCOPE.md`.

Compliant points:

- Stays within topology/elevation metadata.
- Uses LevelDatum.
- Uses pipe endpoint elevation metadata.
- Uses node level metadata without treating `Node.z` as a source of truth.
- Does not implement physical offsets.
- Does not use catalog dimensions.
- Does not model B寸法.
- Does not model 差口M/L.
- Does not model 立て管有効長.
- Does not model multiple Z per port.
- Does not implement hydraulic simulation.
- Does not implement physical invert modeling.
- Does not add UI, save/open, preview, apply, or propagation behavior.

Potential scope/architecture gap:

- The architecture says `elevation_locked` always wins. B1 does not overwrite anything, so it does not violate this rule, but it also does not carry lock state into anchor metadata for later stages.
- The architecture says conflicts should be detected rather than guessed. B1 currently discovers anchors but does not report conflicts between anchors.

## Review Conclusion

The current B1 implementation is a real partial-to-nearly-complete implementation, not skeleton code.

Recommended status: Nearly complete.

Recommended next action after approval:

- Keep the existing implementation as the B1 baseline.
- Add only B1-focused diagnostics/conflict/edge-case coverage if the team wants B1 to be declared complete before moving to B2.
- Do not begin propagation, UI, save/open, preview, apply, or Milestone C physical modeling in B1.
