$exitCode = 0

Write-Host "=== Linting Python code ===" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\backend"

if (Get-Command "ruff" -ErrorAction SilentlyContinue) {
    ruff check app/
    if ($LASTEXITCODE -ne 0) { $exitCode = 1 }
    mypy app/
    if ($LASTEXITCODE -ne 0) { $exitCode = 1 }
} else {
    Write-Host "ruff/mypy not found. Install with: pip install ruff mypy" -ForegroundColor Yellow
}

Write-Host "`n=== Linting TypeScript code ===" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\frontend"

if (Test-Path "node_modules") {
    npx next lint
    if ($LASTEXITCODE -ne 0) { $exitCode = 1 }
    npx tsc --noEmit
    if ($LASTEXITCODE -ne 0) { $exitCode = 1 }
} else {
    Write-Host "node_modules not found. Run: npm install" -ForegroundColor Yellow
}

if ($exitCode -eq 0) {
    Write-Host "`n=== All lints passed ===" -ForegroundColor Green
} else {
    Write-Host "`n=== Lint issues found ===" -ForegroundColor Red
}
exit $exitCode
