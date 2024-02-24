"""Pyspark test setup"""
import logging
import os
import sys
import unittest

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType


class TestPySpark(unittest.TestCase):
    """Pyspark unit test class"""

    spark: SparkSession

    @classmethod
    def setup_logging(cls) -> None:
        """Set up Spark logging."""
        logging.getLogger("py4j").setLevel(logging.WARN)

    @classmethod
    def register_mock_spark_udfs(cls) -> None:
        """Register mocks for UDFs."""
        cls.spark.udf.register("A_UDF_FCN", cls.a_udf_fcn, StringType())

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test case for Spark."""
        cls.setup_logging()
        os.environ["PYSPARK_PYTHON"] = sys.executable
        os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

        conf = SparkConf()
        conf.setMaster("local").setAppName("unit-tests")
        conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

        cls.spark = SparkSession.builder.config(conf=conf).getOrCreate()
        logging.info("Using session %s", cls.spark.sparkContext.applicationId)

        cls.register_mock_spark_udfs()

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up Spark."""
        cls.spark.stop()

    @staticmethod
    def a_udf_fcn() -> str:
        """Mock for `A_UDF_FCN`."""
        return "mock_return_message"
