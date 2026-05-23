param(
  [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

function Assert-LastCommand($Message) {
  if ($LASTEXITCODE -ne 0) {
    throw $Message
  }
}

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
}

if (-not $SkipDocker) {
  Write-Host "Reset Docker demo state..."
  docker compose -p coworkbooking-demo -f docker-compose.local.yml down -v --remove-orphans
  Assert-LastCommand "Docker Compose cleanup failed"

  Write-Host "Start Docker demo services..."
  docker compose -p coworkbooking-demo -f docker-compose.local.yml up -d minio zookeeper kafka clickhouse
  Assert-LastCommand "Docker Compose startup failed"
  Start-Sleep -Seconds 20
}

docker run --rm `
  -v "${Root}:/workspace" `
  -w /workspace `
  apache/airflow:2.7.1-python3.9 `
  python scripts/local_full_demo.py
Assert-LastCommand "Local Python demo pipeline failed"

if (-not $SkipDocker) {
  docker compose -p coworkbooking-demo -f docker-compose.local.yml up -d minio-init
  Assert-LastCommand "MinIO seed failed"

  docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka `
    kafka-topics --bootstrap-server localhost:9092 --delete --if-exists --topic coworkbooking.workplace_events
  Start-Sleep -Seconds 3

  docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka `
    kafka-topics --bootstrap-server localhost:9092 --create --if-not-exists --topic coworkbooking.workplace_events --partitions 1 --replication-factor 1
  Assert-LastCommand "Kafka topic creation failed"

  ((Get-Content "data/runtime/streaming/events/workplace_events.kafka.jsonl" | Where-Object { $_.Trim().Length -gt 0 }) -join "`n") |
    docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka `
      kafka-console-producer --bootstrap-server localhost:9092 --topic coworkbooking.workplace_events
  Assert-LastCommand "Kafka event publishing failed"

  docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse `
    clickhouse-client --query "TRUNCATE TABLE IF EXISTS coworkbooking.space_occupancy_5m"
  Assert-LastCommand "ClickHouse room aggregate truncate failed"

  ((Get-Content "data/runtime/streaming/aggregates/space_occupancy_5m_clickhouse.csv" | Where-Object { $_.Trim().Length -gt 0 }) -join "`n") |
    docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse `
      clickhouse-client --query "INSERT INTO coworkbooking.space_occupancy_5m FORMAT CSVWithNames"
  Assert-LastCommand "ClickHouse room aggregate load failed"

  docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse `
    clickhouse-client --query "TRUNCATE TABLE IF EXISTS coworkbooking.booking_revenue"
  Assert-LastCommand "ClickHouse booking revenue truncate failed"

  ((Get-Content "data/runtime/booking_revenue_clickhouse.csv" | Where-Object { $_.Trim().Length -gt 0 }) -join "`n") |
    docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse `
      clickhouse-client --query "INSERT INTO coworkbooking.booking_revenue FORMAT CSVWithNames"
  Assert-LastCommand "ClickHouse booking revenue load failed"
}

Write-Host ""
Write-Host "LOCAL DEMO PASS"
Write-Host "Dashboard: $Root\data\runtime\dashboard\index.html"
Write-Host "Summary:   $Root\data\runtime\reports\LOCAL_DEMO_SUMMARY.md"
Write-Host "MinIO:     http://localhost:9001 (minioadmin/minioadmin)"
Write-Host "ClickHouse:http://localhost:8123"
