import json
import os
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

import boto3
import pandas as pd
import requests
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException


S3_BUCKET = os.getenv("S3_BUCKET", "coworkbooking-lakehouse")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
DATA_DIR = Path(os.getenv("DATA_DIR", "/opt/airflow/data/samples"))


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
        region_name=os.getenv("AWS_REGION", "ru-central1"),
    )


def notify_failure(context):
    msg = f"Airflow DAG failed: {context['dag'].dag_id}.{context['task_instance'].task_id}"
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    if telegram_token and telegram_chat:
        requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            json={"chat_id": telegram_chat, "text": msg},
            timeout=10,
        )
    if slack_webhook:
        requests.post(slack_webhook, json={"text": msg}, timeout=10)


def write_parquet_to_s3(df: pd.DataFrame, key: str) -> str:
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    s3_client().put_object(Bucket=S3_BUCKET, Key=key, Body=buffer.getvalue())
    return f"s3://{S3_BUCKET}/{key}"


def validate_bookings(df: pd.DataFrame) -> None:
    errors = []
    if df["booking_id"].duplicated().any():
        errors.append("booking_id contains duplicates")
    if not (df["total_price"] >= 0).all():
        errors.append("total_price must be non-negative")
    if not (df["hours"] > 0).all():
        errors.append("hours must be positive")
    if not set(df["status"]).issubset({"ACTIVE", "CANCELLED", "COMPLETED"}):
        errors.append("unexpected booking status")
    if df[["client_id", "space_id", "workplace_id", "created_at"]].isna().any().any():
        errors.append("required fields contain nulls")
    if errors:
        raise AirflowFailException("; ".join(errors))


def validate_booking_events(df: pd.DataFrame) -> None:
    errors = []
    if df["event_id"].duplicated().any():
        errors.append("event_id contains duplicates")
    if not (df["amount"] >= 0).all():
        errors.append("amount must be non-negative")
    if not set(df["event_type"]).issubset({"booking_confirmed", "booking_cancelled"}):
        errors.append("unexpected booking event_type")
    if errors:
        raise AirflowFailException("; ".join(errors))


default_args = {
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "on_failure_callback": notify_failure,
}


@dag(
    dag_id="booking_operations_raw_ingestion",
    schedule="@daily",
    start_date=datetime(2026, 5, 1),
    catchup=False,
    default_args=default_args,
    tags=["data-mesh", "raw", "booking_operations", "coworkbooking"],
)
def booking_operations_raw_ingestion():
    @task
    def load_booking_csv() -> str:
        df = pd.read_csv(DATA_DIR / "bookings.csv")
        validate_bookings(df)
        dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return write_parquet_to_s3(df, f"bronze/booking_operations/bookings/dt={dt}/bookings.parquet")

    @task
    def load_booking_api() -> str:
        url = os.getenv("BOOKING_API_URL", "http://api:5000/booking-events")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        validate_booking_events(df)
        dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return write_parquet_to_s3(df, f"bronze/booking_operations/booking_events/dt={dt}/events.parquet")

    @task
    def publish_lineage(bookings_uri: str, events_uri: str) -> str:
        lineage = {
            "job": "booking_operations_raw_ingestion",
            "domain": "booking_operations",
            "inputs": ["data/samples/bookings.csv", "Booking API /booking-events"],
            "outputs": [bookings_uri, events_uri],
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
        key = f"lineage/booking_operations/{lineage['captured_at']}.json"
        s3_client().put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(lineage, ensure_ascii=False, indent=2).encode("utf-8"),
        )
        return f"s3://{S3_BUCKET}/{key}"

    publish_lineage(load_booking_csv(), load_booking_api())


booking_operations_raw_ingestion()
