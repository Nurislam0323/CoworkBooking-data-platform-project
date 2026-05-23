import pandas as pd


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
        raise ValueError("; ".join(errors))


if __name__ == "__main__":
    df = pd.read_csv("data/samples/bookings.csv")
    validate_bookings(df)
    print("Data quality checks passed")
