# Handover to Home PC

Date: 2026-06-18

## Project Location

- Work PC source: `C:\Users\PC\Documents\Nevis2.03`
- Home-PC handover copy: `D:\Nevis2.03`
- Main application: `Nevis_no_ui.py`
- Tests: `tests\`
- Documentation: `docs\`
- Libraries: `library\`

## Continue on Another Computer

1. Copy the complete `Nevis2.03` directory to the target computer.
2. Use Python with PySide6 support. The current work PC uses Python 3.14.
3. Open PowerShell in the copied project directory.
4. Install required packages if they are not already available.
5. Run the tests before making changes.
6. Read `docs\PROJECT_STATE.md` and `docs\NEXT_TASK.md`.
7. Start with Phase 2A manual acceptance, then design Phase 2B.

## Required Libraries

Core UI:

```powershell
python -m pip install PySide6
```

PDF loading:

```powershell
python -m pip install PyMuPDF
```

Excel export:

```powershell
python -m pip install openpyxl
```

The automated tests use Python's built-in `unittest`; `pytest` is not required.

## Run Commands

Normal source run:

```powershell
cd D:\Nevis2.03
python -u Nevis_no_ui.py
```

Development run that bypasses the machine-license check:

```powershell
cd D:\Nevis2.03
$env:NEVIS_SKIP_LICENSE='1'
python -u Nevis_no_ui.py
```

Focused handover tests:

```powershell
cd D:\Nevis2.03
$env:QT_QPA_PLATFORM='offscreen'
$env:NEVIS_SKIP_LICENSE='1'
python -m unittest tests.test_pdf_underlay_workflow tests.test_pipe_quick_check -q
```

Compile check:

```powershell
python -m py_compile Nevis_no_ui.py tests/test_pdf_underlay_workflow.py
```

## Current Project State

- Main UI starts and remains usable without a main-pipe size at startup.
- PDF Underlay Phase 1 is complete.
- Phase 2A straightening exists and passes automated tests; real-PDF acceptance remains.
- Phase 2B scaling is not implemented.
- Quick Check is complete and passes 10/10 tests.
- BOM, JWW, model, fitting, and PDF renderer were deliberately left unchanged by Phase 2A.
- Elevation UI is disabled through `ELEVATION_UI_ENABLED = False`.
- Library tab is hidden by default and can be enabled in application settings.

## Important Safety Notes

- Do not copy only `Nevis_no_ui.py`; preserve `docs`, `tests`, `library`, resources,
  and any project-local generated configuration needed by the target machine.
- Do not implement Phase 2B until Phase 2A is manually accepted.
- Alignment and scaling must transform only the PDF/image underlay.
- Run Quick Check tests after every underlay change.
