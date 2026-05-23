# Команды для проверки перед защитой

Этот файл - короткая шпаргалка. Его задача: заранее прогнать проект дома и понять, какие части реально запускаются live, а какие являются архитектурными заготовками для выполнения требований задания.

## 1. Что реально запускать на защите

Главный рабочий сценарий:

```powershell
cd C:\Users\e_vla\Desktop\Руденкова\ПРОЕКТ
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

Эта команда запускает локальный демо-стенд и выполняет полный прогон:

- очищает старое состояние Docker-проекта `coworkbooking-demo`;
- поднимает `MinIO`, `Kafka`, `Zookeeper`, `ClickHouse`;
- запускает Python pipeline в Docker-контейнере Airflow;
- создает Parquet-файлы в слоях Bronze, Silver, Gold;
- выполняет проверки качества данных;
- создает lineage JSON;
- создает признаки для Feature Store;
- генерирует события рабочих мест;
- отправляет события в Kafka;
- загружает агрегаты в ClickHouse;
- создает локальный HTML dashboard.

Успешный результат в конце:

```text
LOCAL DEMO PASS
```

## 2. Что нужно сделать дома заранее

Сначала открой Docker Desktop и дождись статуса `Running`.

Потом в PowerShell выполни:

```powershell
docker version
docker compose version
```

Если обе команды выводят версии без ошибок, Docker готов.

Дальше перейди в папку проекта:

```powershell
cd C:\Users\e_vla\Desktop\Руденкова\ПРОЕКТ
```

Заранее скачай Docker-образы, чтобы на защите не зависеть от интернета:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml pull
docker pull apache/airflow:2.7.1-python3.9
```

После этого выполни основной прогон:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

## 3. Быстрые проверки после запуска

Проверить, что контейнеры запущены:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml ps
```

Проверить количество строк в ClickHouse-таблице с real-time агрегатами:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse clickhouse-client --query "SELECT count() FROM coworkbooking.space_occupancy_5m"
```

Ожидаемо: примерно `109`.

Проверить выручку по сегментам клиентов:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse clickhouse-client --query "SELECT segment, round(sum(total_price), 0), countDistinct(client_id) FROM coworkbooking.booking_revenue GROUP BY segment ORDER BY segment"
```

Ожидаемо должны быть сегменты:

- `corporate`;
- `freelancer`;
- `startup`;
- `student`.

Проверить, что события попали в Kafka:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic coworkbooking.workplace_events
```

Ожидаемо: offset около `180`.

## 4. Что открыть в браузере

MinIO console:

```text
http://localhost:9001
```

Логин:

```text
minioadmin
```

Пароль:

```text
minioadmin
```

ClickHouse HTTP:

```text
http://localhost:8123
```

Локальный dashboard создается как HTML-файл:

```text
C:\Users\e_vla\Desktop\Руденкова\ПРОЕКТ\data\runtime\dashboard\index.html
```

Отчет прогона:

```text
C:\Users\e_vla\Desktop\Руденкова\ПРОЕКТ\data\runtime\reports\LOCAL_DEMO_SUMMARY.md
```

## 5. Что является рабочим, а что заготовкой

Рабочий live-сценарий:

- `scripts/run_local_demo.ps1`;
- `scripts/local_full_demo.py`;
- `docker-compose.local.yml`;
- `data/samples`;
- `data/runtime`;
- `Kafka`;
- `ClickHouse`;
- `MinIO`;
- quality reports;
- lineage;
- local dashboard.

Архитектурные заготовки, которые показываются как часть структуры проекта:

- `infra/terraform` - Infrastructure as Code для облака;
- `orchestration/airflow/dags` - пример настоящего Airflow DAG;
- `great_expectations` - структура для Data Quality;
- `lakehouse/spark` - PySpark/SQL-трансформации;
- `feature_store` - Feast-описание признаков;
- `semantic/cube` - Cube.js semantic layer;
- `semantic/web` - embedded analytics UI;
- `.gitlab-ci.yml` - CI/CD pipeline.

Правильная формулировка на защите:

> Для стабильной демонстрации я запускаю локальный end-to-end сценарий через Docker. Он реально создает данные, проверки, Kafka events и ClickHouse-агрегаты. Остальные папки показывают, как эта же платформа раскладывается по полноценным промышленным компонентам: Terraform, Airflow, Feast, Cube.js и CI/CD.

## 6. Как остановить стенд

После проверки можно остановить контейнеры:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local_demo.ps1
```

Если нужно полностью удалить локальные volumes и начать с чистого состояния:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml down -v
```

Основной скрипт `run_local_demo.ps1` сам очищает volumes проекта `coworkbooking-demo`, потому что демо каждый раз пересоздает данные заново. Это снижает риск ошибок из-за старого состояния Kafka, Zookeeper или ClickHouse.

## 7. Если что-то пошло не так

Если Docker пишет, что daemon недоступен:

1. Открой Docker Desktop.
2. Дождись статуса `Running`.
3. Повтори:

```powershell
docker version
```

Если занят порт:

- `9001` - MinIO console;
- `8123` - ClickHouse;
- `29092` - Kafka external listener.

Можно остановить стенд:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local_demo.ps1
```

Потом запустить снова:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

## 8. Самый короткий сценарий для защиты

Если времени мало, делай так:

```powershell
cd C:\Users\e_vla\Desktop\Руденкова\ПРОЕКТ
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse clickhouse-client --query "SELECT count() FROM coworkbooking.space_occupancy_5m"
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic coworkbooking.workplace_events
```

Потом открыть:

```text
data\runtime\reports\LOCAL_DEMO_SUMMARY.md
data\runtime\dashboard\index.html
docs\PROJECT_EXPLAINED.md
presentation\coworkbooking_data_platform_defense.pptx
```
