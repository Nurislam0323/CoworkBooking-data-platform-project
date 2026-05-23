# Сценарий защиты

1. Показать связь с прошлым проектом `CoworkBooking`: система бронирования рабочих мест теперь получила платформу данных.
2. Показать ADR и домены данных.
3. Открыть Terraform и объяснить Object Storage, Managed Kafka, VM.
4. Запустить локальный прогон: `powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1`.
5. Показать `data/runtime/reports/LOCAL_DEMO_SUMMARY.md`.
6. Показать Parquet-файлы: `data/runtime/lakehouse/bronze`, `silver`, `gold`.
7. Показать quality-отчеты: `data/runtime/reports/quality_*.json`.
8. Показать Feast local registry и feature table: `feature_store/feast/data/local_registry.json`, `data/feature_store/client_features.parquet`.
9. Показать Kafka topic и offset командой из `docs/LOCAL_DEMO_RUNBOOK.md`.
10. Показать ClickHouse агрегаты командой из `docs/LOCAL_DEMO_RUNBOOK.md`.
11. Открыть dashboard `data/runtime/dashboard/index.html`.
12. Показать Cube.js schema и React UI как production-like embedded analytics контур.
13. Показать GitLab CI/CD pipeline и deploy stage.
