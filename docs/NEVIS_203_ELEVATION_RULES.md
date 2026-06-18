# NEVIS 2.03 — Elevation Rules / Milestone B Notes

## Core Principles

* Edge.start_z / Edge.end_z are the source of truth.
* Node.z is derived/display only.
* Do not use Node.z as input for elevation calculation.
* Do not modify BOM/JWW/export/fitting/rebuild_flow in Milestone B.
* Do not model physical fitting offset in Milestone B.
* Correctness > Performance > UI Convenience.
* Fail loud. Do not guess.

## Scope of Milestone B

Milestone B is topology-only.

Included:

* Drainage Elevation Engine v1
* Simple fitting-aware propagation
* Y / LT / DT / IN / 集合管 topology rules
* Lock handling
* Conflict detection
* Validation severity

Excluded:

* 集合管 internal offset
* B寸法
* 差口M/L
* 立て管有効長
* Multiple Z per port
* JWW elevation export
* BOM elevation data
* Physical fitting geometry elevation

Physical offset will be Milestone C.

## 集合管 Rule for Milestone B

集合管 is a single-Z topology node.

Do not assume:

* stack middle
* stack end
* final manifold
* intermediate manifold
* floor structure
* physical outlet/inlet role

Use only:

* degree(nid)
* Fitting.ftype
* connected edges
* base_nodes / parent only if needed for flow direction validation

All nodes with ftype == "集合管" use the same handler.

Rule:

* If any connected edge has Z at the 集合管 side, that value can define 集合管 Z.
* Once 集合管 Z is known, connected edges missing Z at the 集合管 side receive that Z.
* If multiple sources give the same Z within tolerance: OK.
* If multiple sources give different Z values: conflict, do not overwrite.
* If node has manually assigned Z/level: treat as explicit anchor. Connected edge values that disagree become conflict.
* Do not calculate internal port offset.

## Y / LT / DT Rule

Y / LT / DT are branch junctions.

* Main axis and branch ownership must be respected.
* Do not propagate branch A into branch B.
* Do not let one fitting modify another fitting’s branch.
* If insufficient information: stop and report.
* If locked elevation is encountered: do not overwrite.

## IN Rule

IN is pass-through for elevation in Milestone B.

* No elevation offset.
* Continue slope through IN.
* Do not change reducer orientation or size propagation logic.
* Direction issues should be validation warnings, not automatic fitting edits.

## Lock Rule

* elevation_locked=True always wins.
* Locked edge is an anchor.
* Never overwrite locked start_z/end_z.
* If propagation result conflicts with locked value: report conflict.
* Do not auto-fix.

## Validation Severity

Critical:

* reverse slope against flow direction
* conflicting wavefront values
* cycle / repeated processing beyond safe limit

High:

* conflicting Z sources at 集合管
* manual node Z conflicts with edge Z
* locked value conflicts with computed value

Medium:

* branch elevation mismatch
* clamp required
* ambiguous fitting ownership

Info:

* missing elevation
* missing anchor
* missing level datum
* zero length pipe

## Implementation Rule

Implement as additive functions.

Do not rewrite:

* existing drainage workflow
* existing fitting classification
* existing BOM
* existing JWW export
* existing save/open schema unless absolutely required

Prefer pure functions that accept PipeModel and return:

* updated edges
* warnings/conflicts
* unresolved items

Before coding, add tests for:

* simple chain
* Y branch ownership
* LT/DT branch ownership
* IN pass-through
* 集合管 single-Z rule
* multiple 集合管 in one project
* conflict detection
* locked edge protection
* reverse slope detection
