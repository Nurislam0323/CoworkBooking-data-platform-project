from datetime import datetime, timedelta, timezone
from feast import FeatureStore

if __name__ == "__main__":
    store = FeatureStore(repo_path=".")
    store.apply([])
    end = datetime.now(timezone.utc)
    store.materialize(start_date=end - timedelta(days=7), end_date=end)
