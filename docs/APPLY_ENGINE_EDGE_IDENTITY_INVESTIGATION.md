# Apply Engine Edge Identity Investigation

Date: 2026-06-18
Status: Test investigation only - no wiring

## Question

Can canonical endpoint-pair identity remain stable between B6 preview and apply
when the edge list changes?

The investigation uses the real B1-B6 pipeline to create a `Proposed` row and
a test-local reference verifier. No production Apply Engine or NEVIS wiring is
changed.

## Identity Under Test

The captured preview identity contains:

- Canonical pair `(min(a, b), max(a, b))` for lookup.
- Expected oriented pair `(a, b)`.
- Target endpoint and expected target node.
- Preview edge index for diagnostics only.
- Target old value and lock state for basic stale-attribute checks.

The verifier rebuilds a pair index from the current model immediately before
the reference write. It rejects zero matches, multiple matches, orientation
mismatch, endpoint-node mismatch, changed target value, or changed lock state.

## Cases

1. Preview then apply without topology change:
   - Pair resolves to the original edge and original index.

2. Preview, delete another edge, then apply:
   - Target index shifts.
   - Pair plus orientation still resolves the correct target.
   - This demonstrates why preview index cannot be identity.

3. Preview, add an unrelated edge, then apply:
   - Unique target pair remains resolvable.
   - The unrelated edge is not modified.

4. Add a second edge with the same canonical pair:
   - Verification hard-blocks before write.
   - Reversed orientation is still treated as the same canonical pair.

## Expected Finding

Endpoint-pair identity is sufficiently stable as an intermediate identity for
the tested single-edge-per-node-pair model. It survives unrelated index shifts
and unrelated additions.

It is not sufficient by itself:

- Orientation must be retained and verified for `start`/`end` semantics.
- A global uniqueness check is mandatory.
- Multi-edge must hard-block; no edge may be selected by index or list order.
- Relevant attributes and a fresh B1-B6 report still require verification.
- Parallel edges require a future stable edge ID.

## Decision Boundary

Passing these tests would support continuing blocker-resolution work at module
level. It would not approve wiring `Nevis_no_ui.py`.
