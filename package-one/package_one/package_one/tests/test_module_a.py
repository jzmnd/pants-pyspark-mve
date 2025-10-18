"""Tests for Module A"""

from package_one.module_a import (
    basic_spark_function,
    basic_udf,
    pandas_grouped_map_udf,
    spark_sql_udf,
)
from package_one.tests._pyspark import TestPySpark
from pyspark.sql import functions as fn
from pyspark.sql.types import DoubleType, LongType, StructField, StructType


class TestModuleA(TestPySpark):
    """Test cases for Module A"""

    def test_simple_assert(self) -> None:
        """Test simple assert."""
        self.assertEqual(1, 1)

    def test_basic_spark_function(self) -> None:
        """Test basic Spark function."""
        test = self.spark.createDataFrame(
            [(1, "apple", True), (2, "orange", False)],
            ["index", "fruit", "is_good"],
        )
        expected = self.spark.createDataFrame(
            [(1, "apple", True, 2)],
            ["index", "fruit", "is_good", "index2"],
        )
        output = basic_spark_function(test)
        self.assertCountEqual(expected.collect(), output.collect())

    def test_basic_udf(self) -> None:
        """Test UDF."""
        test = self.spark.createDataFrame(
            [(39.916668, 116.383331)],
            ["lat", "lng"],
        )
        expected = self.spark.createDataFrame(
            [(39.91527139086107, 116.37709430717217)],
            ["lat", "lng"],
        )
        wgs_coords = basic_udf(fn.col("lat"), fn.col("lng"))
        output = test.select(wgs_coords["lat"], wgs_coords["lng"])
        self.assertCountEqual(expected.collect(), output.collect())

    def test_spark_sql_udf(self) -> None:
        """Test Spark SQL UDF."""
        test = self.spark.createDataFrame(
            [(1, "apple", True), (2, "orange", False)],
            ["index", "fruit", "is_good"],
        )
        expected = self.spark.createDataFrame(
            [
                (1, "apple", True, "mock_return_message"),
                (2, "orange", False, "mock_return_message"),
            ],
            ["index", "fruit", "is_good", "new_column"],
        )
        output = spark_sql_udf(test)
        self.assertCountEqual(expected.collect(), output.collect())

    def test_pandas_grouped_map_udf(self) -> None:
        """Test grouped map Pandas UDF."""
        test = self.spark.createDataFrame(
            [(1, 1.0), (1, 2.0), (2, 3.0), (2, 5.0), (2, 10.0)],
            ("id", "value"),
        )
        expected = self.spark.createDataFrame(
            [(1, -0.5), (1, 0.5), (2, -3.0), (2, -1.0), (2, 4.0)],
            ("id", "value"),
        )
        schema = StructType(
            [StructField("id", LongType(), False), StructField("value", DoubleType(), True)]
        )
        output = test.groupby("id").applyInPandas(pandas_grouped_map_udf, schema)
        self.assertCountEqual(expected.collect(), output.collect())
