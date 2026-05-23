from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String

client = Entity(name="client", join_keys=["client_id"], description="CoworkBooking client")

client_features_source = FileSource(
    name="client_features_source",
    path="../../data/feature_store/client_features.parquet",
    timestamp_field="event_timestamp",
)

client_booking_features = FeatureView(
    name="client_booking_features",
    entities=[client],
    ttl=timedelta(days=7),
    schema=[
        Field(name="segment", dtype=String),
        Field(name="city", dtype=String),
        Field(name="avg_booking_value_30d", dtype=Float32),
        Field(name="bookings_30d", dtype=Int64),
        Field(name="cancelled_booking_rate_30d", dtype=Float32),
        Field(name="total_revenue_30d", dtype=Float32),
    ],
    online=True,
    source=client_features_source,
)
