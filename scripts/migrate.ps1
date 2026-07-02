param(
    [ValidateSet("up", "down", "revision")]
    [string]$Action = "up",
    [int]$Revision = 1
)

Set-Location -Path "$PSScriptRoot\..\backend"

if ($Action -eq "up") {
    Write-Host "Running migrations up..." -ForegroundColor Cyan
    python -m alembic upgrade head
} elseif ($Action -eq "down") {
    Write-Host "Rolling back $Revision revision(s)..." -ForegroundColor Yellow
    python -m alembic downgrade -$Revision
} elseif ($Action -eq "revision") {
    Write-Host "Creating new migration revision..." -ForegroundColor Cyan
    python -m alembic revision --autogenerate
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nMigration ${Action} completed" -ForegroundColor Green
} else {
    Write-Host "`nMigration ${Action} failed" -ForegroundColor Red
}
