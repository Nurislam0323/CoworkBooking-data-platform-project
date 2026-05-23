# Data Product: Client Booking Features

Продукт данных принадлежит домену `booking_operations` и публикует признаки клиентов CoworkBooking для аналитики и ML.

## Интерфейсы

- Batch: Iceberg table `gold.booking_operations.client_features`.
- Feature Store: Feast FeatureView `client_booking_features`.
- Semantic Layer: Cube.js cube `BookingOperations`.

## SLA

- Доступность: 99.5% в месяц.
- Свежесть: ежедневное обновление до 04:00 UTC.
- Качество: отсутствие дублей `client_id`, обязательные поля не NULL, стоимость бронирований неотрицательна.

## Метрики качества

- `duplicate_client_id_count`
- `null_required_field_count`
- `negative_booking_value_count`
- `freshness_lag_hours`
