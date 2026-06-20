# Project State

Date: 2026-06-18
Current version: NEVIS 2.03
Main entrypoint: `Nevis_no_ui.py`

## Active Modules and Features

- Main PySide6 desktop UI and central drawing preview.
- Pipe graph/model display, selection, pan, zoom, and eight-direction interactions.
- Fitting selection and existing fitting algorithms.
- BOM/material table and Excel export path.
- JWW import/background and JWW export path.
- Undo workflow.
- Quick Check read-only validation panel.
- PDF/image underlay Phase 1:
  - Load, show/hide, opacity, and clear.
  - Mouse pass-through.
- PDF underlay Phase 2A candidate:
  - Two-point straightening and current-angle display.
  - Underlay-only rotation persisted across redraws.
- Vietnamese/Japanese UI translation paths.

## Hidden or Disabled Modules

- Elevation UI is disabled by `ELEVATION_UI_ENABLED = False`.
  Elevation-related code/tests remain present but are not exposed in the normal UI.
- Library tree tab is hidden by default through `show_library_tab = False`.
- The obsolete reducer task panel is hidden; the current reducer/undo workflow remains active.
- Main-system selection controls are hidden in drainage-only mode.
- PDF rotate/flip and clear commands are not on the main toolbar; they are secondary PDF-menu actions.
- `Căn tỷ lệ` is reserved but hidden/disabled because Phase 2B is not implemented.

## Modules Under Development

- PDF Underlay Phase 2A:
  - Automated implementation is present and passing.
  - Manual acceptance with real 1-3 degree tilted PDFs is pending.
- PDF Underlay Phase 2B:
  - Known-distance scaling workflow is not implemented.
- Long-term PDF tracing pipeline:
  - `PDF -> Align -> Scale -> Trace -> BOM -> JWW`.
  - Trace/BOM/JWW automation from PDF is conceptual only.

## Verified Test State

- `tests.test_pdf_underlay_workflow`: 6/6 PASS.
- `tests.test_pipe_quick_check`: 10/10 PASS.
- Combined focused result: 16/16 PASS on 2026-06-18.

## Stability Boundary

Underlay work must not alter the PDF renderer, NEVIS model coordinates/topology,
fitting algorithms, BOM behavior, JWW behavior, Elevation behavior, or Quick Check logic.
