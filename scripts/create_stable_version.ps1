param(
    [Parameter(Mandatory = $false)]
    [string]$Label = "update"
)

$ErrorActionPreference = "Stop"

$safeLabel = ($Label -replace "[^a-zA-Z0-9_-]", "-").Trim("-")
if ([string]::IsNullOrWhiteSpace($safeLabel)) {
    $safeLabel = "update"
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$stableTag = "stable-$timestamp-$safeLabel"

if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    throw "Ez a mappa nem git repository."
}

if (-not (git config --get user.name 2>$null)) {
    git config user.name "Local User" | Out-Null
}
if (-not (git config --get user.email 2>$null)) {
    git config user.email "local@example.com" | Out-Null
}

git add -A

$stagedFiles = git diff --cached --name-only
$hasStagedChanges = -not [string]::IsNullOrWhiteSpace(($stagedFiles -join ""))

$hasHead = $true
try {
    git rev-parse --verify HEAD 1>$null 2>$null
} catch {
    $hasHead = $false
}

if ($hasStagedChanges) {
    git commit -m "stable: $Label" | Out-Null
} elseif (-not $hasHead) {
    git commit --allow-empty -m "stable: $Label (empty baseline)" | Out-Null
}

$headCommit = (git rev-parse HEAD).Trim()

$previousLatest = $null
try {
    $previousLatest = (git rev-parse --verify "refs/tags/stable-latest`^{commit}" 2>$null).Trim()
} catch {
    $previousLatest = $null
}

git tag -a $stableTag -m "Stable version: $Label" | Out-Null

if ($previousLatest) {
    git tag -f stable-previous $previousLatest | Out-Null
}

git tag -f stable-latest $headCommit | Out-Null

Write-Host "Stabil verzió létrehozva: $stableTag"
Write-Host "Mutató tag: stable-latest -> $headCommit"
if ($previousLatest) {
    Write-Host "Előző stabil: stable-previous -> $previousLatest"
}
