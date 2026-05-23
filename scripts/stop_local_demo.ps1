$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root
docker compose -p coworkbooking-demo -f docker-compose.local.yml down
