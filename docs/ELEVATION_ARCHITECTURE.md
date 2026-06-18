# NEVIS 2.03 Elevation Architecture

## Source Of Truth

- Edge.start_z
- Edge.end_z

are the source of truth.

Node.z is derived/display only.

## Lock Precedence

elevation_locked always wins.

Never overwrite locked values.

## Propagation Model

Anchor
-> Frontier
-> Known Set
-> Propagation
-> Conflict
-> Validation

## Known Set

known[(edge_id, endpoint)]

Once assigned:

- never overwrite
- conflict instead

## 集合管

Milestone B:

- single-Z node
- topology only
- no physical offset
- no B dimension
- no insertion depth
- no multiple Z per port

## Milestone B Scope

Topology only.

See docs/ELEVATION_SCOPE.md.

Excluded:

- physical fitting geometry
- catalog dimensions
- invert offset modeling

Those belong to Milestone C.
