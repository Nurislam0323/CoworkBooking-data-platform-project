import os
from pyflink.table import EnvironmentSettings, TableEnvironment

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)

bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

t_env.execute_sql(f'''
CREATE TABLE workplace_events (
  event_id STRING,
  client_id STRING,
  event_type STRING,
  space_id STRING,
  workplace_id STRING,
  zone STRING,
  event_ts STRING,
  ts AS TO_TIMESTAMP_LTZ(UNIX_TIMESTAMP(event_ts, 'yyyy-MM-dd''T''HH:mm:ss.SSSX') * 1000, 3),
  WATERMARK FOR ts AS ts - INTERVAL '10' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'coworkbooking.workplace_events',
  'properties.bootstrap.servers' = '{bootstrap}',
  'scan.startup.mode' = 'latest-offset',
  'format' = 'json'
)
''')

t_env.execute_sql('''
CREATE TABLE space_occupancy_5m (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  space_id STRING,
  zone STRING,
  people_delta BIGINT,
  event_count BIGINT
) WITH (
  'connector' = 'jdbc',
  'url' = 'jdbc:clickhouse://clickhouse:8123/coworkbooking',
  'table-name' = 'space_occupancy_5m',
  'driver' = 'com.clickhouse.jdbc.ClickHouseDriver'
)
''')

t_env.execute_sql('''
INSERT INTO space_occupancy_5m
SELECT
  window_start,
  window_end,
  space_id,
  zone,
  SUM(CASE WHEN event_type = 'check_in' THEN 1 WHEN event_type = 'check_out' THEN -1 ELSE 0 END) AS people_delta,
  COUNT(*) AS event_count
FROM TABLE(
  HOP(TABLE workplace_events, DESCRIPTOR(ts), INTERVAL '1' MINUTE, INTERVAL '5' MINUTE)
)
GROUP BY window_start, window_end, space_id, zone
''').wait()
