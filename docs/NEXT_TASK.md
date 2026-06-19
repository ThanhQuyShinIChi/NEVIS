# Next Task

Date: 2026-06-18

## Current Status

NEVIS 2.03 is in a stable handover state. The main application starts normally,
the central preview remains usable without a main-pipe size at startup, and the
PDF underlay no longer blocks pipe selection, drawing, pan, or zoom.

### Completed

- PDF Underlay Phase 1:
  - Load the first page of a PDF or load an image.
  - Show/hide the underlay and adjust opacity.
  - Clear the underlay from the PDF menu.
  - Underlay ignores mouse input and does not intercept model interaction.
  - PDF toolbar is responsive at narrow window sizes.
- Quick Check:
  - Read-only validation panel is complete.
  - Error codes E101, E102, E201, E202, and E203 are active.
  - TMP to DV fitting fallback is accepted when the resolver finds a valid file.
  - Quick Check regression suite: 10/10 PASS.
- Startup/UI stability:
  - The application no longer locks the whole workflow when main-pipe size is empty.
  - Apply/draw actions show a light message: `Vui lòng nhập kích thước ống chính`.
  - Preview toolbar keeps Detail, Undo, Fit, PDF, visibility, opacity, and alignment controls.
  - Rotate/flip and clear-background commands are secondary items in the PDF menu.

### Current Phase 2A Implementation

The current workspace already contains a working and automated-tested version of
PDF Underlay Phase 2A (two-point straightening). It rotates only the underlay,
shows the current angle, survives scene redraw, and leaves the NEVIS model unchanged.
This implementation still needs user acceptance with real project PDFs on the home PC.

## Next Tasks

1. PDF Underlay Phase 2A - Straighten (`Căn thẳng`)
   - Reopen and manually verify with real PDF/image files tilted by 1-3 degrees.
   - Confirm point A/B workflow, horizontal/vertical snapping, pan/zoom, and 8-direction pipe work.
   - Treat this as acceptance/hardening only; do not redesign the renderer.
2. PDF Underlay Phase 2B - Scale (`Căn tỷ lệ`)
   - Define the two-point known-distance workflow before implementation.
   - Scale only the underlay; never transform the NEVIS model.

## Boundaries

Do not change PDF rendering, model topology, fitting algorithms, BOM, JWW, Elevation,
or Quick Check while completing the underlay alignment/scale work unless a separate
task explicitly authorizes it.
