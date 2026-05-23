# Инструкция по развертыванию

## Локальный стенд

1. Установить Docker Desktop.
2. Скопировать `.env.example` в `.env`.
3. Запустить `docker compose -p coworkbooking-platform up -d`.
4. Открыть Airflow `http://localhost:8080`, логин `admin`, пароль `admin`.
5. Запустить DAG `booking_operations_raw_ingestion`.

## Облако

1. Создать сервисный аккаунт Yandex Cloud и выдать права на Object Storage, Compute, VPC, Managed Kafka.
2. Заполнить `infra/terraform/yandex/terraform.tfvars`.
3. Выполнить `terraform init`, `terraform plan`, `terraform apply`.
4. Перейти по `airflow_url` из outputs.

## Feature Store

```bash
cd feature_store/feast
feast apply
python materialize_features.py
```

## Потоковый контур

1. Запустить Kafka и ClickHouse.
2. Запустить `python streaming/event_simulator/producer.py`.
3. Отправить Flink job `streaming/flink/workplace_event_window_job.py`.
4. Открыть Grafana и dashboard `Coworking Realtime Occupancy`.
