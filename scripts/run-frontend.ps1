param(
    [int]$Port = 3000
)

$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
$env:NEXT_PUBLIC_WS_URL = "ws://localhost:8000"

Write-Host "Starting frontend on port $Port..." -ForegroundColor Green
npx next dev -p $Port
