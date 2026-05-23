# Data Lineage

## Batch lineage

- `data/samples/bookings.csv` -> `bronze/booking_operations/bookings` -> `silver.bookings` -> `gold.client_features` -> Feast/Cube.js.
- `Booking API /booking-events` -> `bronze/booking_operations/booking_events`.

## Streaming lineage

- `streaming/event_simulator` -> Kafka topic `coworkbooking.workplace_events` -> Flink job `space_occupancy_5m` -> ClickHouse `coworkbooking.space_occupancy_5m` -> Grafana/Cube.js.

Airflow DAG дополнительно пишет JSON lineage-факт в `s3://<bucket>/lineage/booking_operations/`.
