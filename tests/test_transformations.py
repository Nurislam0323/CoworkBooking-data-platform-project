import pandas as pd

from lakehouse.spark.lib.transformations import build_client_features


def test_build_client_features_aggregates_bookings():
    bookings = pd.DataFrame([
        {"client_id": "C001", "booking_id": "B1", "status": "COMPLETED", "total_price": 1000},
        {"client_id": "C001", "booking_id": "B2", "status": "CANCELLED", "total_price": 500},
        {"client_id": "C002", "booking_id": "B3", "status": "COMPLETED", "total_price": 2400},
    ])
    clients = pd.DataFrame([
        {"client_id": "C001", "segment": "freelancer", "city": "Moscow"},
        {"client_id": "C002", "segment": "startup", "city": "Moscow"},
    ])

    result = build_client_features(bookings, clients)

    c001 = result[result.client_id == "C001"].iloc[0]
    assert c001.avg_booking_value_30d == 750.0
    assert c001.bookings_30d == 2
    assert c001.cancelled_booking_rate_30d == 0.5
