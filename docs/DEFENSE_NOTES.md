# Заметки для защиты

## Как начать рассказ

Проект является продолжением моей системы `CoworkBooking` из предыдущего курса. Тогда была спроектирована информационная система бронирования рабочих мест в коворкинге. В этом проекте я добавил платформу данных: сбор событий, Lakehouse, Feature Store, real-time аналитику, semantic layer и CI/CD.

## Почему есть два Docker Compose файла

`docker-compose.yml` - полный стенд, близкий к production-like варианту: Airflow, MinIO, Kafka, ClickHouse, Grafana, Cube.js и React UI.

`docker-compose.local.yml` - компактный стенд для защиты. Он использует уже подготовленные локальные образы и поднимает только то, что нужно для стабильной демонстрации: MinIO, Kafka, Zookeeper и ClickHouse.

Такой подход снижает риск, что на защите что-то сорвется из-за долгой сборки frontend/backend образов.

## Что делает локальный запуск

Команда:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

Выполняет:

1. Поднимает Docker-сервисы.
2. Создает Raw/Bronze данные из CSV и Booking API-like источника.
3. Проверяет качество данных.
4. Создает Silver и Gold Parquet.
5. Формирует признаки клиента для Feature Store.
6. Генерирует события рабочих мест и публикует их в Kafka.
7. Считает агрегаты загрузки зон коворкинга и грузит их в ClickHouse.
8. Создает HTML dashboard и lineage.

## Что показать в первую очередь

1. `README.md` - общий вход в проект.
2. `docs/PROJECT_MAP.md` - структура.
3. `infra/terraform/yandex/main.tf` - облачная инфраструктура.
4. `orchestration/airflow/dags/raw_ingestion_dag.py` - batch ingestion.
5. `lakehouse/spark/lib/transformations.py` - расчет признаков клиентов.
6. `streaming/flink/workplace_event_window_job.py` - streaming aggregation.
7. `semantic/cube/schema/BookingOperations.js` - semantic layer.
8. `.gitlab-ci.yml` - CI/CD.
9. `data/runtime/dashboard/index.html` - результат локального прогона.

## Проверочные числа после запуска

После успешного `run_local_demo.ps1`:

- Kafka topic `coworkbooking.workplace_events`: 180 событий.
- ClickHouse `coworkbooking.space_occupancy_5m`: около 109 строк.
- Gold feature table: 4 строки и 9 колонок.

## Если преподаватель спросит про связь с прошлым проектом

В прошлом проекте была спроектирована система бронирования рабочих мест: клиенты, администраторы, коворкинги, рабочие места, бронирования и отчеты. Здесь эти сущности стали источниками данных для платформы:

- `Client` -> entity в Feast;
- `Booking` -> batch source и аналитическая таблица выручки;
- `Workplace` и `CoworkingSpace` -> streaming события и метрики загрузки;
- административные отчеты -> semantic layer и dashboard.

## Если преподаватель спросит про облако

Terraform находится в `infra/terraform/yandex`. Для настоящего облачного запуска нужны реальные `cloud_id`, `folder_id`, service account и SSH key. В проекте подготовлен `terraform.tfvars.example`, потому что секреты нельзя хранить в репозитории.

## Если преподаватель спросит про Great Expectations

В `great_expectations/expectations` лежит suite с ожиданиями. В локальном прогоне создаются JSON-отчеты в `data/runtime/reports`. Проверяются уникальность ключей, обязательные поля, допустимые статусы, длительность и неотрицательная стоимость бронирований.

## Если преподаватель спросит про Data Mesh

Data Mesh здесь выражен через:

- домены в `data/domains.yaml`;
- владельцев доменов;
- Data Product contract в `data-products/booking_operations/data_product.yaml`;
- SLA и quality metrics;
- явные интерфейсы: batch table, Feast feature view, Cube.js semantic layer.
