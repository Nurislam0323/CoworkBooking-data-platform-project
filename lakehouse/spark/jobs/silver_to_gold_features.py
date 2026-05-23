import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, countDistinct, round as spark_round, sum as spark_sum


def spark():
    return (
        SparkSession.builder.appName("silver-to-gold-client-features")
        .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.lakehouse.type", "hadoop")
        .config("spark.sql.catalog.lakehouse.warehouse", os.getenv("WAREHOUSE", "s3a://coworkbooking-lakehouse"))
        .getOrCreate()
    )


if __name__ == "__main__":
    s = spark()
    s.sql("CREATE NAMESPACE IF NOT EXISTS lakehouse.gold")
    clients = s.read.option("header", True).csv(os.getenv("CLIENTS_PATH", "s3a://coworkbooking-lakehouse/reference/clients.csv"))
    bookings = s.table("lakehouse.silver.bookings")
    features = (
        bookings.groupBy("client_id")
        .agg(
            spark_round(avg("total_price"), 2).alias("avg_booking_value_30d"),
            countDistinct("booking_id").alias("bookings_30d"),
            spark_round(avg((bookings.status == "CANCELLED").cast("double")), 3).alias("cancelled_booking_rate_30d"),
            spark_round(spark_sum("total_price"), 2).alias("total_revenue_30d"),
        )
        .join(clients, "client_id", "left")
    )
    features.writeTo("lakehouse.gold.client_features").using("iceberg").createOrReplace()
