python_requirements(
    name = "reqs-pytest",
    resolve = "pytest",
    source = "requirements-pytest.txt",
)

python_requirements(
    name = "reqs-spark",
    overrides = {
        "pyspark": {
            "dependencies": [
                ":reqs-spark#pyarrow",
            ],
        },
    },
    resolve = "spark",
    source = "requirements-spark.txt",
)

python_requirements(
    name = "reqs",
    resolve = "default",
)
