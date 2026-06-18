# Design Decisions

Decision 001

Edge.start_z/end_z are source of truth.

Reason:

Y/LT/DT/集合管 may connect multiple edges.

Decision 002

Node.z is derived only.

Reason:

avoid multiple ownership.

Decision 003

集合管 is single-Z in Milestone B.

Reason:

physical offset postponed to Milestone C.

Scope:

docs/ELEVATION_SCOPE.md

Decision 004

Do not infer building structure.

No:

- stack middle
- stack end
- final manifold

Use topology only.

Decision 005

Fail loud.

Conflict > Auto Guess.
