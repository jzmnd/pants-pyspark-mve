resource(
    name = "pyproject",
    source = "pyproject.toml",
)

python_distribution(
    name = "package-one",
    dependencies = [
        ":pyproject",
        "package-one/package_one/package_one",
    ],
    provides = python_artifact(
        name = "package-one",
        description = "An example PySpark package.",
    ),
)
