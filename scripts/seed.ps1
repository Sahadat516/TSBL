Set-Location -Path "$PSScriptRoot\..\backend"

Write-Host "Seeding database..." -ForegroundColor Cyan
python -m app.seed

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database seeded successfully" -ForegroundColor Green
} else {
    Write-Host "Seed failed" -ForegroundColor Red
}
