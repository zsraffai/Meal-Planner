param(
    [Parameter(Mandatory = $true)]
    [string]$SnapshotName
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SnapshotsDir = Join-Path $ProjectRoot ".snapshots"
$SnapshotPath = Join-Path $SnapshotsDir $SnapshotName

if (-not (Test-Path $SnapshotPath)) {
    Write-Error "Nem található ilyen snapshot: $SnapshotName"
    exit 1
}

$SafetyTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$SafetyName = "pre-restore-$SafetyTimestamp"
$SafetyPath = Join-Path $SnapshotsDir $SafetyName
New-Item -Path $SafetyPath -ItemType Directory | Out-Null

$ExcludeNames = @(
    ".snapshots",
    ".git",
    "__pycache__",
    ".venv",
    "venv"
)

Get-ChildItem -Path $ProjectRoot -Force | Where-Object {
    $ExcludeNames -notcontains $_.Name
} | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $SafetyPath -Recurse -Force
}

Get-ChildItem -Path $ProjectRoot -Force | Where-Object {
    $ExcludeNames -notcontains $_.Name
} | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force
}

Get-ChildItem -Path $SnapshotPath -Force | Where-Object {
    $_.Name -ne "snapshot.json"
} | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $ProjectRoot -Recurse -Force
}

Write-Host "Snapshot visszaállítva: $SnapshotName"
Write-Host "Biztonsági mentés készült: $SafetyName"
