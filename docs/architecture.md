# Архитектура платформы

```mermaid
flowchart LR
  API[Booking API] --> AF[Airflow DAG]
  CSV[CSV exports: bookings, clients, workplaces] --> AF
  AF --> S3[(S3 Object Storage)]
  S3 --> BR[Bronze]
  BR --> SP[Spark + Iceberg]
  SP --> SI[Silver]
  SI --> GO[Gold]
  GO --> FS[Feast Feature Store]
  GO --> CH[(ClickHouse)]
  K[Kafka workplace events] --> FL[Flink windows]
  FL --> CH
  CH --> CU[Cube.js Semantic Layer]
  CU --> UI[React Embedded Analytics]
  CH --> GR[Grafana]
```

Платформа разделена по доменам Data Mesh. Домен `booking_operations` отвечает за бронирования и выручку, `space_operations` - за загрузку рабочих мест и зон, `customer_engagement` - за активность и удержание клиентов.

Основной Lakehouse хранится в S3-совместимом Object Storage. Таблицы Bronze/Silver/Gold создаются через Spark и Apache Iceberg, что дает ACID-транзакции, time travel и эволюцию схем.
