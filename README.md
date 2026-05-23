# CoworkBooking Data Platform

Локальная демонстрационная data platform для предметной области **CoworkBooking**: системы бронирования рабочих мест в коворкинге.

Проект показывает полный путь данных: от CSV/API-источников и событий до проверок качества, Lakehouse-слоев, Feature Store, Kafka/ClickHouse-агрегатов, dashboard, CI/CD и документации.

## Что реализовано

- Data Mesh-домены: `booking_operations`, `space_operations`, `customer_engagement`.
- Terraform blueprint для Yandex Cloud: Object Storage, Kafka, VM.
- Airflow DAG для raw ingestion.
- Data Quality проверки в стиле Great Expectations.
- Bronze / Silver / Gold Lakehouse-слои в Parquet.
- Feature table для ML-признаков клиентов.
- Kafka topic для событий рабочих мест.
- ClickHouse-таблицы для аналитических агрегатов.
- HTML dashboard для локальной демонстрации.
- Cube.js / React / Grafana / Flink / Feast как архитектурные компоненты и заготовки.
- GitLab CI и GitHub Actions CI.

## Быстрый запуск

Откройте Docker Desktop и дождитесь статуса `Running`.

```powershell
cd C:\Users\e_vla\Desktop\вцув\ПРОЕКТ
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

Успешный результат:

```text
LOCAL DEMO PASS
```

## Проверка после запуска

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml ps
```

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse clickhouse-client --query "SELECT count() FROM coworkbooking.space_occupancy_5m"
```

Ожидаемо:

```text
109
```

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic coworkbooking.workplace_events
```

Ожидаемо:

```text
coworkbooking.workplace_events:0:180
```

## Что открыть

- Dashboard: `data/runtime/dashboard/index.html`
- Summary: `data/runtime/reports/LOCAL_DEMO_SUMMARY.md`
- Project explanation: `docs/PROJECT_EXPLAINED.md`
- File tree PDF: `PROJECT_FILE_TREE.pdf`
- Presentation: `presentation/coworkbooking_data_platform_defense.pptx`

MinIO:

```text
http://localhost:9001
login: minioadmin
password: minioadmin
```

ClickHouse HTTP endpoint:

```text
http://localhost:8123
```

Ожидаемый ответ:

```text
Ok.
```

## CI/CD

Для GitHub добавлен workflow:

```text
.github/workflows/ci.yml
```

Он выполняет:

- `pytest`;
- data quality check;
- синтаксическую проверку ключевых Python-файлов.

Зависимости для локального запуска CI-проверок перечислены в:

```text
requirements-dev.txt
```

Для GitLab также оставлен:

```text
.gitlab-ci.yml
```

## Основные папки

- `data/` - входные данные и runtime-артефакты.
- `data-products/` - Data Product по домену бронирований.
- `docs/` - документация, ADR, runbook, пояснения.
- `infra/terraform/` - Infrastructure as Code.
- `orchestration/airflow/` - Airflow DAG и Dockerfile.
- `lakehouse/spark/` - Spark/PySpark трансформации.
- `feature_store/` - Feast Feature Store.
- `streaming/` - Kafka/Flink/ClickHouse/Grafana часть.
- `semantic/` - Cube.js и React UI.
- `scripts/` - локальный запуск и сервисные скрипты.
- `tests/` - unit tests.

## Остановка стенда

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local_demo.ps1
```
