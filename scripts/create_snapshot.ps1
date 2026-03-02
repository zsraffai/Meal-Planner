param(
    [Parameter(Mandatory = $false)]
    [string]$Label = "change"
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SnapshotsDir = Join-Path $ProjectRoot ".snapshots"

if (-not (Test-Path $SnapshotsDir)) {
    New-Item -Path $SnapshotsDir -ItemType Directory | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$SafeLabel = ($Label -replace "[^a-zA-Z0-9_-]", "-").Trim('-')
if ([string]::IsNullOrWhiteSpace($SafeLabel)) {
    $SafeLabel = "change"
}

$SnapshotName = "$Timestamp-$SafeLabel"
$SnapshotPath = Join-Path $SnapshotsDir $SnapshotName
New-Item -Path $SnapshotPath -ItemType Directory | Out-Null

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
    Copy-Item -Path $_.FullName -Destination $SnapshotPath -Recurse -Force
}

$Meta = [ordered]@{
    snapshot = $SnapshotName
    created_at = (Get-Date).ToString("s")
    label = $Label
}

$Meta | ConvertTo-Json | Set-Content -Path (Join-Path $SnapshotPath "snapshot.json") -Encoding UTF8

Write-Host "Snapshot létrehozva: $SnapshotName"
Write-Host "Elérési út: $SnapshotPath"
