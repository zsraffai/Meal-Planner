$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SnapshotsDir = Join-Path $ProjectRoot ".snapshots"

if (-not (Test-Path $SnapshotsDir)) {
    Write-Host "Még nincs .snapshots mappa."
    exit 0
}

$snapshots = Get-ChildItem -Path $SnapshotsDir -Directory | Sort-Object Name -Descending

if (-not $snapshots) {
    Write-Host "Nincs mentett snapshot."
    exit 0
}

Write-Host "Elérhető snapshotok:"
$snapshots | ForEach-Object {
    Write-Host "- $($_.Name)"
}
