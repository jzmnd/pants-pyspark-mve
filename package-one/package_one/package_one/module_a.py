"""Module A Spark Library"""
import logging
from typing import Any, Dict

import pandas as pd
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
def basic_udf(lat: float, lng: float) -> Dict[str, Any]:
    """Simple UDF for converting between coordinate systems."""
    try:
        lat_wgs, lng_wgs = gcj2wgs(lat, lng)
    except Exception as err:  # pylint: disable=broad-except
        lat_wgs, lng_wgs = None, None
        logging.warning("Unable to convert. Error: %s", err)
    return {"lat": lat_wgs, "lng": lng_wgs}


def spark_sql_udf(data: DataFrame) -> DataFrame:
    """Simple Spark SQL UDF."""
    return data.select("*", fn.expr("A_UDF_FCN()").alias("new_column"))


def pandas_grouped_map_udf(data: pd.DataFrame) -> pd.DataFrame:
    """Simple grouped map Pandas UDF to subtract mean from a group."""
    return data.assign(value=data.value - data.value.mean())
