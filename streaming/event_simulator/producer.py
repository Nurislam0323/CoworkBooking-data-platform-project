import json
import os
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

from confluent_kafka import Producer
from faker import Faker

fake = Faker()
producer = Producer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")})
topic = os.getenv("KAFKA_TOPIC", "coworkbooking.workplace_events")

workplaces = ["W-101", "MR-201", "W-301", "TEAM-1"]
spaces = {"W-101": "SP-01", "MR-201": "SP-01", "W-301": "SP-02", "TEAM-1": "SP-02"}
zones = {"W-101": "Open Space", "MR-201": "Meeting Zone", "W-301": "Quiet Zone", "TEAM-1": "Team Zone"}
event_types = ["check_in", "check_out", "booking_created"]

while True:
    workplace_id = random.choice(workplaces)
    event = {
        "event_id": str(uuid4()),
        "client_id": f"C{random.randint(1, 999):03d}",
        "event_type": random.choice(event_types),
        "space_id": spaces[workplace_id],
        "workplace_id": workplace_id,
        "zone": zones[workplace_id],
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "metadata": {"device_id": fake.uuid4()},
    }
    producer.produce(topic, key=event["client_id"], value=json.dumps(event).encode("utf-8"))
    producer.poll(0)
    print(event, flush=True)
    time.sleep(float(os.getenv("EVENT_INTERVAL_SECONDS", "1")))
