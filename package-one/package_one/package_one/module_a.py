"""Module A Spark Library"""
import logging
from typing import Any, Dict

from eviltransform import gcj2wgs
from pyspark.sql import DataFrame
from pyspark.sql import functions as fn
from pyspark.sql.types import DoubleType, StructField, StructType


def basic_spark_function(data: DataFrame) -> DataFrame:
    """Simple Spark function that adds a columns and performs a filter."""
    return data.select(
        "*",
        (fn.col("index") * 2).alias("index2"),
    ).filter(fn.col("is_good"))


@fn.udf(
    returnType=StructType(
        [StructField("lat", DoubleType(), True), StructField("lng", DoubleType(), True)]
    )
)
def udf_function(lat: float, lng: float) -> Dict[str, Any]:
    """Simple UDF for converting between coordinate systems."""
    try:
        lat_wgs, lng_wgs = gcj2wgs(lat, lng)
    except Exception as err:  # pylint: disable=broad-except
        lat_wgs, lng_wgs = None, None
        logging.warning("Unable to convert. Error: %s", err)
    return {"lat": lat_wgs, "lng": lng_wgs}


def udf_spark_function(data: DataFrame) -> DataFrame:
    """Simple Spark UDF"""
    return data.select("*", fn.expr("A_UDF_FCN()").alias("new_column"))
