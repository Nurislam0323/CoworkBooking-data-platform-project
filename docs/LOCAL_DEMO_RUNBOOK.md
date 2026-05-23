# Local Demo Runbook

Дата защиты: 22 мая 2026.

## Основной сценарий

Откройте PowerShell в корне проекта:

```powershell
cd C:\Users\e_vla\Desktop\Руденкова\ПРОЕКТ
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

Команда делает полный локальный прогон:

1. Поднимает MinIO, Kafka, Zookeeper и ClickHouse через `docker-compose.local.yml`.
2. В контейнере `apache/airflow:2.7.1-python3.9` запускает batch pipeline с `pandas + pyarrow`.
3. Пишет настоящие Parquet-файлы в Bronze/Silver/Gold.
4. Выполняет проверки качества в стиле Great Expectations.
5. Генерирует Data Lineage JSON.
6. Создает Feature Store артефакты Feast.
7. Генерирует workplace events, публикует их в Kafka и грузит агрегаты в ClickHouse.
8. Создает локальный HTML dashboard.

## Что показать комиссии

- Отчет прогона: `data/runtime/reports/LOCAL_DEMO_SUMMARY.md`.
- Dashboard: `data/runtime/dashboard/index.html`.
- Parquet-слои: `data/runtime/lakehouse/bronze`, `silver`, `gold`.
- Quality reports: `data/runtime/reports/quality_*.json`.
- Lineage: `data/runtime/lineage/lineage.json`.
- Kafka topic: `coworkbooking.workplace_events`.
- ClickHouse tables: `coworkbooking.space_occupancy_5m`, `coworkbooking.booking_revenue`.
- Презентация: `presentation/coworkbooking_data_platform_defense.pptx`.

## Быстрые проверки после запуска

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse clickhouse-client --query "SELECT count() FROM coworkbooking.space_occupancy_5m"
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse clickhouse-client --query "SELECT segment, round(sum(total_price), 0), countDistinct(client_id) FROM coworkbooking.booking_revenue GROUP BY segment ORDER BY segment"
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic coworkbooking.workplace_events
```

Ожидаемо:

- `space_occupancy_5m`: около 109 строк.
- `booking_revenue`: сегменты `corporate`, `freelancer`, `startup`, `student`.
- Kafka offset: 180 событий после чистого запуска.

## Остановка стенда

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local_demo.ps1
```

## Если Docker недоступен

Можно показать артефакты уже созданного прогона в `data/runtime` и объяснить, что основной запуск выполняется командой `run_local_demo.ps1`. На защите лучше заранее открыть Docker Desktop и дождаться статуса Running.
