# ADR-001: Yandex Cloud + S3-compatible Lakehouse + Kafka для CoworkBooking

## Статус
Принято.

## Контекст
Требуется показать облачную основу платформы данных для CoworkBooking без локальной установки тяжелых инструментов. Нужны объектное хранилище, Kafka, VM для оркестратора и воспроизводимая инфраструктура.

## Решение
Используем Yandex Cloud: Object Storage как S3-compatible Data Lake, Managed Kafka для событий бронирования и рабочих мест, Compute VM с Docker Compose для Airflow и вспомогательных сервисов. Для локальной демонстрации используется MinIO/Kafka/ClickHouse/Grafana/Cube.js в Docker Compose.

## Последствия
Платформа переносима: S3 API позволяет заменить Yandex Object Storage на AWS S3 или GCS S3-compatible gateway. Terraform фиксирует инфраструктурные зависимости, а Docker Compose упрощает защиту проекта.
