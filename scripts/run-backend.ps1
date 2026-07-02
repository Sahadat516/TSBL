param(
    [string]$Host = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Reload = $true
)

$reloadArg = if ($Reload) { "--reload" } else { "" }
$envFile = if (Test-Path ".env") { "" } else { "--env-file .env.dev" }

Write-Host "Starting backend on $Host`:$Port..." -ForegroundColor Green
uvicorn app.main:app --host $Host --port $Port $reloadArg $envFile
