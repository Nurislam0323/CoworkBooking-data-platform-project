# Подробное объяснение проекта CoworkBooking Data Platform

Этот файл написан как вводная инструкция для защиты. Его цель - объяснить проект с нуля: что это за система, зачем нужны папки, как данные проходят через платформу, что запускать и что показывать преподавателю.

## 1. Идея проекта простыми словами

В предыдущем курсе был проект `CoworkBooking` - информационная система для бронирования рабочих мест в коворкинге.

Там основная логика была такая:

- клиент выбирает рабочее место;
- система проверяет доступность;
- клиент создает бронирование;
- администратор управляет рабочими местами и смотрит отчеты.

В этом проекте поверх этой системы построена платформа данных. Она нужна не для самого бронирования, а для аналитики и обработки данных:

- сколько бронирований создается;
- какие клиентские сегменты приносят выручку;
- какие рабочие зоны загружены;
- сколько людей находится в коворкинге в реальном времени;
- какие признаки можно использовать для ML-модели;
- как автоматически проверять качество данных;
- как развернуть инфраструктуру через Terraform;
- как автоматизировать проверки и деплой через CI/CD.

Если совсем коротко:

> `CoworkBooking` - это бизнес-система, а этот проект - data-платформа вокруг нее.

## 2. Главный поток данных

Проект показывает два типа обработки данных.

### Batch pipeline

Batch - это пакетная обработка, то есть данные обрабатываются периодически, например раз в день.

В проекте batch-источники:

- `data/samples/bookings.csv` - выгрузка бронирований;
- `data/samples/clients.csv` - справочник клиентов;
- `services/lms_api/app.py` - имитация Booking API.

Путь данных:

```text
CSV + Booking API
  -> Raw/Bronze слой
  -> проверки качества
  -> Silver слой
  -> Gold слой
  -> Feature Store
  -> Semantic Layer / Dashboard
```

### Streaming pipeline

Streaming - это потоковая обработка событий почти в реальном времени.

В проекте потоковые события:

- `check_in` - клиент вошел в рабочую зону;
- `check_out` - клиент вышел;
- `booking_created` - клиент создал бронирование.

Путь событий:

```text
workplace events
  -> Kafka topic coworkbooking.workplace_events
  -> оконная агрегация
  -> ClickHouse
  -> dashboard / Grafana / Cube.js
```

## 3. Что запускается на защите

Главная команда:

```powershell
cd C:\Users\e_vla\Desktop\Руденкова\ПРОЕКТ
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

Она делает все основное:

1. Запускает Docker-сервисы: MinIO, Kafka, Zookeeper, ClickHouse.
2. Запускает Python pipeline внутри Docker-контейнера Airflow.
3. Создает Parquet-файлы в Bronze/Silver/Gold слоях.
4. Создает отчеты качества данных.
5. Создает lineage-файл.
6. Создает признаки клиентов для Feature Store.
7. Генерирует события рабочих мест.
8. Публикует события в Kafka.
9. Загружает агрегаты в ClickHouse.
10. Создает HTML dashboard.

Если в конце написано:

```text
LOCAL DEMO PASS
```

значит демонстрационный сценарий прошел успешно.

## 4. Основные технологии

Этот раздел нужен, чтобы ты мог объяснить преподавателю не только названия сервисов, но и их смысл. Важно говорить так: “этот сервис нужен не просто потому, что он есть в задании, а потому что он закрывает конкретную задачу платформы данных”.

Короткая карта сервисов:

| Сервис | Простыми словами | Зачем нужен в нашем проекте |
| --- | --- | --- |
| Docker Compose | Запускает много сервисов одной командой | Чтобы вся платформа работала локально на ноутбуке |
| MinIO / S3 | Хранилище файлов | Чтобы хранить слои Data Lake: Bronze, Silver, Gold |
| Kafka | Очередь/шина событий | Чтобы передавать события бронирования почти в реальном времени |
| Zookeeper | Служебный сервис для Kafka | Чтобы Kafka корректно запускалась в выбранной версии |
| Airflow / Prefect | Планировщик пайплайнов | Чтобы запускать загрузку, проверки и обработку данных по шагам |
| Great Expectations | Проверка качества данных | Чтобы находить дубликаты, пустые поля и неверные значения |
| Spark | Движок обработки больших данных | Чтобы преобразовывать данные между слоями Lakehouse |
| Iceberg / Delta Lake | Формат lakehouse-таблиц | Чтобы данные в Data Lake были похожи на надежные таблицы БД |
| Feast | Feature Store | Чтобы хранить признаки для ML-моделей |
| ClickHouse | Быстрая аналитическая база | Чтобы быстро строить дашборды и агрегаты |
| Grafana | Дашборды и мониторинг | Чтобы показывать метрики в реальном времени |
| Cube.js | Semantic Layer | Чтобы бизнес-метрики были описаны в одном месте |
| React / Streamlit | Веб-интерфейс аналитики | Чтобы встроить графики в пользовательское приложение |
| Terraform | Infrastructure as Code | Чтобы описать облачную инфраструктуру кодом |
| GitLab CI/CD | Автоматизация проверок и деплоя | Чтобы тесты, качество данных и сборка запускались автоматически |

### Docker Compose

Docker Compose - это способ запустить несколько сервисов одной командой. Без него пришлось бы отдельно ставить Kafka, ClickHouse, MinIO и другие инструменты на Windows. Это долго, неудобно и может ломаться из-за разных версий.

В проекте Docker Compose нужен для локальной защиты. Он делает так, что проект можно показать без настоящего облака:

```text
docker compose up
  -> запускает MinIO
  -> запускает Kafka
  -> запускает ClickHouse
  -> запускает вспомогательные сервисы
```

Как объяснить на защите:

> Docker Compose используется как локальный стенд. Он имитирует облачную data platform, но запускается на моем компьютере.

### MinIO / S3

S3 - это объектное хранилище. Если говорить проще, это большое файловое хранилище для данных. В облаке это мог бы быть Yandex Object Storage или AWS S3. Локально вместо него используется MinIO, потому что он работает почти так же, но запускается в Docker.

MinIO нужен для Data Lake. Data Lake - это место, где лежат файлы данных:

- сырые данные после загрузки;
- очищенные данные;
- аналитические витрины;
- parquet-файлы;
- результаты пайплайнов.

В проекте MinIO показывает, как данные попадают в слои:

```text
Bronze -> Silver -> Gold
```

Как объяснить на защите:

> MinIO здесь заменяет облачный S3. Мы используем его как Data Lake, куда пайплайн складывает данные в формате Parquet.

### Kafka

Kafka - это сервис для потоковых событий. Его можно представить как надежную очередь сообщений.

Обычный пример из проекта:

1. Клиент забронировал рабочее место.
2. Система создала событие `booking_created`.
3. Событие отправилось в Kafka.
4. Другой сервис прочитал событие и посчитал агрегаты для дашборда.

В проекте topic называется:

```text
coworkbooking.workplace_events
```

Kafka нужна там, где данные появляются постоянно, а не один раз в день. Например:

- клиент вошел в коворкинг;
- клиент вышел из коворкинга;
- рабочее место стало занято;
- появилось новое бронирование;
- бронирование отменили.

Без Kafka мы могли бы читать только готовые CSV-файлы. С Kafka появляется real-time часть проекта: события летят в поток, а система может сразу обновлять метрики.

Как объяснить на защите:

> Kafka нужна для real-time сценария. Она принимает события из симулятора и передает их дальше на обработку, чтобы можно было строить оперативные метрики по загрузке коворкинга.

### Zookeeper

Zookeeper - это служебный компонент, который нужен Kafka в используемой версии. Его не нужно показывать как отдельную бизнес-часть проекта.

Проще всего объяснять так:

> Zookeeper - техническая зависимость Kafka. Он помогает Kafka хранить служебное состояние и корректно работать в локальном стенде.

Если преподаватель не спрашивает отдельно про Zookeeper, можно не углубляться.

### Airflow / Prefect

Airflow и Prefect - это оркестраторы. Оркестратор - это сервис, который запускает пайплайн не хаотично, а по понятным шагам.

Например, загрузку данных нельзя делать в случайном порядке. Сначала нужно получить данные, потом проверить качество, потом сохранить в Data Lake, потом построить витрины.

Логика пайплайна:

```text
extract
  -> validate
  -> write bronze
  -> transform silver
  -> build gold
  -> register lineage
  -> send alert if failed
```

В проекте есть настоящий DAG, который показывает, как загружать данные из CSV и API. Для локального демо контейнер Airflow также используется как удобная Python-среда с `pandas` и `pyarrow`.

Как объяснить на защите:

> Airflow нужен, чтобы пайплайн был управляемым: каждый шаг виден, ошибки логируются, есть retry и можно понять, где именно произошел сбой.

### Great Expectations

Great Expectations - это инструмент проверки качества данных. Он отвечает на вопрос: “можно ли доверять данным, которые пришли в систему?”

Например, для бронирований плохо, если:

- два бронирования имеют один и тот же `booking_id`;
- у бронирования нет `client_id`;
- стоимость отрицательная;
- длительность бронирования равна нулю;
- статус имеет неизвестное значение.

В проекте проверяются:

- уникальность `booking_id`;
- наличие `client_id`;
- корректность `status`;
- неотрицательная стоимость бронирования;
- положительная длительность бронирования.

Если проверка падает, пайплайн должен показать ошибку. Это важно, потому что плохие данные не должны незаметно попасть в аналитику.

Как объяснить на защите:

> Great Expectations выполняет роль автоматического контролера качества. Перед тем как данные пойдут дальше, система проверяет, что они не сломают аналитику.

### Spark

Spark - это движок для обработки данных. В большом проекте он нужен, когда данных много и обычного Python уже недостаточно.

В этом учебном проекте Spark показывает архитектурный подход:

- взять сырые данные;
- очистить их;
- соединить таблицы;
- посчитать агрегаты;
- подготовить Gold-слой для аналитики и ML.

Пример:

```text
bookings + clients + workplaces
  -> очищенные таблицы
  -> выручка по сегментам
  -> загрузка рабочих зон
  -> признаки клиентов
```

Как объяснить на защите:

> Spark отвечает за преобразование данных между слоями Lakehouse. Даже если данных в демо немного, архитектура показывает, как это масштабируется на большие объемы.

### Iceberg / Delta Lake

Обычный Data Lake - это просто набор файлов. Проблема в том, что с файлами сложнее работать как с нормальными таблицами: нужны версии, надежные обновления, контроль схемы.

Iceberg и Delta Lake решают эту проблему. Они превращают файлы в Data Lake в более управляемые lakehouse-таблицы.

Зачем это нужно:

- чтобы таблицы можно было безопасно обновлять;
- чтобы схема данных была понятной;
- чтобы аналитика работала стабильнее;
- чтобы была поддержка ACID-подхода.

В проекте это относится к слоям:

- Bronze - сырые данные;
- Silver - очищенные данные;
- Gold - данные для отчетов, ML и дашбордов.

Как объяснить на защите:

> Iceberg или Delta Lake нужны, чтобы Data Lake был не просто папкой с файлами, а надежным Lakehouse-слоем с таблицами.

### ClickHouse

ClickHouse - это аналитическая база данных. Она хорошо подходит для быстрых запросов по большим таблицам, особенно когда нужно строить графики и агрегаты.

В проекте ClickHouse хранит таблицы:

- `coworkbooking.space_occupancy_5m`;
- `coworkbooking.booking_revenue`.

Почему не хранить все только в CSV или Parquet? Потому что дашборду нужно быстро отвечать на вопросы:

- сколько людей было в зоне за последние 5 минут;
- какая загрузка рабочих мест;
- какая выручка по сегментам клиентов;
- какие зоны используются чаще всего.

Как объяснить на защите:

> ClickHouse используется как быстрый аналитический слой. В него попадают готовые агрегаты, которые удобно показывать на дашборде.

### Grafana

Grafana - это инструмент для визуализации и мониторинга. Она подключается к источнику данных, например к ClickHouse, и строит графики.

В проекте Grafana нужна для real-time dashboard:

- загрузка коворкинга;
- количество людей по зонам;
- события за последние минуты;
- состояние пайплайна или метрик.

Как объяснить на защите:

> Grafana показывает результат потоковой обработки в понятном виде. Вместо чтения таблиц преподаватель видит график или метрику.

### Feast

Feast - это Feature Store. Feature Store нужен для ML-признаков.

Признак - это подготовленная характеристика объекта. Например, для клиента:

- сколько бронирований он сделал;
- какая у него средняя стоимость бронирования;
- как часто он отменяет бронирования;
- насколько недавно он был активен.

В проекте признаки клиента:

- `avg_booking_value_30d`;
- `bookings_30d`;
- `cancelled_booking_rate_30d`;
- `total_revenue_30d`.

Зачем нужен Feast:

- чтобы признаки были описаны в одном месте;
- чтобы ML-модель и аналитика использовали одинаковые расчеты;
- чтобы признаки можно было получать для обучения модели.

Как объяснить на защите:

> Feast нужен, чтобы Gold-данные можно было использовать для машинного обучения. Он хранит описание признаков и делает их доступными для обучения модели.

### Cube.js

Cube.js - это semantic layer, то есть слой бизнес-смысла поверх таблиц.

Без semantic layer аналитик или интерфейс должен знать SQL и структуру таблиц. Например, нужно помнить, где лежит выручка, как считать средний чек, как соединять таблицы.

С Cube.js можно описать метрики один раз:

- `ClientCount`;
- `TotalRevenue`;
- `AvgBookingValue`;
- `SpaceUtilization`.

После этого интерфейс запрашивает не сложный SQL, а понятные бизнес-метрики.

Как объяснить на защите:

> Cube.js отделяет бизнес-логику от физического хранения данных. Если формула выручки изменится, ее можно поменять в одном месте, а не во всех графиках.

### React UI / Streamlit

React UI или Streamlit - это пользовательский интерфейс. Он нужен, чтобы показать аналитику не в виде файлов и таблиц, а как нормальное приложение.

В проекте интерфейс показывает embedded analytics:

- графики по выручке;
- метрики по бронированиям;
- drill-down;
- переход от общего уровня к деталям.

Пример drill-down:

```text
коворкинг
  -> зона
  -> рабочее место
  -> бронирование
```

Как объяснить на защите:

> Интерфейс показывает, как аналитика может быть встроена в бизнес-приложение CoworkBooking.

### Terraform

Terraform - это инструмент Infrastructure as Code. Он описывает инфраструктуру кодом.

То есть вместо ручного создания ресурсов в облаке можно написать конфигурации:

- Object Storage;
- Managed Kafka;
- Compute VM;
- сеть и subnet.

В защите важно сказать, что проект работает локально, но Terraform показывает, как такую же основу можно развернуть в облаке.

Как объяснить на защите:

> Terraform закрывает часть задания про Infrastructure as Code. Локально я запускаю стенд через Docker, а Terraform-конфигурации показывают cloud-ready вариант инфраструктуры.

### GitLab CI/CD

CI/CD - это автоматизация проверки и доставки проекта.

Если говорить просто, это сценарий, который сам выполняет технические проверки:

1. Запускает тесты.
2. Проверяет качество данных.
3. Собирает Docker images.
4. Деплоит проект на тестовый стенд.

В проекте CI/CD описан в `.gitlab-ci.yml`.

Как объяснить на защите:

> GitLab CI/CD нужен, чтобы изменения не попадали в проект без проверок. Это показывает, что платформа не только запускается вручную, но и готова к автоматизированному сопровождению.

### Telegram / Slack alerts

Оповещения нужны, чтобы человек узнал о проблеме сразу, а не случайно через несколько дней.

В проекте это относится к падениям DAG и ошибкам пайплайнов:

- не загрузились данные;
- не прошла проверка качества;
- не записался файл;
- не обновилась аналитическая таблица.

Как объяснить на защите:

> Alerts нужны для observability. Если пайплайн падает, система должна сообщить об этом в Telegram или Slack, чтобы проблему быстро заметили.

## 5. Объяснение корневых файлов

### `.env`

Файл с переменными окружения для локального запуска.

Там лежат настройки:

- имя проекта;
- доступ к MinIO;
- bucket;
- Kafka bootstrap servers;
- ClickHouse host;
- Cube.js настройки.

Важно: `.env` обычно не коммитят в Git, потому что там могут быть секреты. В учебном локальном проекте он нужен для запуска.

### `.env.example`

Шаблон `.env`.

Если `.env` удален, его можно восстановить:

```powershell
Copy-Item .env.example .env
```

### `.gitignore`

Файл говорит Git, что не нужно добавлять в репозиторий:

- `.env`;
- временные runtime-данные;
- `__pycache__`;
- Terraform state;
- node_modules и прочие временные файлы.

### `.gitlab-ci.yml`

Описание GitLab CI/CD pipeline.

Стадии:

- `test`;
- `data_quality`;
- `build`;
- `deploy`.

### `docker-compose.yml`

Большой production-like стенд.

Он описывает:

- MinIO;
- Kafka;
- Postgres;
- Airflow;
- ClickHouse;
- Grafana;
- Cube.js;
- Booking API;
- React UI.

Этот файл показывает, как могла бы запускаться вся платформа целиком.

### `docker-compose.local.yml`

Компактный стенд для защиты.

Он запускает только критичные сервисы:

- MinIO;
- Zookeeper;
- Kafka;
- ClickHouse.

Именно этот файл использует `scripts/run_local_demo.ps1`.

### `README.md`

Короткая главная инструкция проекта. Это первый файл, который удобно открыть преподавателю.

## 6. Папка `data`

Папка `data` хранит входные данные, домены и результаты локального запуска.

### `data/domains.yaml`

Описывает Data Mesh домены:

- `booking_operations`;
- `space_operations`;
- `customer_engagement`.

Это ответ на требование “определить домены данных”.

### `data/samples/bookings.csv`

Тестовая выгрузка бронирований.

Основные поля:

- `booking_id` - идентификатор бронирования;
- `client_id` - клиент;
- `space_id` - площадка коворкинга;
- `workplace_id` - рабочее место;
- `workplace_type` - тип места;
- `status` - статус бронирования;
- `hours` - длительность;
- `total_price` - итоговая стоимость.

### `data/samples/clients.csv`

Справочник клиентов.

Поля:

- `client_id`;
- `segment`;
- `city`;
- `registered_at`.

Сегменты нужны для аналитики: freelancer, startup, student, corporate.

### `data/samples/workplaces.csv`

Справочник рабочих мест.

Поля:

- `workplace_id`;
- `space_id`;
- `zone`;
- `workplace_type`;
- `capacity`;
- `price_per_hour`.

### `data/runtime`

Это результаты локального запуска. Появляются после `run_local_demo.ps1`.

#### `data/runtime/lakehouse/bronze`

Bronze слой - сырые данные, максимально близкие к источнику.

Внутри:

- `booking_operations/bookings/.../bookings.parquet`;
- `booking_operations/booking_events/.../events.parquet`.

#### `data/runtime/lakehouse/silver`

Silver слой - очищенные данные.

Файл:

- `booking_operations/bookings.parquet`.

Здесь уже убраны дубли и проверена корректность значений.

#### `data/runtime/lakehouse/gold`

Gold слой - данные, готовые для аналитики и ML.

Файл:

- `booking_operations/client_features.parquet`.

#### `data/runtime/reports`

Отчеты локального запуска.

Файлы:

- `LOCAL_DEMO_SUMMARY.md` - краткий итог прогона;
- `quality_bookings.json` - отчет качества по бронированиям;
- `quality_booking_events.json` - отчет качества по событиям бронирований.

#### `data/runtime/lineage/lineage.json`

Lineage показывает, откуда пришли данные и во что они превратились.

Например:

```text
bookings.csv -> bronze -> silver -> gold client_features
```

#### `data/runtime/streaming/events`

События для Kafka:

- `workplace_events.jsonl` - полный JSONL с event_id;
- `workplace_events.kafka.jsonl` - версия для отправки в Kafka.

#### `data/runtime/streaming/aggregates`

Агрегаты потоковых событий:

- `space_occupancy_5m.parquet`;
- `space_occupancy_5m_clickhouse.csv`.

Они показывают загрузку зон коворкинга в 5-минутных окнах.

#### `data/runtime/dashboard/index.html`

Локальный HTML dashboard. Его можно открыть двойным кликом.

Показывает:

- качество данных;
- количество feature rows;
- количество streaming windows;
- выручку по сегментам;
- загрузку зон коворкинга.

### `data/feature_store/client_features.parquet`

Файл признаков для Feature Store.

Его можно объяснить так:

> Это готовая таблица признаков клиентов для аналитики или ML-модели.

## 7. Папка `data-products`

### `data-products/booking_operations/data_product.yaml`

Контракт Data Product.

Там описано:

- название продукта;
- домен;
- владелец;
- интерфейсы;
- схема;
- SLA;
- метрики качества.

Это ответ на требование про Data Mesh Data Product.

### `data-products/booking_operations/README.md`

Человеческое описание Data Product: что публикуется, где лежит, какие гарантии качества.

## 8. Папка `docs`

Документация для защиты.

### `docs/PROJECT_EXPLAINED.md`

Это текущий файл. Его задача - объяснить весь проект.

### `docs/PROJECT_MAP.md`

Короткая карта проекта по папкам. Удобно открыть во время защиты.

### `docs/DEFENSE_NOTES.md`

Заметки, что говорить преподавателю.

### `docs/LOCAL_DEMO_RUNBOOK.md`

Runbook для запуска:

- основная команда;
- что показать;
- проверочные команды;
- как остановить стенд.

### `docs/demo_script.md`

Сценарий защиты по шагам.

### `docs/architecture.md`

Архитектурная схема Mermaid и объяснение потока данных.

### `docs/data_domains.md`

Описание доменов Data Mesh.

### `docs/lineage.md`

Описание lineage: какие источники во что превращаются.

### `docs/monitoring.md`

Описание observability:

- retry;
- alerts;
- quality reports;
- lineage;
- streaming metrics;
- CI/CD visibility.

### `docs/deployment.md`

Инструкция по локальному и облачному развертыванию.

### `docs/adr/ADR-001-cloud-lakehouse-yandex.md`

ADR - Architecture Decision Record.

Это документ, который фиксирует архитектурное решение:

- почему Yandex Cloud;
- почему S3-compatible Object Storage;
- почему Kafka;
- почему VM + Docker Compose.

## 9. Папка `infra`

Terraform-инфраструктура.

### `infra/terraform/yandex/versions.tf`

Описывает версию Terraform и провайдера Yandex Cloud.

### `infra/terraform/yandex/variables.tf`

Описывает входные переменные:

- `cloud_id`;
- `folder_id`;
- `zone`;
- `project`;
- `ssh_public_key`;
- `service_account_id`;
- `kafka_user_password`.

### `infra/terraform/yandex/main.tf`

Главный Terraform файл.

Создает:

- VPC network;
- subnet;
- Object Storage bucket;
- static access key;
- Managed Kafka cluster;
- Compute VM;
- cloud-init для запуска Docker/Airflow.

### `infra/terraform/yandex/outputs.tf`

Выводит полезные значения после `terraform apply`:

- bucket name;
- Kafka cluster id;
- публичный IP VM;
- Airflow URL.

### `infra/terraform/yandex/terraform.tfvars.example`

Пример файла с реальными значениями переменных.

Его надо скопировать в `terraform.tfvars` и заполнить перед облачным запуском.

### `infra/terraform/yandex/cloud-init-airflow.yaml.tftpl`

Шаблон cloud-init.

Когда создается VM, cloud-init:

- обновляет пакеты;
- ставит Docker;
- клонирует репозиторий;
- запускает Docker Compose.

## 10. Папка `orchestration`

Оркестрация batch-процессов через Airflow.

### `orchestration/airflow/Dockerfile`

Образ Airflow с дополнительными Python-библиотеками:

- pandas;
- pyarrow;
- boto3;
- requests;
- Great Expectations;
- OpenLineage provider.

### `orchestration/airflow/requirements.txt`

Список Python-зависимостей для Airflow.

### `orchestration/airflow/dags/raw_ingestion_dag.py`

Главный Airflow DAG.

Что делает:

1. Загружает `bookings.csv`.
2. Проверяет качество бронирований.
3. Забирает события из Booking API.
4. Проверяет качество событий.
5. Пишет Parquet в S3/MinIO.
6. Публикует lineage JSON.
7. Имеет retry и callback для Telegram/Slack alerts.

## 11. Папка `great_expectations`

Проверки качества данных.

### `great_expectations/great_expectations.yml`

Конфигурация Great Expectations.

### `great_expectations/expectations/booking_operations_bookings.json`

Expectation suite.

Проверяет:

- `booking_id` уникален;
- `client_id` не пустой;
- `total_price >= 0`;
- `hours > 0`;
- `status` входит в допустимый набор.

## 12. Папка `lakehouse`

Логика Lakehouse.

### `lakehouse/spark/jobs/bronze_to_silver.py`

Spark job для перехода Bronze -> Silver.

Он:

- читает сырые бронирования;
- удаляет дубли;
- фильтрует некорректные цены и длительность;
- приводит даты;
- записывает Iceberg table `lakehouse.silver.bookings`.

### `lakehouse/spark/jobs/silver_to_gold_features.py`

Spark job для перехода Silver -> Gold.

Он считает признаки:

- средний чек;
- количество бронирований;
- долю отмен;
- суммарную выручку.

### `lakehouse/spark/lib/transformations.py`

Чистая Python-функция `build_client_features`.

Она нужна, чтобы бизнес-логику можно было тестировать отдельно от Spark.

## 13. Папка `feature_store`

Feature Store на Feast.

### `feature_store/feast/feature_store.yaml`

Конфиг Feast.

Проект называется:

```text
coworkbooking_platform
```

### `feature_store/feast/features.py`

Описание entity и FeatureView.

Entity:

- `client`.

FeatureView:

- `client_booking_features`.

### `feature_store/feast/materialize_features.py`

Скрипт для materialize признаков в online store.

### `feature_store/feast/data/local_registry.json`

Локальный registry artifact, который создается demo-прогоном.

## 14. Папка `streaming`

Потоковый контур.

### `streaming/event_simulator/producer.py`

Генератор событий.

Создает события:

- `check_in`;
- `check_out`;
- `booking_created`.

Пишет их в Kafka topic:

```text
coworkbooking.workplace_events
```

### `streaming/event_simulator/requirements.txt`

Зависимости генератора событий:

- `confluent-kafka`;
- `faker`.

### `streaming/flink/workplace_event_window_job.py`

Flink job.

Он читает Kafka topic и считает загрузку коворкинга в скользящих окнах.

Окно:

- размер 5 минут;
- шаг 1 минута.

### `streaming/clickhouse/schema.sql`

SQL-схема ClickHouse.

Создает:

- database `coworkbooking`;
- table `space_occupancy_5m`;
- table `booking_revenue`.

### `streaming/grafana/provisioning/datasources/clickhouse.yml`

Datasource для Grafana.

Подключает Grafana к ClickHouse.

### `streaming/grafana/provisioning/dashboards/dashboards.yml`

Описывает, где Grafana должна искать dashboard JSON.

### `streaming/grafana/provisioning/dashboards/realtime-campus.json`

Dashboard для загрузки коворкинга.

Название файла осталось техническим, но внутри dashboard уже про CoworkBooking. Если преподаватель спросит, можно сказать, что это provisioning-файл Grafana, имя файла не влияет на работу.

## 15. Папка `semantic`

Semantic Layer и embedded analytics.

### `semantic/cube/Dockerfile`

Dockerfile для Cube.js.

### `semantic/cube/package.json`

Node.js зависимости Cube.js.

### `semantic/cube/schema/BookingOperations.js`

Cube.js schema для бронирований.

Метрики:

- `ClientCount`;
- `TotalRevenue`;
- `AvgBookingValue`;
- `BookingCount`.

Измерения:

- `segment`;
- `city`;
- `spaceId`;
- `workplaceType`;
- `status`;
- `eventDate`.

### `semantic/cube/schema/SpaceUtilization.js`

Cube.js schema для загрузки зон.

Метрики:

- `SpaceUtilization`;
- `EventCount`.

Измерения:

- `spaceId`;
- `zone`;
- `windowStart`.

### `semantic/web/Dockerfile`

Dockerfile для React UI.

### `semantic/web/package.json`

Зависимости frontend:

- React;
- Vite;
- Recharts;
- Cube.js client;
- lucide-react.

### `semantic/web/index.html`

HTML-точка входа React-приложения.

### `semantic/web/src/App.jsx`

Главный React-компонент.

Он строит график:

- выручка по сегментам;
- количество клиентов;
- drill-down от сегмента к площадке.

### `semantic/web/src/styles.css`

Стили React-интерфейса.

## 16. Папка `services`

Сервис-источник данных.

### `services/lms_api/Dockerfile`

Dockerfile для API-сервиса.

Название папки историческое, но сам сервис внутри уже `CoworkBooking API`.

### `services/lms_api/app.py`

FastAPI приложение.

Endpoint:

```text
/booking-events
```

Возвращает события бронирований:

- `booking_confirmed`;
- `booking_cancelled`.

## 17. Папка `scripts`

Скрипты запуска и проверки.

### `scripts/run_local_demo.ps1`

Главный скрипт защиты.

Он:

- запускает Docker Compose;
- запускает Python pipeline в контейнере;
- создает Kafka topic;
- отправляет события в Kafka;
- грузит CSV в ClickHouse;
- выводит `LOCAL DEMO PASS`.

### `scripts/stop_local_demo.ps1`

Останавливает локальный demo-стенд.

### `scripts/local_full_demo.py`

Основной локальный pipeline.

Он не заменяет Airflow DAG, а нужен для надежной демонстрации на защите.

Создает:

- Bronze/Silver/Gold Parquet;
- quality reports;
- lineage;
- feature store files;
- streaming events;
- ClickHouse CSV;
- HTML dashboard.

### `scripts/run_data_quality.py`

Простой скрипт для CI/CD.

Проверяет `data/samples/bookings.csv`.

### `scripts/deploy_test_stand.sh`

Скрипт деплоя на тестовый стенд по SSH.

Используется в `.gitlab-ci.yml`.

## 18. Папка `presentation`

Материалы для защиты.

### `presentation/coworkbooking_data_platform_defense.pptx`

Презентация проекта.

### `presentation/previews`

PNG-превью слайдов.

Они нужны, чтобы быстро посмотреть, что в презентации нет проблем с текстом.

## 19. Папка `tests`

Тесты.

### `tests/test_transformations.py`

Unit-test для функции `build_client_features`.

Он проверяет:

- средний чек;
- количество бронирований;
- долю отмен.

## 20. Как объяснить проект преподавателю за 2 минуты

Можно сказать так:

> В прошлом курсе я делал систему CoworkBooking для бронирования рабочих мест в коворкинге. В этом проекте я построил вокруг нее платформу данных. Я выделил домены booking_operations, space_operations и customer_engagement. Для инфраструктуры описал Terraform в Yandex Cloud: Object Storage, Managed Kafka и VM. Для batch-обработки сделал Airflow DAG, который загружает бронирования из CSV и API, проверяет качество данных и пишет Parquet. Дальше данные проходят Bronze, Silver и Gold слои Lakehouse. В Gold формируются признаки клиентов, которые регистрируются в Feast. Для real-time части генерируются события рабочих мест, они публикуются в Kafka, агрегируются по окнам и сохраняются в ClickHouse. Поверх ClickHouse описан semantic layer на Cube.js и React-интерфейс с drill-down аналитикой. Все это покрыто CI/CD pipeline и локально запускается одной командой.

## 21. Что показывать по шагам

1. Открыть `README.md`.
2. Открыть `docs/PROJECT_MAP.md`.
3. Показать `data/domains.yaml`.
4. Показать `data-products/booking_operations/data_product.yaml`.
5. Показать Terraform: `infra/terraform/yandex/main.tf`.
6. Показать Airflow DAG: `orchestration/airflow/dags/raw_ingestion_dag.py`.
7. Запустить:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

8. Открыть `data/runtime/reports/LOCAL_DEMO_SUMMARY.md`.
9. Открыть `data/runtime/dashboard/index.html`.
10. Показать Kafka offset:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic coworkbooking.workplace_events
```

11. Показать ClickHouse:

```powershell
docker compose -p coworkbooking-demo -f docker-compose.local.yml exec -T clickhouse clickhouse-client --query "SELECT segment, round(sum(total_price), 0), countDistinct(client_id) FROM coworkbooking.booking_revenue GROUP BY segment ORDER BY segment"
```

12. Показать презентацию.

## 22. Что важно запомнить

- `Bronze` - сырые данные.
- `Silver` - очищенные данные.
- `Gold` - данные для аналитики и ML.
- `Kafka` - поток событий.
- `ClickHouse` - быстрая аналитическая база.
- `Feast` - Feature Store.
- `Cube.js` - semantic layer.
- `Terraform` - инфраструктура как код.
- `Airflow` - оркестрация batch pipeline.
- `Great Expectations` - качество данных.
- `Lineage` - откуда пришли данные и куда пошли дальше.

## 23. Если что-то не запускается

Проверить Docker Desktop:

```powershell
docker version
```

Если Docker не Running, открыть Docker Desktop и дождаться запуска.

Остановить старый стенд:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local_demo.ps1
```

Запустить заново:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

## 24. Главная мысль проекта

Этот проект показывает не просто набор технологий, а полный data lifecycle:

```text
бизнес-система CoworkBooking
  -> источники данных
  -> качество
  -> Lakehouse
  -> Feature Store
  -> real-time analytics
  -> semantic layer
  -> dashboard
  -> CI/CD
```

То есть это демонстрация того, как обычную информационную систему можно развить до современной платформы данных.
