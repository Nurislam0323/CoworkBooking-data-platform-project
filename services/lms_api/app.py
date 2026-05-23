from datetime import datetime, timezone
from fastapi import FastAPI

app = FastAPI(title="CoworkBooking API")


@app.get("/booking-events")
def booking_events():
    now = datetime.now(timezone.utc).isoformat()
    return [
        {"event_id": "E2001", "booking_id": "B001", "client_id": "C001", "space_id": "SP-01", "event_type": "booking_confirmed", "event_ts": now, "amount": 1350},
        {"event_id": "E2002", "booking_id": "B002", "client_id": "C002", "space_id": "SP-01", "event_type": "booking_confirmed", "event_ts": now, "amount": 2400},
        {"event_id": "E2003", "booking_id": "B003", "client_id": "C003", "space_id": "SP-02", "event_type": "booking_cancelled", "event_ts": now, "amount": 700},
    ]
