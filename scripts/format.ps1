Write-Host "=== Formatting Python code ===" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\backend"

if (Get-Command "ruff" -ErrorAction SilentlyContinue) {
    ruff format app/
    ruff check --fix app/
} else {
    Write-Host "ruff not found. Install with: pip install ruff" -ForegroundColor Yellow
}

Write-Host "`n=== Formatting TypeScript code ===" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\frontend"

if (Get-Command "npx" -ErrorAction SilentlyContinue) {
    npx prettier --write "src/**/*.{ts,tsx,json,css}"
} else {
    Write-Host "npx not found. Ensure Node.js is installed." -ForegroundColor Yellow
}

Write-Host "`n=== Format complete ===" -ForegroundColor Green
