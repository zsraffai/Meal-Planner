param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("stable-latest", "stable-previous")]
    [string]$Target = "stable-previous"
)

$ErrorActionPreference = "Stop"

if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    throw "Ez a mappa nem git repository."
}

$targetCommit = git rev-parse --verify "refs/tags/$Target^{commit}" 2>$null
if (-not $targetCommit) {
    throw "Nem található a cél stabil tag: $Target"
}
$targetCommit = $targetCommit.Trim()

$backupTag = "backup-before-rollback-$(Get-Date -Format "yyyyMMdd-HHmmss")"
$currentCommit = (git rev-parse HEAD).Trim()

git tag -a $backupTag -m "Backup before rollback to $Target" $currentCommit | Out-Null
git reset --hard $targetCommit | Out-Null

Write-Host "Rollback kész."
Write-Host "Visszaállt commit: $targetCommit ($Target)"
Write-Host "Biztonsági mentés tag: $backupTag -> $currentCommit"
