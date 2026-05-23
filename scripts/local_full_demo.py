from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lakehouse.spark.lib.transformations import build_client_features


RUNTIME = ROOT / "data" / "runtime"
LAKEHOUSE = RUNTIME / "lakehouse"
REPORTS = RUNTIME / "reports"
LINEAGE = RUNTIME / "lineage"
STREAMING = RUNTIME / "streaming"
DASHBOARD = RUNTIME / "dashboard"
FEATURE_DATA = ROOT / "data" / "feature_store"
LOCAL_TZ = timezone(timedelta(hours=3), "MSK")


def local_run_time() -> str:
    return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S MSK")


def ensure_dirs() -> None:
    for path in [LAKEHOUSE, REPORTS, LINEAGE, STREAMING, DASHBOARD, FEATURE_DATA]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_parquet(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def quality_check(name: str, checks: list[tuple[str, bool, str]]) -> dict:
    normalized = [(label, bool(ok), details) for label, ok, details in checks]
    passed = sum(1 for _, ok, _ in normalized if ok)
    result = {
        "suite": name,
        "success": passed == len(checks),
        "statistics": {"evaluated": len(checks), "successful": passed, "unsuccessful": len(checks) - passed},
        "results": [{"expectation": label, "success": ok, "details": details} for label, ok, details in normalized],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    if not result["success"]:
        raise ValueError(f"Data quality failed for {name}: {result}")
    return result


def build_raw_layer(dt: str) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    bookings = pd.read_csv(ROOT / "data" / "samples" / "bookings.csv")
    booking_events = pd.DataFrame(
        [
            {
                "event_id": "E2001",
                "booking_id": "B001",
                "client_id": "C001",
                "space_id": "SP-01",
                "event_type": "booking_confirmed",
                "event_ts": "2026-05-21T08:55:00Z",
                "amount": 1350,
            },
            {
                "event_id": "E2002",
                "booking_id": "B002",
                "client_id": "C002",
                "space_id": "SP-01",
                "event_type": "booking_confirmed",
                "event_ts": "2026-05-21T09:05:00Z",
                "amount": 2400,
            },
            {
                "event_id": "E2003",
                "booking_id": "B003",
                "client_id": "C003",
                "space_id": "SP-02",
                "event_type": "booking_cancelled",
                "event_ts": "2026-05-21T09:20:00Z",
                "amount": 700,
            },
        ]
    )

    booking_checks = quality_check(
        "booking_operations_bookings",
        [
            ("booking_id is unique", not bookings["booking_id"].duplicated().any(), "No duplicated booking_id values"),
            ("client_id is not null", bookings["client_id"].notna().all(), "All rows contain client_id"),
            ("total_price is non-negative", (bookings["total_price"] >= 0).all(), "Prices are valid"),
            ("hours is positive", (bookings["hours"] > 0).all(), "Booking duration is positive"),
            ("status is known", set(bookings["status"]).issubset({"ACTIVE", "CANCELLED", "COMPLETED"}), "Statuses match contract"),
        ],
    )
    event_checks = quality_check(
        "booking_operations_events",
        [
            ("event_id is unique", not booking_events["event_id"].duplicated().any(), "No duplicated event_id values"),
            ("amount is non-negative", (booking_events["amount"] >= 0).all(), "Amounts are valid"),
            ("event_type is known", set(booking_events["event_type"]).issubset({"booking_confirmed", "booking_cancelled"}), "Event types match contract"),
        ],
    )
    write_json(REPORTS / "quality_bookings.json", booking_checks)
    write_json(REPORTS / "quality_booking_events.json", event_checks)

    booking_path = write_parquet(bookings, LAKEHOUSE / "bronze" / "booking_operations" / "bookings" / f"dt={dt}" / "bookings.parquet")
    event_path = write_parquet(booking_events, LAKEHOUSE / "bronze" / "booking_operations" / "booking_events" / f"dt={dt}" / "events.parquet")
    return bookings, booking_events, [{"source": "data/samples/bookings.csv", "target": str(booking_path)}, {"source": "Booking API /events", "target": str(event_path)}]


def build_lakehouse(bookings: pd.DataFrame, dt: str) -> tuple[pd.DataFrame, list[dict]]:
    clients = pd.read_csv(ROOT / "data" / "samples" / "clients.csv")
    silver_bookings = bookings.drop_duplicates(["booking_id"]).copy()
    silver_bookings = silver_bookings[silver_bookings["total_price"] >= 0].copy()
    silver_bookings["created_at"] = pd.to_datetime(silver_bookings["created_at"], utc=True)
    silver_bookings["start_ts"] = pd.to_datetime(silver_bookings["start_ts"], utc=True)
    silver_bookings["end_ts"] = pd.to_datetime(silver_bookings["end_ts"], utc=True)
    silver_path = write_parquet(silver_bookings, LAKEHOUSE / "silver" / "booking_operations" / "bookings.parquet")

    features = build_client_features(silver_bookings, clients)
    features["event_timestamp"] = pd.Timestamp("2026-05-21T00:00:00Z")
    gold_path = write_parquet(features, LAKEHOUSE / "gold" / "booking_operations" / "client_features.parquet")
    write_parquet(features, FEATURE_DATA / "client_features.parquet")

    booking_revenue = silver_bookings.merge(clients, on="client_id", how="left")
    booking_revenue["event_date"] = dt
    booking_revenue_csv = booking_revenue[
        ["client_id", "segment", "city", "space_id", "workplace_type", "status", "total_price", "hours", "event_date"]
    ]
    booking_revenue_csv.to_csv(RUNTIME / "booking_revenue_clickhouse.csv", index=False)

    registry = {
        "project": "coworkbooking_platform",
        "feature_view": "client_booking_features",
        "entity": "client",
        "features": ["segment", "city", "avg_booking_value_30d", "bookings_30d", "cancelled_booking_rate_30d", "total_revenue_30d"],
        "offline_path": str(FEATURE_DATA / "client_features.parquet"),
    }
    write_json(ROOT / "feature_store" / "feast" / "data" / "local_registry.json", registry)
    return features, [{"source": str(silver_path), "target": str(gold_path)}, {"source": str(gold_path), "target": str(FEATURE_DATA / "client_features.parquet")}]


def build_streaming_outputs() -> tuple[pd.DataFrame, list[dict]]:
    random.seed(42)
    start = datetime(2026, 5, 21, 9, 0, tzinfo=timezone.utc)
    workplaces = ["W-101", "MR-201", "W-301", "TEAM-1"]
    spaces = {"W-101": "SP-01", "MR-201": "SP-01", "W-301": "SP-02", "TEAM-1": "SP-02"}
    zones = {"W-101": "Open Space", "MR-201": "Meeting Zone", "W-301": "Quiet Zone", "TEAM-1": "Team Zone"}
    event_types = ["check_in", "check_out", "booking_created"]
    rows = []
    for i in range(180):
        workplace_id = random.choice(workplaces)
        rows.append(
            {
                "event_id": str(uuid4()),
                "client_id": f"C{random.randint(1, 80):03d}",
                "event_type": random.choices(event_types, weights=[0.48, 0.32, 0.20])[0],
                "space_id": spaces[workplace_id],
                "workplace_id": workplace_id,
                "zone": zones[workplace_id],
                "event_ts": (start + timedelta(seconds=i * 12)).isoformat().replace("+00:00", "Z"),
            }
        )
    events = pd.DataFrame(rows)
    events_path = STREAMING / "events" / "workplace_events.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    events[["client_id", "event_type", "space_id", "workplace_id", "zone", "event_ts"]].to_json(
        STREAMING / "events" / "workplace_events.kafka.jsonl",
        orient="records",
        lines=True,
        force_ascii=False,
    )

    events["ts"] = pd.to_datetime(events["event_ts"], utc=True)
    events["window_start"] = events["ts"].dt.floor("min")
    events["people_delta"] = events["event_type"].map({"check_in": 1, "check_out": -1}).fillna(0).astype(int)
    aggregates = (
        events.groupby(["window_start", "space_id", "zone"], as_index=False)
        .agg(people_delta=("people_delta", "sum"), event_count=("event_id", "count"))
        .sort_values(["window_start", "space_id", "zone"])
    )
    aggregates["window_end"] = aggregates["window_start"] + pd.Timedelta(minutes=5)
    aggregates = aggregates[["window_start", "window_end", "space_id", "zone", "people_delta", "event_count"]]

    write_parquet(aggregates, STREAMING / "aggregates" / "space_occupancy_5m.parquet")
    ch = aggregates.copy()
    ch["window_start"] = ch["window_start"].dt.strftime("%Y-%m-%d %H:%M:%S")
    ch["window_end"] = ch["window_end"].dt.strftime("%Y-%m-%d %H:%M:%S")
    ch.to_csv(STREAMING / "aggregates" / "space_occupancy_5m_clickhouse.csv", index=False)
    return aggregates, [{"source": str(events_path), "target": str(STREAMING / "aggregates" / "space_occupancy_5m.parquet")}]


def build_dashboard(features: pd.DataFrame, aggregates: pd.DataFrame) -> None:
    by_segment = (
        features.groupby("segment", as_index=False)
        .agg(avg_booking_value=("avg_booking_value_30d", "mean"), client_count=("client_id", "count"), revenue=("total_revenue_30d", "sum"))
        .sort_values("segment")
    )
    space = aggregates.groupby(["space_id", "zone"], as_index=False).agg(people_delta=("people_delta", "sum"), event_count=("event_count", "sum"))
    max_value = max(by_segment["avg_booking_value"].max(), 1)
    max_events = max(space["event_count"].max(), 1)
    segment_rows = "\n".join(
        f"<tr><td>{r.segment}</td><td>{r.client_count}</td><td>{r.avg_booking_value:.0f} руб.</td><td>{r.revenue:.0f} руб.</td><td><div class='bar' style='width:{r.avg_booking_value / max_value * 100:.0f}%'></div></td></tr>"
        for r in by_segment.itertuples()
    )
    space_rows = "\n".join(
        f"<tr><td>{r.space_id}</td><td>{r.zone}</td><td>{r.event_count}</td><td>{r.people_delta}</td><td><div class='bar green' style='width:{r.event_count / max_events * 100:.0f}%'></div></td></tr>"
        for r in space.itertuples()
    )
    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>CoworkBooking Data Platform Demo</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #102033; background: #f8fafc; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 36px; }}
    h1 {{ font-size: 34px; margin: 0 0 8px; }}
    h2 {{ margin-top: 34px; }}
    .sub {{ color: #516276; margin-bottom: 28px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
    .bar {{ height: 16px; background: #2563eb; border-radius: 4px; }}
    .green {{ background: #059669; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 28px 0; }}
    .metric {{ background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; }}
    .metric strong {{ display: block; font-size: 28px; }}
  </style>
</head>
<body>
<main>
  <h1>CoworkBooking Data Platform: локальный демо-прогон</h1>
  <p class="sub">Отчет сформирован {local_run_time()}. Данные прошли Raw -> Bronze -> Silver -> Gold -> Feature Store -> Streaming aggregates.</p>
  <section class="grid">
    <div class="metric"><span>Data quality</span><strong>PASS</strong></div>
    <div class="metric"><span>Client feature rows</span><strong>{len(features)}</strong></div>
    <div class="metric"><span>Streaming windows</span><strong>{len(aggregates)}</strong></div>
    <div class="metric"><span>Lineage facts</span><strong>saved</strong></div>
  </section>
  <h2>Booking analytics drill-down: client segment</h2>
  <table><tr><th>Segment</th><th>Clients</th><th>Avg booking value</th><th>Revenue</th><th>Bar</th></tr>{segment_rows}</table>
  <h2>Realtime coworking space utilization</h2>
  <table><tr><th>Space</th><th>Zone</th><th>Events</th><th>People delta</th><th>Bar</th></tr>{space_rows}</table>
</main>
</body>
</html>"""
    (DASHBOARD / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    dt = "2026-05-21"
    bookings, _, raw_lineage = build_raw_layer(dt)
    features, lakehouse_lineage = build_lakehouse(bookings, dt)
    aggregates, streaming_lineage = build_streaming_outputs()
    build_dashboard(features, aggregates)

    lineage = {
        "run_id": f"local-demo-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "domains": ["booking_operations", "space_operations", "customer_engagement"],
        "edges": raw_lineage + lakehouse_lineage + streaming_lineage,
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(LINEAGE / "lineage.json", lineage)

    summary = f"""# Local Demo Run

Status: PASS

Generated at: {local_run_time()}

- Bronze Parquet: `{LAKEHOUSE / "bronze"}`
- Silver Parquet: `{LAKEHOUSE / "silver"}`
- Gold feature table: `{LAKEHOUSE / "gold" / "booking_operations" / "client_features.parquet"}`
- Feast local registry: `{ROOT / "feature_store" / "feast" / "data" / "local_registry.json"}`
- Streaming events for Kafka: `{STREAMING / "events" / "workplace_events.kafka.jsonl"}`
- ClickHouse aggregate CSV: `{STREAMING / "aggregates" / "space_occupancy_5m_clickhouse.csv"}`
- Dashboard: `{DASHBOARD / "index.html"}`
- Lineage: `{LINEAGE / "lineage.json"}`
"""
    (REPORTS / "LOCAL_DEMO_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
