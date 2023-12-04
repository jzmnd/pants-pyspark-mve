from eviltransform import gcj2wgs
from pyspark.sql import Column, DataFrame, functions as fn
from pyspark.sql.types import DoubleType, StructField, StructType


def basic_spark_function(df: DataFrame) -> DataFrame:
    return df.select(
        "*",
        (fn.col("index") * 2).alias("index2"),
    ).filter(
        fn.col("is_good")
    )


@fn.udf(
    returnType=StructType(
        [StructField("lat", DoubleType(), True), StructField("lng", DoubleType(), True)]
    )
)
def udf_spark_function(lat: Column, lng: Column) -> Column:
    try:
        lat_wgs, lng_wgs = gcj2wgs(lat, lng)
    except:
        lat_wgs, lng_wgs = None
    return {"lat": lat_wgs, "lng": lng_wgs}
