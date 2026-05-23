import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp


def spark():
    return (
        SparkSession.builder.appName("bronze-to-silver-booking-operations")
        .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.lakehouse.type", "hadoop")
        .config("spark.sql.catalog.lakehouse.warehouse", os.getenv("WAREHOUSE", "s3a://coworkbooking-lakehouse"))
        .getOrCreate()
    )


if __name__ == "__main__":
    s = spark()
    s.sql("CREATE NAMESPACE IF NOT EXISTS lakehouse.silver")
    bronze_path = os.getenv("BRONZE_BOOKINGS_PATH", "s3a://coworkbooking-lakehouse/bronze/booking_operations/bookings")
    bookings = s.read.parquet(bronze_path)
    cleaned = (
        bookings.dropDuplicates(["booking_id"])
        .where((col("total_price") >= 0) & (col("hours") > 0))
        .withColumn("created_at", to_timestamp("created_at"))
        .withColumn("start_ts", to_timestamp("start_ts"))
        .withColumn("end_ts", to_timestamp("end_ts"))
    )
    cleaned.writeTo("lakehouse.silver.bookings").using("iceberg").createOrReplace()
