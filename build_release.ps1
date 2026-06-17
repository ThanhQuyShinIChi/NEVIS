param(
    [switch]$InstallDeps,
    [switch]$BuildInstaller
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Release = Join-Path $Root "release\NEVIS_MEP"

Set-Location $Root

if ($InstallDeps) {
    py -m pip install -r requirements-build.txt
}

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "release") { Remove-Item -Recurse -Force "release" }
New-Item -ItemType Directory -Force -Path $Release | Out-Null

py -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name "Nevis" `
    --icon "Ico\icon_tan.ico" `
    --hidden-import openpyxl `
    "Nevis_no_ui.py"

py -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name "Nevis_Library_Editor" `
    --icon "Ico\icon_tan.ico" `
    "Nevis_JSON_Library_Editor_FINAL_i18n.py"

Copy-Item "dist\Nevis.exe" $Release -Force
Copy-Item "dist\Nevis_Library_Editor.exe" $Release -Force

Copy-Item "library" (Join-Path $Release "library") -Recurse -Force
Copy-Item "Ico" (Join-Path $Release "Ico") -Recurse -Force

foreach ($f in @(
    "nevis_master.json",
    "nevis_settings.json",
    "system_config.json",
    "nevis_library_index.json",
    "Nevis_JSON_Library_Editor_FINAL_i18n.py"
)) {
    if (Test-Path $f) {
        Copy-Item $f $Release -Force
    }
}

New-Item -ItemType Directory -Force -Path (Join-Path $Release "tools") | Out-Null
Copy-Item "tools\create_install_marker.ps1" (Join-Path $Release "tools\create_install_marker.ps1") -Force
Copy-Item "Nevis_JWW_Gaibu.bat" (Join-Path $Release "Nevis_JWW_Gaibu.bat") -Force

Write-Host "Release folder ready:" $Release

if ($BuildInstaller) {
    $iscc = (Get-Command iscc.exe -ErrorAction SilentlyContinue)
    if (-not $iscc) {
        throw "Inno Setup compiler is not installed. Install Inno Setup, then run again with -BuildInstaller."
    }
    & $iscc.Source "NevisInstaller.iss"
}
