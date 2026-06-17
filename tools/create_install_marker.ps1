param(
    [Parameter(Mandatory=$true)][string]$AppDir,
    [Parameter(Mandatory=$true)][string]$ProgramDataDir
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
New-Item -ItemType Directory -Force -Path $ProgramDataDir | Out-Null

$appIdPath = Join-Path $AppDir "install_id.dat"
$pdIdPath = Join-Path $ProgramDataDir "install_id.dat"

if (Test-Path $appIdPath) {
    $id = (Get-Content -Raw -Path $appIdPath).Trim()
} elseif (Test-Path $pdIdPath) {
    $id = (Get-Content -Raw -Path $pdIdPath).Trim()
} else {
    $id = [guid]::NewGuid().ToString("N")
}

if ([string]::IsNullOrWhiteSpace($id)) {
    $id = [guid]::NewGuid().ToString("N")
}

Set-Content -Path $appIdPath -Value $id -Encoding ASCII
Set-Content -Path $pdIdPath -Value $id -Encoding ASCII
