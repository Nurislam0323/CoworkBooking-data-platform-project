import pandas as pd


def build_client_features(bookings: pd.DataFrame, clients: pd.DataFrame) -> pd.DataFrame:
    bookings = bookings.copy()
    bookings["is_cancelled"] = bookings["status"].eq("CANCELLED").astype(int)

    agg = (
        bookings.groupby("client_id", as_index=False)
        .agg(
            avg_booking_value_30d=("total_price", "mean"),
            bookings_30d=("booking_id", "nunique"),
            cancelled_booking_rate_30d=("is_cancelled", "mean"),
            total_revenue_30d=("total_price", "sum"),
        )
    )

    features = clients.merge(agg, on="client_id", how="left")
    features["avg_booking_value_30d"] = features["avg_booking_value_30d"].fillna(0).round(2)
    features["bookings_30d"] = features["bookings_30d"].fillna(0).astype(int)
    features["cancelled_booking_rate_30d"] = features["cancelled_booking_rate_30d"].fillna(0).round(3)
    features["total_revenue_30d"] = features["total_revenue_30d"].fillna(0).round(2)
    return features
