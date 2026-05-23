CREATE DATABASE IF NOT EXISTS coworkbooking;

CREATE TABLE IF NOT EXISTS coworkbooking.space_occupancy_5m
(
  window_start DateTime,
  window_end DateTime,
  space_id String,
  zone String,
  people_delta Int64,
  event_count UInt64
)
ENGINE = MergeTree
ORDER BY (window_start, space_id, zone);

CREATE TABLE IF NOT EXISTS coworkbooking.booking_revenue
(
  client_id String,
  segment String,
  city String,
  space_id String,
  workplace_type String,
  status String,
  total_price Float64,
  hours Float64,
  event_date Date
)
ENGINE = MergeTree
ORDER BY (segment, city, client_id, event_date);
