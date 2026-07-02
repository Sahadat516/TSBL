param(
    [switch]$Force
)

if (-not $Force) {
    $confirm = Read-Host "This will DESTROY all data. Type 'RESET' to confirm"
    if ($confirm -ne "RESET") {
        Write-Host "Cancelled" -ForegroundColor Yellow
        exit 1
    }
}

Set-Location -Path "$PSScriptRoot\..\backend"

Write-Host "Dropping all tables..." -ForegroundColor Red
python -c "
import asyncio
from app.core.database import engine, Base
async def reset():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print('All tables dropped')
        await conn.run_sync(Base.metadata.create_all)
        print('All tables created')
asyncio.run(reset())
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database reset complete" -ForegroundColor Green
} else {
    Write-Host "Reset failed" -ForegroundColor Red
}
