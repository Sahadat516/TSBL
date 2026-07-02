param(
    [Parameter(Mandatory = $true)]
    [string]$Message
)

Set-Location -Path "$PSScriptRoot\..\backend"

if (Test-Path ".venv") {
    $venvPython = ".venv\Scripts\python"
} else {
    $venvPython = "python"
}

& $venvPython -m alembic revision --autogenerate -m "$Message"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nMigration created successfully" -ForegroundColor Green
} else {
    Write-Host "`nMigration failed" -ForegroundColor Red
}
