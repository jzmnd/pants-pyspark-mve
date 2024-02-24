"""Tests for Module A"""
from package_one.module_a import basic_spark_function, udf_function, udf_spark_function
from package_one.tests._pyspark import TestPySpark
from pyspark.sql import functions as fn


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

    def test_udf_function(self) -> None:
        """Test UDF."""
        test = self.spark.createDataFrame(
            [(39.916668, 116.383331)],
            ["lat", "lng"],
        )
        expected = self.spark.createDataFrame(
            [(39.91527139086107, 116.37709430717217)],
            ["lat", "lng"],
        )
        wgs_coords = udf_function(fn.col("lat"), fn.col("lng"))
        output = test.select(wgs_coords["lat"], wgs_coords["lng"])
        self.assertCountEqual(expected.collect(), output.collect())

    def test_udf_spark_function(self) -> None:
        """Test Spark UDF."""
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
        output = udf_spark_function(test)
        self.assertCountEqual(expected.collect(), output.collect())
