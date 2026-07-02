param(
    [string]$Path = "tests/",
    [switch]$Coverage
)

Set-Location -Path "$PSScriptRoot\..\backend"

if ($Coverage) {
    python -m pytest $Path -v --tb=short --cov=app --cov-report=term --cov-report=html
} else {
    python -m pytest $Path -v --tb=short
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== All tests passed ===" -ForegroundColor Green
} else {
    Write-Host "`n=== Tests failed ===" -ForegroundColor Red
}
