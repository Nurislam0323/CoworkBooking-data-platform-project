# Карта проекта

Этот файл нужен для быстрой навигации по проекту во время защиты.

## 1. Инфраструктура

`infra/terraform/yandex`

Здесь описана облачная часть платформы:

- S3-compatible Object Storage для Lakehouse;
- Managed Kafka для потоковых событий;
- Compute VM для запуска Docker/Airflow;
- cloud-init сценарий установки Docker и запуска сервисов.

Во время защиты я показываю `main.tf`, `variables.tf`, `outputs.tf` и объясняю, что локальный стенд повторяет ту же архитектурную идею без облачных секретов.

## 2. Домены и Data Product

`data/domains.yaml`

Домены:

- `booking_operations` - бронирования, статусы, оплата и выручка;
- `space_operations` - рабочие места, зоны, загрузка помещений;
- `customer_engagement` - активность, сегменты и удержание клиентов.

`data-products/booking_operations/data_product.yaml`

Здесь описан Data Product `Client Booking Features`: интерфейсы, схема, SLA и метрики качества.

## 3. Batch ingestion и качество данных

`orchestration/airflow/dags/raw_ingestion_dag.py`

DAG загружает CSV и Booking API в Bronze слой, выполняет проверки, пишет Parquet и lineage.

`great_expectations`

Хранит suite с проверками качества: уникальность ключа, обязательные поля, допустимые статусы и неотрицательная стоимость.

## 4. Lakehouse

`lakehouse/spark/jobs`

Spark jobs показывают, как Bronze слой очищается в Silver и агрегируется в Gold.

`lakehouse/spark/lib/transformations.py`

Отдельно вынесена бизнес-логика расчета клиентских признаков. На нее написан unit-test.

## 5. Feature Store

`feature_store/feast`

Feast repository содержит entity `client` и feature view `client_booking_features`.

В локальном прогоне создается:

- `data/feature_store/client_features.parquet`;
- `feature_store/feast/data/local_registry.json`.

## 6. Streaming

`streaming/event_simulator/producer.py`

Генератор событий клиентов и рабочих мест.

`streaming/flink/workplace_event_window_job.py`

Flink job со скользящими окнами по загрузке зон коворкинга.

`streaming/clickhouse/schema.sql`

Таблицы ClickHouse для realtime-агрегатов и аналитического слоя.

## 7. Semantic Layer и UI

`semantic/cube/schema`

Cube.js схемы `BookingOperations` и `SpaceUtilization`.

`semantic/web`

React-интерфейс с drill-down от клиентского сегмента к площадке.

## 8. Локальный прогон

`scripts/run_local_demo.ps1`

Главная команда для защиты. Она запускает Docker-стенд и прогоняет данные по всему маршруту.

`scripts/local_full_demo.py`

Локальный pipeline для воспроизводимой демонстрации. Он создает Parquet, quality reports, lineage, feature artifacts, Kafka events, ClickHouse CSV и dashboard.

## 9. CI/CD

`.gitlab-ci.yml`

Pipeline:

- `pytest`;
- data quality checks;
- сборка Docker-образов Airflow и Cube.js;
- деплой на тестовый стенд по SSH.
