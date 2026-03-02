$ErrorActionPreference = "Stop"

if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    throw "Ez a mappa nem git repository."
}

$stableTags = git tag --list "stable-*" --sort=-creatordate

if (-not $stableTags) {
    Write-Host "Nincs még stabil verzió tag."
    exit 0
}

Write-Host "Stabil verziók:"
$stableTags | ForEach-Object {
    $tagName = $_.Trim()
    $commit = (git rev-list -n 1 $tagName).Trim()
    Write-Host "- $tagName -> $commit"
}

$latest = $null
$previous = $null

try {
    $latest = (git rev-parse --verify "refs/tags/stable-latest`^{commit}" 2>$null).Trim()
} catch {
    $latest = $null
}

try {
    $previous = (git rev-parse --verify "refs/tags/stable-previous`^{commit}" 2>$null).Trim()
} catch {
    $previous = $null
}

if ($latest) {
    Write-Host ""
    Write-Host "stable-latest  -> $latest"
}
if ($previous) {
    Write-Host "stable-previous -> $previous"
}
