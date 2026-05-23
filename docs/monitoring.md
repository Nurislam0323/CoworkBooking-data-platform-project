# Monitoring and Observability

- Airflow task retries: 3 попытки, задержка 2 минуты.
- Failure alerting: Telegram Bot API и Slack webhook через `notify_failure`.
- Data quality: Great Expectations suite для raw bookings.
- Lineage: JSON lineage-факты в S3 и OpenLineage-compatible зависимость job/input/output.
- Streaming metrics: ClickHouse table `space_occupancy_5m`, dashboard Grafana.
- CI observability: GitLab stages test, data_quality, build, deploy.
